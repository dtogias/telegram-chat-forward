import asyncio
import logging
from pprint import pprint

import ccxt
import yaml
from telethon.errors.rpcerrorlist import FloodWaitError

from common import intify, diff
from settings import BINANCE_API_KEY, BINANCE_API_SECRET, defaults

print('CCXT Version:', ccxt.__version__)

exchange = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_API_SECRET,
    'enableRateLimit': True,  # https://github.com/ccxt/ccxt/wiki/Manual#rate-limit
    'options': {
        'defaultType': 'future',
        'warnOnFetchOpenOrdersWithoutSymbol': False
    },
})

# {
#   'symbol': 'EOSUSDT',
#   'initialMargin': '0',
#   'maintMargin': '0',
#   'unrealizedProfit': '0.00000000',
#   'positionInitialMargin': '0',
#   'openOrderInitialMargin': '0',
#   'leverage': '20',
#   'isolated': False,
#   'entryPrice': '0.0000',
#   'maxNotional': '250000',
#   'positionSide': 'BOTH',
#   'positionAmt': '0.0',
#   'notional': '0',
#   'isolatedWallet': '0'
#   }

class BPosition:

    def __init__(self, bdict):
        self.symbol = bdict['symbol']
        self.initialMargin = float(bdict['initialMargin'])
        self.leverage = int(bdict['leverage'])
        self.entryPrice = float(bdict['entryPrice'])
        self.positionSide = bdict['positionSide']
        self.positionAmt = float(bdict['positionAmt'])

    def __str__(self):
        return "(\"symbol\": {0}, \"initialMargin\": {1}, \"leverage\": {2}, " \
               "\"entryPrice\": {3}, \"positionSide\": {4}, \"positionAmt\": {5})".format(self.symbol,
                                                                                          self.initialMargin,
                                                                                          self.leverage,
                                                                                          self.entryPrice,
                                                                                          self.positionSide,
                                                                                          self.positionAmt)

    def __repr__(self):
        return "(\"symbol\": {0}, \"initialMargin\": {1}, \"leverage\": {2}, " \
               "\"entryPrice\": {3}, \"positionSide\": {4}, \"positionAmt\": {5})".format(self.symbol,
                                                                                          self.initialMargin,
                                                                                          self.leverage,
                                                                                          self.entryPrice,
                                                                                          self.positionSide,
                                                                                          self.positionAmt)

    def __iter__(self):
        pass

    def __hash__(self):
        return hash((self.symbol, self.entryPrice))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.symbol == other.symbol and self.entryPrice == other.entryPrice

        return False


class Binance:

    def __init__(self, file):
        with open(file, 'r') as f:
            params = yaml.safe_load(f)

        self.positions = []
        bdict = params['binance']
        for entry in bdict:
            self.positions.append(BPosition(entry))


def yaml_equivalent_of_default(dumper, data):
    dict_representation = data.__dict__
    node = dumper.represent_dict(dict_representation)
    return node


yaml.add_representer(BPosition, yaml_equivalent_of_default)


async def binance_job(client):
    positions = exchange.fetch_positions()
    current_positions = []
    for entry in positions:
        b_position = BPosition(entry)
        if b_position.entryPrice > 0.0:
            current_positions.append(b_position)
            pprint(entry)

    binance = Binance('binance.yaml')

    # diff
    diff_positions = diff(binance.positions, current_positions)
    if diff_positions:
        to_chat = defaults.get('to')
        msg = "[Binance Futures - Updates]\n\n"
        for item in current_positions:
            msg = msg + " symbol: {0}\n entry price: {1}\n\n".format(item.symbol, item.entryPrice)

        try:
            await client.send_message(intify(to_chat), msg)
        except FloodWaitError as fwe:
            print(f'{fwe}')
        except Exception as err:
            logging.exception(err)

    with open(r'binance.yaml', 'w') as file:
        yaml.dump({'binance': current_positions}, file)
