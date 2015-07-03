import json
import time

from lxml import etree
import requests

EN_SONG_SEARCH_URL = 'http://developer.echonest.com/api/v4/song/search'

def found_song(xml_path, api_key):
  params = {
    'api_key': api_key,
    'format': 'json',
    'results': 1
  }
  try:
    root = etree.parse(xml_path)
  except:
    with open('error.txt', 'a') as f:
      f.write(os.path.basename(xml_path) + '\n')
    return

  artist = root.xpath('//artist/text()')
  title = root.xpath('//title/text()')
  if not (artist and title):
    # Skip anything that doesn't have an artist AND a title
    return False

  params['artist'] = artist
  params['title'] = title

  resp = requests.get(EN_SONG_SEARCH_URL, params=params)
  resp.raise_for_status()
  data = json.loads(resp.text)
  return bool(data['response']['status']['code'] == 0 and
              len(data['response']['songs']))

if __name__ == '__main__':
  import errno
  import os
  import sys
  import shutil
  import util

  util.mkdir_p('xml/existing')
  util.mkdir_p('xml/nonexistant')
  api_key = os.environ['ECHO_NEST_API_KEY']

  if len(sys.argv) != 2:
    # No argument given, do entire xml/raw directory
    for dirpath, dirnames, filenames in os.walk('xml/raw'):
      for filename in filenames:
        full_path = os.path.join(dirpath, filename)
        print full_path,

        exist_path = os.path.join('xml/existing', filename)
        if os.path.isfile(exist_path):
          print ' o'
          continue

        nonexist_path = os.path.join('xml/nonexistant', filename)
        if os.path.isfile(nonexist_path):
          print ' x'
          continue

        if found_song(full_path, api_key):
          print ' O'
          shutil.copyfile(full_path, exist_path)
        else:
          util.touch(nonexist_path)
          print ' X'
        time.sleep(0.5)
  else:
    if found_song(sys.argv[1], api_key):
      print os.path.join('xml/existing', os.path.basename(sys.argv[1]))
