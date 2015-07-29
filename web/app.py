import decimal
import os
import random
import urlparse

import bson
import flask
import markdown
import pymongo


MONGO_URL = 'mongodb://localhost:27017/neural-noise'
client = pymongo.MongoClient(MONGO_URL)
db = client.get_default_database()

app = flask.Flask(__name__)

def is_debug():
  return os.environ.get('FLASK_ENV') != 'production'

def random_song(checkpoint, temperature):
  # Taken from http://stackoverflow.com/a/21867984/41060
  query = {
    'checkpoint': { '$eq': checkpoint },
    'random': { '$lte': random.random() },
  }
  if temperature:
    query['temperature'] = { '$eq': temperature }

  cursor = db.songs.find(query).sort('random', pymongo.DESCENDING)
  try:
    doc = next(cursor)
  except StopIteration:
    del query['random']
    cursor = db.songs.find(query).sort('random', pymongo.DESCENDING);
    try:
      doc = next(cursor)
    except StopIteration:
      return None

  doc['random'] = random.random();
  db.songs.update({ '_id': doc['_id'] }, doc);
  return doc

@app.route('/')
def index():
  checkpoints = [cp['name'] for cp in db.checkpoints.find({})]
  checkpoints.append('Test')
  return flask.render_template('index.html', checkpoints=checkpoints)

@app.route('/query')
def query():
  temperature = flask.request.args.get('temperature')
  checkpoint = flask.request.args.get('checkpoint')
  song = random_song(checkpoint, temperature)
  if not song:
    return 'Error: no songs at checkpoint=%s with temperature=%s found' % (checkpoint, temperature)
  return flask.redirect(flask.url_for(
    'render', checkpoint=checkpoint, id_=str(song['_id'])))

@app.route('/render/<checkpoint>/<id_>')
def render(checkpoint, id_):
  song = db.songs.find_one({
    '_id': { '$eq': bson.objectid.ObjectId(id_) }
  })

  return flask.render_template('render.html', song=song)

@app.route('/2png/<id_>.png')
def png(id_):
  parts = urlparse.urlparse(flask.request.url)
  new_host = flask.request.headers['Host']
  if new_host.find(':') != -1:
    new_host = new_host[:new_host.find(':')]  # Strip out port
  new_path = parts.path.replace('2png', 'png')
  # Replace the /2png/ with just /png/.
  new_parts = [parts.scheme, new_host, new_path, '', '']
  new_url = urlparse.urlunsplit(new_parts)
  return flask.redirect(new_url)

@app.route('/about')
def about():
  md_path = os.path.join(os.path.dirname(__file__), 'templates/_about.md')
  with open(md_path) as f:
    content = flask.Markup(markdown.markdown(f.read()))
  return flask.render_template('about.html', content=content)

if __name__ == '__main__':
  app.run(debug=is_debug(), host='0.0.0.0')
