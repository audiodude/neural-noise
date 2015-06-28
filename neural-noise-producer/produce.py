import base64
import os
import re
import subprocess
import tempfile
import time

import pymongo

CHAR_RNN_DIR = '/home/music/char-rnn'
CP_FILE = 'lm_lstm_epoch18.85_0.3871.t7'
DATA_LENGTH = 8192

MONGO_URL = 'mongodb://localhost:27017/neural-noise'
client = pymongo.MongoClient(MONGO_URL)
db = client.get_default_database()

RE_REPEAT = re.compile('\|:(.*?):\|')

def get_generated_data(temperature):
  cmdline = ('th sample.lua cv/%(file)s -primetext "X:1" -length %(length)s '
             '-temperature %(temp)s -gpuid -1 -verbose 0 -seed %(seed)s' % {
               'file': CP_FILE,
               'length': DATA_LENGTH,
               'temp': temperature,
               'seed': int(time.time())
             })
  pipe = subprocess.Popen(
    cmdline, executable='/bin/bash', shell=True, cwd=CHAR_RNN_DIR,
    stdout=subprocess.PIPE)

  data, _ = pipe.communicate()
  return data

section_count = 0
def get_songs(temperature):
  global section_count
  data = get_generated_data(temperature)
  songs = data.split('X:1\n')
  for song in songs:
    if not song:
      continue

    section_count = 0
    def process_section(md):
      global section_count
      if md.group(1):
        section_count += 1
      return md.group(1)
    song = RE_REPEAT.sub(process_section, song)
    if section_count < 2:
      continue
    song = 'X:1\n' + song
    yield song

def get_midi_path(song):
  with tempfile.NamedTemporaryFile() as f:
    f.write(song)
    f.flush()
    dest_path = os.path.join('/tmp', os.path.basename(f.name) + '.mid')
    args = ['/home/music/abcmidi/abc2midi', f.name, '-o', dest_path, '-silent']
    print ' '.join(args)
    subprocess.call(args)
    return dest_path

def insert_songs(temperature):
  count = 0
  for song in get_songs(temperature):
    count += 1
    midi_path = get_midi_path(song)

    with open(midi_path) as f:
      midi_bin = f.read()
    midi = base64.b64encode(midi_bin)

    db.songs.insert({
      'abc': song,
      'midi': midi,
    })
  return count

if __name__ == '__main__':
  temperature = '0.85'
  num = insert_songs(temperature)
  print '%s songs inserted, temperature=%s' % (num, temperature)
