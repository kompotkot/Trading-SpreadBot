# -*- coding: utf-8 -*-
import time
import unittest
import ccxt
import rawApi
class TestApi(unittest.TestCase):

    def test_getcoinmarketcap(self):
        #print(rawApi.get_coin_market_cap())
        pass

    def test_ccxt(self):
        #print(ccxt.markets)  # print a list of all available market classes
        hitbtc = ccxt.hitbtc({'verbose': True})
        bitmex = ccxt.bitmex()
        huobi = ccxt.huobi()
        bitfinex = ccxt.bitfinex({
            'apiKey': 'YOUR-API-KEY',
            'secret': 'YOUR-API-KEY',
        })
        okcoinusd = ccxt.okcoinusd({
            'apiKey': 'YOUR-API-KEY',
            'secret': 'YOUR-API-KEY',
        })

        trade_amount = 0.1
        market = 'ETH_USD'
        ticker = okcoinusd.fetch_ticker(market)
        print(ticker)
        print('debug %s' % okcoinusd.create_limit_buy_order(market, trade_amount, ticker['ask'] + 1))
        # print('debug %s' % okcoinusd.create_market_sell_order('BTC/USD', trade_amount))

        #ticker = bitfinex.fetch_ticker(market)
        #print(ticker)

        #print('debug %s' % bitfinex.create_market_sell_order('BTC/USD', trade_amount))
        #print('debug %s' % bitfinex.create_market_buy_order('BTC/USD', trade_amount))

        #print('debug %s' % bitfinex.create_limit_buy_order(market, trade_amount, ticker['ask'] + 1))

        #print('debug', okcoinusd.create_limit_buy_order(market, trade_amount, ticker['bid'] + 1))

        #hitbtc_products = hitbtc.load_products()

        # print(hitbtc.id, hitbtc_products)
        # print(bitmex.id, bitmex.load_products())
        # print(huobi.id, huobi.load_products())
        #
        # print(hitbtc.fetch_order_book(hitbtc.symbols[0]))
        # print(bitmex.fetch_ticker('BTC/USD'))
        # print(huobi.fetch_trades('LTC/CNY'))
        #
        # print(bitfinex.fetch_balance())

        # sell one BTC/USD for market price and receive $ right now
        # print(bitfinex.id, bitfinex.create_market_buy_order('BTC/USD', 0.01))
        #
        # # limit buy BTC/EUR, you pay €2500 and receive 1 BTC when the order is closed
        # print(bitfinex.id, bitfinex.create_limit_buy_order('BTC/USD', 0.01, '2500.00'))

if __name__ == '__main__':
    unittest.main()