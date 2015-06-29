import decimal
import os
import random

import bson
import flask
import pymongo


MONGO_URL = 'mongodb://localhost:27017/neural-noise'
client = pymongo.MongoClient(MONGO_URL)
db = client.get_default_database()

app = flask.Flask(__name__)

def is_debug():
  return os.environ.get('FLASK_ENV') != 'production'

def random_song(temperature):
  # Taken from http://stackoverflow.com/a/21867984/41060
  query = {
    'temperature': { '$eq': temperature },
    'random': { '$lte': random.random() },
  }
  cursor = db.songs.find(query).sort('random', pymongo.DESCENDING)
  try:
    doc = next(cursor)
  except StopIteration:
    cursor = db.songs.find().sort('random', pymongo.DESCENDING);
    try:
      doc = next(cursor)
    except StopIteration:
      return None

  doc['random'] = random.random();
  db.songs.update({ '_id': doc['_id'] }, doc);
  return doc

@app.route('/')
def index():
  return flask.render_template('index.html')

@app.route('/query')
def query():
  temperature = flask.request.args['temperature']
  song = random_song(temperature)
  if not song:
    return 'Error: no songs with temperature=%s found' % temperature
  return flask.redirect(flask.url_for('render', x=str(song['_id'])))

@app.route('/render')
def render():
  id_ = flask.request.args['x']
  song = db.songs.find_one({
    '_id': { '$eq': bson.objectid.ObjectId(id_) }
  })

  return flask.render_template('render.html', song=song)

if __name__ == '__main__':
  app.run(debug=is_debug(), host='0.0.0.0')
