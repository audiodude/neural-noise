import base64
import os
import random
import re
import subprocess
import tempfile
import time

import pymongo

CHAR_RNN_DIR = '/home/music/char-rnn'
ABCM2PS_PATH = '/home/music/abcm2ps/abcm2ps'
ABC2MIDI_PATH = '/home/music/abcmidi/abc2midi'
PNG_OUTPUT_PATH = '/var/nn/png'

DATA_LENGTH = 8192

MONGO_URL = 'mongodb://localhost:27017/neural-noise'
client = pymongo.MongoClient(MONGO_URL)
db = client.get_default_database()

RE_REPEAT = re.compile('\|:(.*?):\|')
RE_TITLE = re.compile('T:(.*)')
RE_COMPOSER = re.compile('C:(.*)')

def get_generated_data(temperature, cp_path):
  cmdline = ('th sample.lua cv/%(file)s -primetext "X:1" -length %(length)s '
             '-temperature %(temp)s -gpuid -1 -verbose 0 -seed %(seed)s' % {
               'file': cp_path,
               'length': DATA_LENGTH,
               'temp': temperature,
               'seed': int(float(time.time()) * 1000)
             })
  pipe = subprocess.Popen(
    cmdline, executable='/bin/bash', shell=True, cwd=CHAR_RNN_DIR,
    stdout=subprocess.PIPE)

  data, _ = pipe.communicate()
  return data

section_count = 0
def get_generated_songs(temperature, cp_path):
  global section_count
  data = get_generated_data(temperature, cp_path)
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

def insert_song(song, checkpoint, fields=None):
  if not fields:
    fields = {}

  with tempfile.NamedTemporaryFile() as f:
    f.write(song)
    f.flush()

    with tempfile.NamedTemporaryFile() as m:
      args = [ABC2MIDI_PATH, f.name, '-silent', '-o', m.name]
      subprocess.call(args)
      m.seek(0)
      midi = m.read()

    data = {
      'random': random.random(),
      'created_at': int(time.time()),
      'checkpoint': checkpoint,
      'abc': song,
      'midi': base64.b64encode(midi),
    }
    data.update(fields)
    db.songs.insert(data)

    # Convert from abc to SVG, then to PNG
    png_path = os.path.join(PNG_OUTPUT_PATH, str(data['_id']) + '.png')
    with tempfile.NamedTemporaryFile() as s:
      args = [ABCM2PS_PATH, '-q', '-O', s.name, f.name]
      subprocess.call(args)
      args = ['convert', '-density', '100', '-trim', s.name, png_path]
      subprocess.call(args)

def insert_generated_songs(temperature, cp_path):
  count = 0
  for song in get_generated_songs(temperature, cp_path):
    count += 1
    insert_song(song, cp_path, fields={
      'temperature': temperature
    })
  return count

def fill_minimum(temperature, cp_path, min_):
  num = 0
  while num < min_:
    num += insert_generated_songs(temperature, cp_path)
  return num

def fill_all_temps(cp_path, min_):
  db.checkpoints.update({'name': {'$eq': cp_path}}, {'name': cp_path}, True)
  for i in range(50, 105, 5):
    temperature = str(i/100.0)
    num = fill_minimum(temperature, cp_path, min_)
    print '%s songs inserted, temperature=%s' % (num, temperature)    

# Utility method that is not called from the main process of producing songs.
def fill_from_disk(dir_path, checkpoint):
  count = 0
  for dirpath, dirnames, filenames in os.walk(dir_path):
    for filename in filenames:
      if filename.endswith('.abc'):
        full_path = os.path.join(dirpath, filename)
        with open(full_path) as f:
          song = f.read()

          fields = {
            'file': filename,
          }
          md = RE_TITLE.search(song)
          title = None
          if md:
            fields['title'] = md.group(1)
          md = RE_COMPOSER.search(song)
          composer = None
          if md:
            fields['composer'] = md.group(1)

          print 'Inserting song "%s":%s' % (fields.get('title'), fields['file'])
          insert_song(song, checkpoint, fields=fields)
          count += 1
  print '%s songs inserted, checkpoint=%s' % (count, checkpoint)

# Another utility method, for when songs have outlived their welcome
def purge_checkpoint(checkpoint):
  count = 0
  for song in db.songs.find({'checkpoint': {'$eq': checkpoint}}):
    db.songs.remove(song)
    count += 1

  db.checkpoints.remove({'name': checkpoint})
  print '%s songs removed, checkpoint %s purged' % (count, checkpoint)

if __name__ == '__main__':
  import sys
  min_ = 100
  if len(sys.argv) > 1:
    cp_path = sys.argv[1]
  if len(sys.argv) > 2:
    min_ = int(sys.argv[2])

  full_cp_path = os.path.join(CHAR_RNN_DIR, 'cv', cp_path)
  if not os.path.isfile(full_cp_path):
    print 'Path %s for checkpoint file could not be found'
    print 'usage: produce.py <path> [num per temp]'
    sys.exit(1)

  fill_all_temps(cp_path, min_)

