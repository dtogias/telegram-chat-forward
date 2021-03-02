from pprint import pprint
import ccxt
from settings import BINANCE_API_KEY, BINANCE_API_SECRET

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


async def binance_job():
    positions = exchange.fetch_positions()
    for entry in positions:
        entry_price = float(entry['entryPrice'])
        if entry_price > 0.0:
            pprint(entry)