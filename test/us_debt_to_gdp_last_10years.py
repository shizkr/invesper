import requests
import pandas as pd
import matplotlib.pyplot as plt

FRED_API_KEY = '230c47a4094b5f209026cf42c33e2be5'

def fetch_fred_series(series_id, api_key):
    url = f"https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": "2015-01-01"
    }
    resp = requests.get(url, params=params)
    obs = resp.json()['observations']
    df = pd.DataFrame(obs)
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    return df.set_index('date')[['value']]

# 1. Fetch data
debt = fetch_fred_series('GFDEBTN', FRED_API_KEY)
gdp = fetch_fred_series('GDP', FRED_API_KEY)

# 2. Resample to quarterly (GDP is quarterly, Debt is monthly)
debt_q = debt.resample('Q').last()
gdp_q = gdp.resample('Q').last()

# 3. Align indexes, calculate Debt/GDP ratio
df = pd.concat([debt_q, gdp_q], axis=1, keys=['Debt', 'GDP']).dropna()
df['Debt_to_GDP'] = df['Debt'] / df['GDP'] / 10

# 4. Plot
plt.figure(figsize=(14,7))
plt.plot(df.index, df['Debt_to_GDP'], label='US Federal Debt / GDP (%)')
plt.title('US Debt-to-GDP Ratio (Last 10 Years)')
plt.xlabel('Date')
plt.ylabel('Debt-to-GDP (%)')
plt.grid(True)

# 5. Annotate last point
last_date = df.index[-1]
last_pct = df['Debt_to_GDP'].iloc[-1]
plt.scatter(last_date, last_pct, color='red', zorder=5)
plt.annotate(
    f'{last_date.strftime("%Y-%m-%d")}\n{last_pct:.2f}%',
    xy=(last_date, last_pct),
    xytext=(-80,30),
    textcoords='offset points',
    arrowprops=dict(arrowstyle="->", color='red'),
    fontsize=12,
    backgroundcolor='white',
    color='red'
)

plt.legend()
plt.tight_layout()
plt.show()
