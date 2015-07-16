import os
import sys

from convert import exceptions
from convert import xml_to_abc
from convert import util


def main():
  if len(sys.argv) != 2:
    print 'usage: converter.py xml-file-or-dir'
    sys.exit(1)

  options = {
    # Whether the ABC should be surrounded with repeats to help indicate start
    # amd end of the music
    'use_repeat': False,
    # Whether the artist and title information should be included in the
    # generated metadata
    'include_artist_title': False
  }

  file_or_dir = sys.argv[1]

  if os.path.isfile(file_or_dir):
    print xml_to_abc(file_or_dir, **options)
  else:
    util.mkdir_p('xml/abc')
    for dirpath, dirnames, filenames in os.walk(file_or_dir):
      for filename in filenames:
        full_path = os.path.join(dirpath, filename)
        try:
          data = xml_to_abc(full_path, **options)
        except exceptions.ConversionException:
          # Filter out songs that are missing notes, chords, have
          # unrecognized meter, etc. We might some day accommodate these.
          continue
        except:
          # If there is an unexpected exception, write the file name before
          # we crash so that it can potentially be debugged.
          sys.stderr.write(filename + '\n')
          raise

        with open(os.path.join('xml/abc/', filename) + '.abc', 'w') as f:
          f.write(data + '\n')

if __name__ == '__main__':
  main()
