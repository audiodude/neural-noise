import cStringIO

from reader import XMLReader
from writer import ABCWriter


def convert(reader, writer):
  metadata = {}
  metadata = reader.get_metadata()
  metadata['X'] = 1

  notes = reader.get_notes()
  chords = reader.get_chords()

  writer.write_metadata(metadata)
  writer.write_notes(notes)
  writer.write_chords(chords)
  return writer.getvalue()


def xml_to_abc(xml_path, **options):
  reader = XMLReader(xml_path, **options)
  out = cStringIO.StringIO()
  writer = ABCWriter(out, **options)
  return convert(reader, writer)
