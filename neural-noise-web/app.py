import os

import flask

app = flask.Flask(__name__)

def is_debug():
  return os.environ.get('FLASK_ENV') != 'production'

@app.route('/')
def index():
  return flask.render_template('index.html')

@app.route('/query')
def render():
  temp = flask.request.args['temperature']
  return'Query temperature = %s' % temp

if __name__ == '__main__':
  app.run(debug=is_debug(), host='0.0.0.0')
