from flask import Flask, render_template, request, Response, redirect, url_for
from flask_socketio import SocketIO, emit
from crazyivan import CrazyIvan
import utils
import datetime
import logging
from functools import wraps
import time

utils.init_logger()
async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode, logger=False, engineio_logger=False)
thread = None
stopped = True
profit = 0

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'admin'


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'ACCESS DENIED. \n'
    'Go away!', 401,
    {'WWW-Authenticate': 'Basic realm="Login to Crazy Ivan"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/', defaults={'pair': 'btcusd'})
@app.route('/<pair>')
@requires_auth
def index(pair='btcusd'):
    global profit
    if pair not in ['btcusd', 'ltcusd', 'ethusd']:
        return Response('Crazy Ivan denied this currency. \n', 404)
    return render_template('index.html',
                           name='Crazy Ivan v0.8b',
                           stopped=int(stopped),
                           profit=profit,
                           pair=pair)


def log_event(name, data, pair_name="all"):
    logging.info("{name} - {data}".format(name=pair_name, data=data))
    global profit
    if name == "profit":
        profit = data
    socketio.emit('my_response',
                  {'pair': pair_name,
                   'data': data,
                   'name': name,
                   'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                  namespace='/test')


ivans = {'btcusd': None, 'ltcusd': None}  # 'ethusd': None,

for ivan in ivans:
    config_name = 'config-{pair}.json'.format(pair=ivan)
    config = utils.load_config(config_name)
    ivans[ivan] = CrazyIvan(log_event, config, ivan)


def background_thread():
    while True:
        try:
            global stopped
            if not stopped:
                is_new_minute = datetime.datetime.now().second < 2
                for i in ivans:
                    ivans[i].update(is_new_minute)
        except Exception as e:
            log_event("error", e)
        socketio.sleep(2)


@socketio.on('my_event', namespace='/test')
def test_message(message):
    emit('my_response',
         {'data': str(message)})


@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')


@socketio.on('connect', namespace='/test')
def test_connect():
    log_event('info', 'Connected to Crazy Ivan. Bot is <strong>{state}</strong>.'.format(state='Active' if not stopped else 'Inactive'))
    emit('stopped', stopped, namespace='/test')


@socketio.on('save_config', namespace='/test')
def save_settings(data):
    pair = data['pair']
    config = data['data']
    config_name = 'config-{pair}.json'.format(pair=pair)
    utils.save_config(config, file_name=config_name)
    ivans[pair].update_config(config)
    log_event('info', 'Setting {pair} saved.'.format(pair=pair))


@socketio.on('load_config_req', namespace='/test')
def load_settings(pair):
    config_name = 'config-{pair}.json'.format(pair=pair)
    config = utils.load_config(config_name)
    emit('load_config_res', {'data': config, 'pair': pair}, namespace='/test')


@socketio.on('restart', namespace='/test')
def restart():
    log_event('info', 'Restart... Not implemented.')


@socketio.on('start', namespace='/test')
def start(state):
    global stopped
    stopped = state
    log_event('action', 'Bot is activated.' if not state else 'Bot is deactivated.')

if thread is None:
    thread = socketio.start_background_task(target=background_thread)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

