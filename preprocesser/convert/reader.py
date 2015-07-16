from decimal import Decimal
from fractions import Fraction

from lxml import etree

import exceptions

NOTES = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

def get_octave_appendix(octave):
  o = int(octave)
  if o == 0:
    return ''
  elif o > 0:
    return "'" * o
  else:  # o < 0
    return "," * (o * -1)

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

class XMLReader(object):

  def __init__(self, xml_path, **options):
    self.root = etree.parse(xml_path)
    self.include_artist_title = options.get('include_artist_title', True)

  def is_ready(self):
    if not self.root:
      raise exceptions.ConverterNotReadyException(
        'The set_xml_root method has not been called or was called with None.')

  def get_metadata(self):
    self.is_ready()
    metadata = {}
    if self.include_artist_title:
      artist = self.root.xpath('//artist/text()')
      if artist:
        metadata['C'] = artist[0]

      title = self.root.xpath('//title/text()')
      if title:
        metadata['T'] = title[0]

    meter = self.root.xpath('//beats_in_measure/text()')
    if meter:
      meter = meter[0]
      if meter != '4':
        raise exceptions.UnrecognizedMeterException(meter)
      metadata['M'] = 'C'

    bpm = self.root.xpath('//BPM/text()')
    if bpm:
      metadata['Q'] = '1/4=%s' % bpm[0]

    key = self.root.xpath('//key/text()')
    if key:
      metadata['K'] = key[0]

    metadata['V'] = []
    notes = self.root.xpath('//note')
    if notes:
      metadata['V'].append('notes')

    chords = self.root.xpath('//chord')
    if chords:
      metadata['V'].append('chords')
    return metadata

  def get_notes(self):
    self.is_ready()
    notes = []
    note_xmls = self.root.xpath('//note')
    for note_xml in note_xmls:
      degree = note_xml.find('scale_degree').text
      if not degree:
        raise exceptions.EmptyNoteException(degree)
      if degree == 'rest':
        note = 'x'
      else:
        accidental = ''
        if degree.endswith('f'):
          accidental = '_'
          degree = int(degree[:-1])
        elif degree.endswith('s'):
          accidental = '^'
          degree = int(degree[:-1])
        else:
          degree = int(degree)

        note = accidental + NOTES[degree - 1]

      octave = note_xml.find('octave').text
      octave_append = get_octave_appendix(octave)
      note += octave_append

      length = note_xml.find('note_length').text
      length_append = get_length_appendix(length)
      note += length_append
      notes.append(note)
    return notes

  def get_chords(self):
    self.is_ready()
    chords = []
    chord_xmls = self.root.xpath('//chord')
    for chord_xml in chord_xmls:
      degree = chord_xml.find('sd').text
      if degree == 'rest':
        notes = ('x',)
      else:
        try:
          degree = int(degree)
        except ValueError:
          # The chord is 'flat' or 'sharp'. Not sure how to interpret this
          # musically, so just fail the whole song.
          raise exceptions.UnrecognizedChordException(degree)
        notes = (NOTES[degree - 1] + ',',
                 NOTES[(degree + 2) % 7 - 1] + ',',
                 NOTES[(degree + 4) % 7 - 1] + ',')

      duration = chord_xml.find('chord_duration').text
      length_append = get_length_appendix(duration)
      chord = [note + length_append for note in notes]
      chords.append(chord)
    return chords
