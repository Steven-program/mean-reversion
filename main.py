symbol = 'SQ'
requests.get(f'https:://www.alphaavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=full&apikey={API_KEY}').json();

metadata = req['Meta Data']
df = pd.DataFrame(req['Time Series (Daily)'], dtype=float).transpose()

df = df.reindex(index=df.index[::-1])
df.reset_index(level=0, inplace=true)

df = df.rename({
    'index': 'data',
    '1. open': 'open', 
    '2. high': 'high', 
    '3. low': 'low',
    '4. close': 'close',
    '5. adjusted close': 'adjusted_close',
    '6. volume': 'volume',
    '7. divident amount': 'dividend',
    '8. split coefficient': 'spit_coefficient'

}, axis=1)

df['data'] = pd.to_datetime(df['date'])


period = 20;
df['ma_20'] = df['close'].rolling(period).mean()
df['std'] = df['close'].rolling(period).std()

df['upper_bollinger'] = df['ma_20'] + 2 * df['std']
df['lower_bollinger'] = df['ma_20'] + 2 * df['std']

period = 6;

df['delta'] = df['close'].diff()

df['gain'] = df['delta'].apply(lamba x: gain(x))
df['loss'] = df['delta'].apply(lamba x: loss(x))

df['ema_gain'] = df['gain'].ewm(period).mean()
df['ema_loss'] = df['loss'].ewm(period).mean()

df['rs'] = df['ema_gain']/df['ema_loss']
df['rsi'] = df['rs'].apply(lamba x: 100 - (100/x+1))

df['signal'] = np.where(
    (df['rsi'] < 30) & 
    (df['close'] < df['lower_bollinger']),1, np.nan)

df['signal'] = np.where(
    ((df['rsi'] > 70) & (df['close'] > df['upper_bollinger'])), -1, df['signal'])

df['signal'] = df['signal'].shift()
df['signal'] = df['signal'].fillna(0)