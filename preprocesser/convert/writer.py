import exceptions

METADATA_ORDER = ['X', 'T', 'C', 'M', 'Q', 'V', 'K']
MIN_NOTES = 8
MIN_CHORDS = 4


def format_chord(chord):
  if len(chord) > 1:
    return '[%s]' % ''.join(chord)
  else:
    return chord[0]


class ABCWriter(object):

  def __init__(self, out, **options):
    self.out = out
    self.use_repeat = options.get('use_repeat', False)

  def is_ready(self):
    if not self.out:
      raise exceptions.ConverterNotReadyException(
        'The set_output method has not been called or was called with None.')

  def write_metadata(self, metadata):
    self.is_ready()
    for key in METADATA_ORDER:
      if key in metadata:
        value = metadata[key]
        if key == 'K':
          value = 'C'  # Pretend like all songs are in C for simplification.
        if not isinstance(value, list):
          value = [value]
        for v in value:
          self.out.write('%s:%s\n' % (key, v))

  def write_notes(self, notes):
    self.is_ready()
    if not notes or len(notes) < MIN_NOTES:
      raise exceptions.MissingNotesException()

    self.out.write('[V:notes] ')
    if self.use_repeat:
      self.out.write('|:')
    self.out.write(' '.join(notes))
    if self.use_repeat:
      self.out.write(':|')
    self.out.write('\n')

  def write_chords(self, chords):
    self.is_ready()
    if not chords or len(chords) < MIN_CHORDS:
      raise exceptions.MissingChordsException()

    self.out.write('[V:chords]')
    if self.use_repeat:
      self.out.write(' |:')
    if len(chords) > 1:
      self.out.write(' '.join(format_chord(chord) for chord in chords))
    if self.use_repeat:
      self.out.write(':|')

  def getvalue(self):
    return self.out.getvalue()
