import bitfinex.client
import logging
import time
from okapi.OkcoinSpotAPI import OKCoinSpot
import json

CACHE_TIME_SECONDS = 3


class BitfinexTrader(object):
    def __init__(self, key, secret, symbol):
        self.symbol = symbol.replace(u'/', '')

        self.trading_client = bitfinex.client.Trading(key=key,
                                                      secret=secret,
                                                      symbol=self.symbol)
        self.my_orders = []
        self.cache_time = time.time()

    def get_cached(self, func, value):
        if time.time() - self.cache_time >= CACHE_TIME_SECONDS:
            return func()
        else:
            return value

    def get_my_orders(self, force=False):
        try:
            if force:
                orders = self.trading_client.orders()
            else:
                orders = self.get_cached(lambda: self.trading_client.orders(), self.my_orders)

            if not orders:
                logging.error('Get my orders missed...')

            return orders if orders else self.my_orders
        except Exception as e:
            logging.fatal('TraderAPI new order exception %s' % e)
            return self.my_orders

    def new_order(self, amount=0, price=0, side='sell', order_type='limit'):
        try:
            return self.trading_client.new_order(amount=amount, price=price, side=side, order_type=order_type)
        except Exception as e:
            logging.fatal('TraderAPI new order exception %s' % e)
            return None

    def cancel_order(self, order_id):
        try:
            return self.trading_client.cancel_order(order_id)
        except Exception as e:
            logging.fatal('TraderAPI cancel order exception %s' % e)
            return None


class OkCoinTrader(object):
    def __init__(self, key, secret, symbol):
        self.symbol = symbol.replace(u'/', '_').lower()
        self.ok_api = OKCoinSpot('www.okcoin.com', key, secret)

    def get_my_orders(self, force=False):
        pass

    def new_order(self, amount=0, price=0, side='sell', order_type='limit'):
        try:
            trade_type = "{side}{t}".format(side=side,
                                            t="_market" if order_type == 'market' else "")

            result = json.loads(self.ok_api.trade(self.symbol, trade_type, price, amount))
            if not result['result']:
                logging.fatal('TraderAPI new order error %s' % result)
            return result
        except Exception as e:
            logging.fatal('TraderAPI new order exception %s' % e)
            return None

    def cancel_order(self, order_id):
        try:
            result = json.load(self.ok_api.cancelOrder(self.symbol, order_id))
            if not result['result']:
                logging.fatal('TraderAPI new order error %s' % result)
            return result['result']

        except Exception as e:
            logging.fatal('TraderAPI cancel order exception %s' % e)
            return None
