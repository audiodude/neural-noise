import decimal
import os

import bson
import flask
import pymongo


MONGO_URL = 'mongodb://localhost:27017/neural-noise'
client = pymongo.MongoClient(MONGO_URL)
db = client.get_default_database()

app = flask.Flask(__name__)

def is_debug():
  return os.environ.get('FLASK_ENV') != 'production'

@app.route('/')
def index():
  return flask.render_template('index.html')

@app.route('/query')
def query():
  temperature = flask.request.args['temperature']
  song = db.songs.find_one({
    'temperature': { '$eq': temperature }
  })
  return flask.redirect(flask.url_for('render', x=str(song['_id'])))

@app.route('/render')
def render():
  id_ = flask.request.args['x']
  song = db.songs.find_one({
    '_id': { '$eq': bson.objectid.ObjectId(id_) }
  })
  print song['midi']
  return flask.render_template('render.html', song=song)

if __name__ == '__main__':
  app.run(debug=is_debug(), host='0.0.0.0')
