"""
Generates a synthetic air-quality dataset for demo/tutorial purposes so the
whole pipeline is runnable end-to-end without needing a real data source or
API keys. Replace data/raw/air_quality.csv with your real dataset and this
script is no longer needed - data_ingestion.py just reads whatever CSV is at
config.data_ingestion.source_path.
"""

import numpy as np
import pandas as pd

np.random.seed(42)
N = 2000

pm2_5 = np.random.gamma(2, 20, N)
pm10 = pm2_5 * np.random.uniform(1.2, 1.8, N) + np.random.normal(0, 5, N)
no2 = np.random.gamma(2, 10, N)
so2 = np.random.gamma(1.5, 5, N)
co = np.random.gamma(2, 0.5, N)
o3 = np.random.gamma(2, 15, N)
temperature = np.random.normal(25, 7, N)
humidity = np.clip(np.random.normal(55, 15, N), 5, 100)
wind_speed = np.clip(np.random.gamma(2, 2, N), 0, None)

# Synthetic AQI: correlated with pollutants, mildly reduced by wind, noise added
aqi = (
    0.5 * pm2_5
    + 0.3 * pm10
    + 0.8 * no2
    + 0.6 * so2
    + 15 * co
    + 0.4 * o3
    - 1.5 * wind_speed
    + np.random.normal(0, 10, N)
)
aqi = np.clip(aqi, 0, None)

df = pd.DataFrame(
    {
        "PM2_5": pm2_5.round(2),
        "PM10": pm10.round(2),
        "NO2": no2.round(2),
        "SO2": so2.round(2),
        "CO": co.round(2),
        "O3": o3.round(2),
        "Temperature": temperature.round(2),
        "Humidity": humidity.round(2),
        "WindSpeed": wind_speed.round(2),
        "AQI": aqi.round(2),
    }
)

df.to_csv("data/raw/air_quality.csv", index=False)
print(f"Wrote {df.shape[0]} rows to data/raw/air_quality.csv")
