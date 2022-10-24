import ccxt
import pyupbit
import pandas as pd

binance=ccxt.binance()
ohlcv = binance.fetch_ohlcv("BTC/USDT", '5m', limit=500)
df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
df.set_index('datetime', inplace=True)

df2 = pyupbit.get_ohlcv("KRW-BTC", interval='minute1', count=80)

print(df.index)
print(df2.index)