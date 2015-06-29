import base64
import os
import random
import re
import subprocess
import tempfile
import time

import pymongo

CHAR_RNN_DIR = '/home/music/char-rnn'
ABCM2PS_PATH = '/home/music/abcm2ps-7.8.14/abcm2ps'
ABC2MIDI_PATH = '/home/music/abcmidi/abc2midi'
PNG_OUTPUT_PATH = '/var/nn/png'

CP_FILE = 'lm_lstm_epoch21.83_0.3838.t7'
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

def insert_songs(temperature):
  count = 0
  for song in get_songs(temperature):
    count += 1

    with tempfile.NamedTemporaryFile() as f:
      f.write(song)
      f.flush()

      with tempfile.NamedTemporaryFile() as m:
        args = [ABC2MIDI_PATH, f.name, '-o', m.name,'-silent']
        subprocess.call(args)
        m.seek(0)
        midi = m.read()

      data = {
        'random': random.random(),
        'temperature': temperature,
        'abc': song,
        'midi': base64.b64encode(midi),
      }
      db.songs.insert(data)
      png_path = os.path.join(PNG_OUTPUT_PATH, str(data['_id']) + '.png')

      # Convert from abc to SVG, then to PNG
      with tempfile.NamedTemporaryFile() as s:
        args = [ABCM2PS_PATH, '-O', s.name, f.name]
        subprocess.call(args)
        args = ['convert', '-density', '100', '-trim', s.name, png_path]
        subprocess.call(args)

  return count

def fill_all_temps():
  for i in range(5, 105, 5):
    num = 0
    while num < 100:
      temperature = str(i/100.0)
      num = insert_songs(temperature)
      print '%s songs inserted, temperature=%s' % (num, temperature)

if __name__ == '__main__':
  temperature = '0.9'
  num = insert_songs(temperature)
  print '%s songs inserted, temperature=%s' % (num, temperature)


