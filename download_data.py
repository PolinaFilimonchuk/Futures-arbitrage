import datetime as dt
import os
import sys

import pandas as pd
import yfinance as yf

TICKERS = {"KGHM": "KGH.WA", "PKO": "PKO.WA"}
YEARS = 10


def download_spot(name: str, out_dir: str = "data") -> pd.DataFrame:
    end = dt.date.today()
    start = end - dt.timedelta(days=365 * YEARS + 2)
    # auto_adjust=False: raw close prices, comparable with the src price
    raw = yf.download(TICKERS[name], start=start.isoformat(), end=end.isoformat(),
                      auto_adjust=False, progress=False)
    if raw.empty:
        raise SystemExit(f"No data returned for {TICKERS[name]}")
    if isinstance(raw.columns, pd.MultiIndex):      # newer yfinance versions
        raw.columns = raw.columns.get_level_values(0)

    df = pd.DataFrame({
        "date": pd.to_datetime(raw.index).tz_localize(None),
        "spot": raw["Close"].values,
    }).dropna()

    os.makedirs(out_dir, exist_ok=True)
    path = f"{out_dir}/{name.lower()}_spot.csv"
    df.to_csv(path, index=False)
    print(f"{name}: {len(df)} rows, {df['date'].min().date()} -> {df['date'].max().date()} saved to {path}")
    return df


if __name__ == "__main__":
    names = [a.upper() for a in sys.argv[1:]] or list(TICKERS)
    for n in names:
        download_spot(n)