from decimal import Decimal
from fractions import Fraction
import os
import cStringIO

from lxml import etree

METADATA_ORDER = ['X', 'T', 'C', 'M', 'Q', 'V', 'K']
NOTES = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

class ConversionException(object):
  pass

class UnrecognizedMeterException(object):
  pass

def write_metadata(out, metadata):
  for key in METADATA_ORDER:
    if key in metadata:
      value = metadata[key]
      if key == 'K':
        value = 'C'  # Pretend like all songs are in C for simplification.
      if not isinstance(value, list):
        value = [value]
      for v in value:
        out.write('%s:%s\n' % (key, v))

def get_metadata(root):
  metadata = {}
  artist = root.xpath('//artist/text()')
  if artist:
    metadata['C'] = artist[0]

  title = root.xpath('//title/text()')
  if title:
    metadata['T'] = title[0]

  meter = root.xpath('//beats_in_measure/text()')
  if meter:
    meter = meter[0]
    if meter != '4':
      raise UnrecognizedMeterException(meter)
    metadata['M'] = 'C'

  bpm = root.xpath('//BPM/text()')
  if bpm:
    metadata['Q'] = '1/4=%s' % bpm[0]

  key = root.xpath('//key/text()')
  if key:
    metadata['K'] = key[0]

  metadata['V'] = []
  notes = root.xpath('//note')
  if notes:
    metadata['V'].append('notes')

  chords = root.xpath('//chord')
  if chords:
    metadata['V'].append('chords')

  return metadata

def get_length_appendix(length, base=Decimal('0.5')):
  l = Decimal(length)
  result = l/base

  if result == 1:
    return ''
  elif result < 1:
    f = Fraction(result)
    if f.numerator == '1':
      return '/%s' % f.denominator
    else:
      return '%s/%s' % (f.numerator, f.denominator)
  else:
    return str(int(result))

def get_octave_appendix(octave):
  o = int(octave)
  if o == 0:
    return ''
  elif o > 0:
    return "'" * o
  else:  # o < 0
    return "," * (o * -1)

def get_notes(root):
  notes = []
  note_xmls = root.xpath('//note')
  for note_xml in note_xmls:
    degree = note_xml.find('scale_degree').text
    if degree == 'rest':
      note = 'x'
    else:
      note = NOTES[int(degree) - 1]

    octave = note_xml.find('octave').text
    octave_append = get_octave_appendix(octave)
    note += octave_append

    length = note_xml.find('note_length').text
    length_append = get_length_appendix(length)
    note += length_append
    notes.append(note)
  return notes

def write_notes(out, notes, use_repeat=False):
  out.write('[V:notes] ')
  if use_repeat:
    out.write('|:')
  out.write(' '.join(notes))
  if use_repeat:
    out.write(':|')
  out.write('\n')

def get_chords(root):
  chords = []
  chord_xmls = root.xpath('//chord')
  for chord_xml in chord_xmls:
    degree = int(chord_xml.find('sd').text)
    notes = (NOTES[degree - 1] + ',',
             NOTES[(degree + 2) % 7 - 1] + ',',
             NOTES[(degree + 4) % 7 - 1] + ',')

    duration = chord_xml.find('chord_duration').text
    length_append = get_length_appendix(duration)
    chord = [note + length_append for note in notes]
    chords.append(chord)
  return chords

def write_chords(out, chords, use_repeat=False):
  out.write('[V:chords]')
  if use_repeat:
    out.write(' |:')
  out.write(' '.join('[%s]' % ''.join(chord) for chord in chords))
  if use_repeat:
    out.write(':|')

def abc_from_xml(xml_path, use_repeat=False):
  metadata = {}
  root = etree.parse(xml_path)

  metadata = get_metadata(root)
  metadata['X'] = os.path.basename(xml_path)

  notes = get_notes(root)
  chords = get_chords(root)

  out = cStringIO.StringIO()
  write_metadata(out, metadata)
  write_notes(out, notes, use_repeat)
  write_chords(out, chords, use_repeat)
  return out.getvalue()


if __name__ == '__main__':
  import sys
  import util

  if len(sys.argv) != 2:
    print 'usage: converter.py xml-file-or-dir'
    sys.exit(1)

  file_or_dir = sys.argv[1]

  if os.path.isfile(file_or_dir):
    print abc_from_xml(file_or_dir, use_repeat=False)
  else:
    util.mkdir_p('xml/abc')
    for dirpath, dirnames, filenames in os.walk(file_or_dir):
      for filename in filenames:
        with open(os.path.join('xml/abc/', filename) + '.abc', 'w') as f:
          full_path = os.path.join(dirpath, filename)
          try:
            data = abc_from_xml(full_path, use_repeat=True)
          except:
            sys.stderr.write(filename + '\n')
            raise
          f.write(data + '\n')
