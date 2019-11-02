import json
import logging
import time
import datetime
import colorlog
# config = {
#     "SPREAD_MAX_PERCENT": 0.8,
#     "SPREAD_MIN_PERCENT": 1.4,
#     "TIME_FRAME": 5,
#     "TRADE_AMOUNT": 0.01,
#     "PROFITABLE_SPREAD": 35,
#     "SYMBOL1": "BTC",
#     "SYMBOL2": "USD",
#     "OKCOIN": {
#         "API_KEY": "YOUR-API-KEY",
#         "API_SECRET": "YOUR-API-KEY"
#     },
#     "BITFINEX": {
#         "API_KEY": "YOUR-API-KEY",
#         "API_SECRET": "YOUR-API-KEY"
#     }
# }


def init_logger():
    logging.basicConfig(filename='logs/log-{time}.log'.format(time=get_timestamp()), level=logging.INFO)
    logging.getLogger('requests').setLevel(logging.CRITICAL)
    logging.getLogger('socketio').setLevel(logging.CRITICAL)
    logging.getLogger('requests.packages.urllib3').setLevel(logging.CRITICAL)
    logging.getLogger('engineio').setLevel(logging.ERROR)
    logging.getLogger('werkzeug').setLevel(logging.ERROR)

    root = logging.getLogger()
    # root.setLevel(logging.INFO)
    handler = colorlog.StreamHandler()

    handler.setFormatter(colorlog.ColoredFormatter(
        '%(blue)s%(asctime)s: %(log_color)s%(message)s', "%Y-%m-%d %H:%M:%S"))

    root.addHandler(handler)


def load_config(file_name='config.json'):
    with open(file_name, 'r') as f:
        config = json.load(f)
        return config


def save_config(config, file_name='config.json'):
    with open(file_name, 'w') as f:
        json.dump(config, f)


def update_profit_file(file_name='profit.json', data={}):
    with open(file_name, 'rw') as f:
        json_data = json.load(f)
        json_data[datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")] = data
        json.dump(json_data, f)


def get_timestamp():
    return int(time.time() * 1000)


def to_dict(lst, price_pos):
    result = {}
    for item in lst:
        result[item[0]] = item[price_pos]
    return result


def to_time(ms):
    return datetime.datetime.fromtimestamp(ms / 1000.0).strftime('%Y-%m-%d %H:%M:%S')


conf = {
    'SPREAD_MAX_PERCENT': 0.8,
    'SPREAD_MIN_PERCENT': 1.4,
    'TIME_FRAME': 5,
    'TRADE_AMOUNT': 0.01,
    'PROFITABLE_SPREAD': 35,
    'SYMBOLS': { 'BTC', 'USD'},
    'OKCOIN': {
        'API_KEY': 'YOUR-API-KEY',
        'API_SECRET': 'YOUR-API-KEY',
    },
    'BITFINEX': {
        'API_KEY': 'YOUR-API-KEY',
        'API_SECRET': 'YOUR-API-KEY',
    }
}
