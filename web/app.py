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

def random_song(checkpoint, temperature):
  # Taken from http://stackoverflow.com/a/21867984/41060
  query = {
    'checkpoint': { '$eq': checkpoint },
    'temperature': { '$eq': temperature },
    'random': { '$lte': random.random() },
  }
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
  return flask.render_template('index.html', checkpoints=checkpoints)

@app.route('/query')
def query():
  temperature = flask.request.args['temperature']
  checkpoint = flask.request.args['checkpoint']
  print 'Checkpoint %s temperature %s' % (checkpoint, temperature)
  song = random_song(checkpoint, temperature)
  if not song:
    return 'Error: no songs at checkpoint=%swith temperature=%s found' % (checkpoint, temperature)
  return flask.redirect(flask.url_for(
    'render', checkpoint=checkpoint, id_=str(song['_id'])))

@app.route('/render/<checkpoint>/<id_>')
def render(checkpoint, id_):
  song = db.songs.find_one({
    '_id': { '$eq': bson.objectid.ObjectId(id_) }
  })

  return flask.render_template('render.html', song=song)

if __name__ == '__main__':
  app.run(debug=is_debug(), host='0.0.0.0')
