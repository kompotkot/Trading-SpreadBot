# Crypto Trade bot v0.3a

This trading bot is based on the price difference between currencies on the Bitfinex and OkCoin exchanges.
Upon reaching the specified spread between currencies, two positions are opened on both exchanges. Each position is aimed at narrowing the spread.


![alt text](https://github.com/kompotkot/Trading-SpreadBot/blob/master/Example.jpg?raw=true)


* crazyivan.py - main bot-logic
* trader.py - order manager

## Launch
```
mkdir logs
source env/bin/activate
python3 crazyivan-serv.py
```

## Manage
* Open http://localhost:5000 in browser
* Login none/none

## Config
```
config.json
```

## Thanks
* github repository with OkCoin API
* github repository with Bitfinex API

## Developed by
* Fancy machines (C) 2017
