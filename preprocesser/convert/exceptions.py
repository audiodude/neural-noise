class ConversionException(Exception):
  pass

class MissingNotesException(ConversionException):
  pass

class EmptyNoteException(ConversionException):
  pass

class MissingChordsException(ConversionException):
  pass

class UnrecognizedMeterException(ConversionException):
  pass

class UnrecognizedChordException(ConversionException):
  pass
