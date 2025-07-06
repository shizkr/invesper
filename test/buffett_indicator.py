import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as web

# Download Wilshire 5000 (Market Cap) and US GDP from FRED
market_cap = web.DataReader('WILL5000INDFC', 'fred', '1970-01-01')
gdp = web.DataReader('GDP', 'fred', '1970-01-01')

# GDP is quarterly; Market Cap is daily/monthly, so resample market cap to quarterly for alignment
market_cap_q = market_cap.resample('Q').last()

# Align GDP and Market Cap data
df = pd.DataFrame({
    'MarketCap': market_cap_q['WILL5000INDFC'],
    'GDP': gdp['GDP']
})

# Calculate Buffett Indicator
df['BuffettIndicator'] = df['MarketCap'] / df['GDP']

# Plot
plt.figure(figsize=(14, 6))
plt.plot(df.index, df['BuffettIndicator'], label='Buffett Indicator (Market Cap / GDP)')
plt.title('Buffett Indicator (Wilshire 5000 / US GDP)')
plt.xlabel('Year')
plt.ylabel('Buffett Indicator')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()