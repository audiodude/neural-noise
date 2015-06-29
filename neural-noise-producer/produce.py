import base64
import os
import random
import re
import subprocess
import tempfile
import time

import pymongo

CHAR_RNN_DIR = '/home/music/char-rnn'
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

def get_midi_and_png(song):
  with tempfile.NamedTemporaryFile() as f:
    f.write(song)
    f.flush()

    with tempfile.NamedTemporaryFile() as m:
      args = ['/home/music/abcmidi/abc2midi', f.name, '-o', m.name,'-silent']
      subprocess.call(args)
      m.seek(0)
      yield m.read()

    # The conversion from abc to .tex is not currently working.
    # with tempfile.NamedTemporaryFile() as s:
    #   args = ['/home/music/abc2mtex1.6.1/abc2mtex', '-x', '-o', s.name, f.name]
    #   subprocess.call(args)
    #   with tempfile.NamedTemporaryFile() as p:
    #     args = ['gs', '-sDEVICE=pngalpha', '-o', p.name, '-r160', s.name]
    #     subprocess.call(args)
    #     p.seek(0)
    #     yield p.read()

def insert_songs(temperature):
  count = 0
  for song in get_songs(temperature):
    count += 1
    if count == 1:
      print song
    data = get_midi_and_png(song)

    midi = base64.b64encode(next(data))
    # png = base64.b64encode(next(data))

    db.songs.insert({
      'random': random.random(),
      'temperature': temperature,
      'abc': song,
      'midi': midi,
      # 'png': png,
    })
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


