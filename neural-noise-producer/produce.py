import subprocess
import time

import pymongo

CHAR_RNN_DIR='/home/music/char-rnn'
DATA_LENGTH=1024

MONGO_URL = 'mongodb://localhost:27017/neural-noise'
client = pymongo.MongoClient(MONGO_URL)
db = client.get_default_database()

def get_generated_data(temperature):
  cmdline = ('th sample.lua cv/lm_lstm_epoch0.99_0.5225.t7 -primetext "X:1" '
             '-length %(length)s -temperature %(temp)s -gpuid -1 -verbose 0 '
             '-seed %(seed)s' % {
               'length': DATA_LENGTH,
               'temp': temperature,
               'seed': int(time.time())
             })
  pipe = subprocess.Popen(
    cmdline, executable='/bin/bash', shell=True, cwd=CHAR_RNN_DIR,
    stdout=subprocess.PIPE)

  data, _ = pipe.communicate()
  return data

def main():
  data = get_generated_data('0.8')
  print data
  print '--------------------'
  songs = data.split('X:1\n')
  if songs[-1].find(':|') == -1:
    songs = songs[:-1]

  for song in songs:
    if not song:
      continue
    song = song.replace('|:', '').replace(':|', '')
    print song
    print '======'
    # db.songs.insert({
    #   'abc': song
    # })

if __name__ == '__main__':
  main()
