import ccxt

import datetime
import utils
import rawApi
from trader import OkCoinTrader, BitfinexTrader
import statistics
# SYMBOL = {'bf': 'BTCUSD', 'ok': 'btc_usd'}
TIME_FRAME_HISTORY = 5
PRICE_POS = {'ok': 4, 'bf': 2}
MODE_ACTIVE = 'spy'
MODE_OPEN = 'open'


class CrazyIvan(object):
    def __init__(self, log_event, config, pair_name='pair_name'):
        self.data = {}
        self.spread = {'min': 99999999, 'max': 0, 'stdev': 0, 'top_border': 0, 'low_border': 0}
        self.mode = MODE_ACTIVE
        self.turn_around = False
        self.position = {}
        self.prev_update = datetime.datetime.now() - datetime.timedelta(days=1)
        self.big_candles_updated = False
        self.price = {'bf': 0, 'ok': 0}
        self.log_event = log_event
        self.config = config
        self.pair_name = pair_name
        self.spread_lst = []
        self.spreadratio_dict = {}
        # self.bitfinex = ccxt.bitfinex({
        #     'apiKey': config['BITFINEX']['API_KEY'],
        #     'secret': config['BITFINEX']['API_SECRET'],
        # })
        #
        # self.okcoin = ccxt.okcoinusd({
        #     'apiKey': config['OKCOIN']['API_KEY'],
        #     'secret': config['OKCOIN']['API_SECRET'],
        # })

        self.ok_trader = OkCoinTrader(config['OKCOIN']['API_KEY'], config['OKCOIN']['API_SECRET'], self.get_market())
        self.bf_trader = BitfinexTrader(config['BITFINEX']['API_KEY'], config['BITFINEX']['API_SECRET'],
                                        self.get_market())

        self.update_big_candles()
        self.log("info", "Crazy Ivan wakes up...")

    def update_config(self, config):
        self.config = config

    def get_market(self):
        return "{item1}/{item2}".format(item1=self.config['SYMBOL1'], item2=self.config['SYMBOL2'])

    def log(self, name, text):
        self.log_event(name, str(text), self.pair_name)

    def update_big_candles(self):
        prev_spread = self.spread
        try:
            time_frame = self.config['TIME_FRAME']
            pair_name = self.get_market()
            bf_dict = utils.to_dict(rawApi.get_candles_bf(pair_name, time_frame), PRICE_POS['bf'])
            ok_dict = utils.to_dict(rawApi.get_candles_ok(pair_name, time_frame), PRICE_POS['ok'])
            self.data = {}

            if len(bf_dict) == 0 or len(ok_dict) == 0:
                self.log("error", "Problems with candles api bf: {bf}, ok: {ok}".format(ok=ok_dict, bf=bf_dict))
                return None
            self.spread_lst = []
            self.spreadratio_dict = {}

            for k in bf_dict.keys():
                spread = abs(bf_dict[k] - ok_dict[k])  # Спред
                self.spread_lst.append(spread)
                self.spreadratio_dict[spread] = bf_dict[k] / ok_dict[k]

                # self.data[k] = {'ts': k, 'bf': bf_dict[k], 'ok': ok_dict[k], 'spread': spread}

                # if self.spread['max'] < spread:
                #     self.spread['max'] = spread
                # if self.spread['min'] > spread:
                #     self.spread['min'] = spread

            max_spread = self.spread['max'] = max(self.spread_lst)
            min_spread = self.spread['min'] = min(self.spread_lst)
            stdev_spread = self.spread['stdev'] = statistics.stdev(self.spread_lst)
            self.spread['top_border'] = max_spread - (stdev_spread * self.spreadratio_dict[max_spread])
            self.spread['low_border'] = min_spread + (stdev_spread * self.spreadratio_dict[min_spread])
        except Exception as e:
            self.log('error', e)
            self.spread = prev_spread

    def update(self, is_new_minute):
        date = datetime.datetime.now()
        trade_amount = self.config['TRADE_AMOUNT']
        profit_spread = self.config['PROFITABLE_SPREAD']
        order_place_offset =self.config['ORDER_PLACE_OFFSET']

        if date.minute % self.config['TIME_FRAME'] == 0 and is_new_minute:
            if not self.big_candles_updated:
                self.update_big_candles()
                self.log('info',
                         'Candles updated. Spread(max/min): <strong>{max_spread} / {min_spread}</strong>'
                         .format(max_spread=round(self.spread['max'], 2), min_spread=round(self.spread['min'], 2)))
                self.big_candles_updated = True
        else:
            self.big_candles_updated = False

        # хак чтобы запускалось в начале каждой минуты
        if (date - self.prev_update).total_seconds() >= 30 and is_new_minute:
            self.prev_update = datetime.datetime.now()
            bf_ticker = rawApi.get_ticker_bf(self.get_market())
            ok_ticker = rawApi.get_ticker_ok(self.get_market())
            if bf_ticker and ok_ticker:
                self.price = {'bf': bf_ticker, 'ok': ok_ticker}

            top_border = self.spread['top_border']
            low_border = self.spread['low_border']

            # top_border = self.spread['max'] * self.config['SPREAD_MAX_PERCENT']
            # low_border = self.spread['min'] * self.config['SPREAD_MIN_PERCENT']

            if self.mode == MODE_ACTIVE:
                sell_price = self.price['ok']['bid']
                buy_price = self.price['bf']['ask']
                last_spread = sell_price - buy_price
                self.log(self.mode,
                         u'Spread {top} <strong>[{spread}]</strong> {bottom}. <i>OkCoin {ok} / Bitfinex {bf}</i>'.format(
                             spread=round(last_spread, 4),
                             top=round(top_border, 4),
                             bottom=round(low_border, 4),
                             bf=round(buy_price, 4),
                             ok=round(sell_price, 4)))
                if last_spread > 0 and last_spread > top_border and top_border - low_border > profit_spread:
                    amount = trade_amount
                    profit = 0
                    if self.turn_around:
                        self.log(MODE_OPEN, '<i>Flip!</i>')
                        amount += trade_amount
                        # profit = (
                        #     (self.position['sell'] - buy_price) + (sell_price - self.position['buy']) * trade_amount)
                        #
                        # profit = -1
                        # utils.update_profit_file(data={'profit': profit,
                        #                                'pos_sell': self.position['sell'],
                        #                                'sell': sell_price,
                        #                                'pos_buy': self.position['buy'],
                        #                                'buy': buy_price})

                    self.log('action', 'OPEN POSITIONS: OkCoin sell {ok}, Bitfinex buy {bf}'.format(ok=sell_price,
                                                                                                    bf=buy_price))

                    api_ok = False

                    ok_result = self.ok_trader.new_order(amount, sell_price - order_place_offset, 'sell', 'limit')
                    self.log('debug', ok_result)
                    if ok_result and 'order_id' in ok_result.keys():
                        bf_result = self.bf_trader.new_order(amount, buy_price + order_place_offset, 'buy', 'limit')
                        self.log('debug', bf_result)
                        api_ok = bf_result is not None and 'id' in bf_result.keys()
                        # if profit != 0:
                        #     self.log('info', '<i>PROFIT: <strong>{profit}</strong></i>'.format(profit=round(profit, 2)))
                        #     # self.log('profit', profit)
                        #     # utils.update_profit_file(data={'profit': profit,
                        #     #                                'pos_sell': self.position['sell'],
                        #     #                                'sell': sell_price,
                        #     #                                'pos_buy': self.position['buy'],
                        #     #                                'buy': buy_price})

                    if not api_ok:
                        self.log('error', "Api Error: rollback disabled </i>Okcoin Sell</i>. Retry.")
                        #self.log('debug', self.ok_trader.new_order(amount, sell_price + 50, 'buy', 'limit'))
                        return None

                    self.position = {'buy': buy_price, 'sell': sell_price}
                    self.mode = MODE_OPEN

            elif self.mode == MODE_OPEN:
                sell_price = self.price['bf']['bid']
                buy_price = self.price['ok']['ask']
                last_spread = buy_price - sell_price
                self.log(self.mode,
                         u'Spread {top} <strong>[{spread}]</strong> {bottom}. <i>OkCoin {ok} / Bitfinex {bf}</i>'.format(
                             spread=round(last_spread, 4),
                             top=round(top_border, 4),
                             bottom=round(low_border, 4),
                             bf=round(sell_price, 4),
                             ok=round(buy_price, 4)))
                if last_spread > 0 and last_spread < low_border and top_border - low_border > profit_spread:
                    self.log('action',
                             'CLOSE POSITIONS: OkCoin buy {ok}, Bitfinex sell {bf}'.format(ok=buy_price,
                                                                                           bf=sell_price))

                    amount = trade_amount * 2
                    api_ok = False
                    ok_result = self.ok_trader.new_order(amount, buy_price + order_place_offset, 'buy', 'limit')
                    self.log('debug', ok_result)

                    if ok_result and 'order_id' in ok_result.keys():
                        bf_result = self.bf_trader.new_order(amount, sell_price - order_place_offset, 'sell', 'limit')
                        self.log('debug', bf_result)
                        api_ok = bf_result is not None and 'id' in bf_result.keys()

                    if not api_ok:
                        self.log('error', "Api Error: rollback disabled </i>Okcoin Buy</i>. Retry.")
                        #self.log('debug', self.ok_trader.new_order(amount, buy_price - 50, 'sell', 'limit'))
                        return None

                    profit = (
                        (self.position['sell'] - buy_price) + (sell_price - self.position['buy']) * trade_amount)

                    self.log('info', '<i>PROFIT: <strong>{profit}</strong></i>'.format(profit=round(profit, 2)))
                    self.turn_around = True

                    self.position = {}
                    self.mode = MODE_ACTIVE
                    self.log(self.mode, '<i>Flip!</i>')


                    # ci = CrazyIvan(log_event=lambda x, y: x)
                    # print('Waiting for fresh candle...')
                    # while True:
                    #     try:
                    #         ci.update()
                    #     except Exception as e:
                    #         print("Exception %s" %e)
                    #     time.sleep(2)
                    # print(ci.get_candles_ok('btc_usd', 15))
                    # print(ci.get_last_candle(ci.get_candles_ok('btc_usd', 15)))
                    # print(ci.get_last_candle(ci.get_candles_bf('BTCUSD', 15)))
                    #
                    # print(ci.get_candles_bf('BTCUSD', 15))


                    # def keywithmaxval(d):
                    #     """ a) create a list of the dict's keys and values;
                    #         b) return the key with the max value"""
                    #     v = list(d.values())
                    #     k = list(d.keys())
                    #     return k[v.index(max(v))]
