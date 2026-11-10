
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.pricing import theoretical_price

DAYS_IN_YEAR = 365


# ---------- expiry calendar ----------
def third_friday(year: int, month: int) -> pd.Timestamp:
    first = pd.Timestamp(year=year, month=month, day=1)
    first_friday = first + pd.Timedelta(days=(4 - first.weekday()) % 7)
    return first_friday + pd.Timedelta(days=14)


def expiry_calendar(start: pd.Timestamp, end: pd.Timestamp) -> list:
    return sorted(third_friday(y, m)
                  for y in range(start.year, end.year + 2) for m in (3, 6, 9, 12))


def assign_expiry(dates: pd.Series, calendar: list) -> pd.Series:
    cal = np.array(calendar, dtype="datetime64[ns]")
    idx = np.searchsorted(cal, dates.values.astype("datetime64[ns]"), side="left")
    return pd.Series(cal[idx], index=dates.index)


# ---------- data ----------
def load(name: str, rates_path=None, r_default=0.0524) -> pd.DataFrame:
    spot = pd.read_csv(f"data/{name}_spot.csv", parse_dates=["date"])
    fut = pd.read_csv(f"data/{name}_futures.csv", parse_dates=["date"])
    df = spot.merge(fut, on="date", how="inner").dropna().sort_values("date")
    if rates_path:
        rates = pd.read_csv(rates_path, parse_dates=["date"]).sort_values("date")
        df = pd.merge_asof(df, rates.rename(columns={"r": "r_t"}), on="date")
        df["r_t"] = df["r_t"].fillna(r_default)
    else:
        df["r_t"] = r_default
    return df.reset_index(drop=True)


def build(df: pd.DataFrame, q: float) -> pd.DataFrame:
    df = df.copy()
    df["expiry"] = assign_expiry(df["date"], expiry_calendar(df["date"].min(), df["date"].max()))
    df["days_left"] = (df["expiry"] - df["date"]).dt.days
    df["T"] = df["days_left"] / DAYS_IN_YEAR
    df["theoretical"] = theoretical_price(df["spot"], df["r_t"].values, q, df["T"].values)
    df["mispricing"] = df["src"] - df["theoretical"]
    return df


# ---------- strategy ----------
def backtest(df: pd.DataFrame, cost: float, min_days: int) -> pd.DataFrame:
    """One trade per contract cycle. cost = round-trip cost as a fraction of spot."""
    trades = []
    last_date = df["date"].max()
    for expiry, g in df.groupby("expiry"):
        if expiry > last_date:                       # contract not settled yet
            continue
        g = g[g["days_left"] >= min_days]            # skip noisy days near expiry / roll
        sig = g[g["mispricing"].abs() > cost * g["spot"]]
        if sig.empty:
            continue
        e = sig.iloc[0]
        undervalued = e["mispricing"] < 0
        profit = abs(e["mispricing"]) - cost * e["spot"]
        trades.append({
            "entry_date": e["date"], "expiry": expiry,
            "signal": "undervalued" if undervalued else "overvalued",
            "futures_leg": "long" if undervalued else "short",
            "spot_leg": "short" if undervalued else "long",
            "spot": e["spot"], "src": e["src"], "theoretical": e["theoretical"],
            "profit_per_share": profit,
            "return": profit / e["spot"],
            "days_held": int(e["days_left"]),
        })
    return pd.DataFrame(trades)


def report(name: str, df: pd.DataFrame, trades: pd.DataFrame, out: str) -> None:
    os.makedirs(out, exist_ok=True)
    print(f"\n== {name} ==  {df['date'].min().date()} -> {df['date'].max().date()}, {len(df)} days")
    print(f"Mean mispricing over all days: {df['mispricing'].mean():.2f}  "
          f"(far from 0 usually means r or q in the model is off)")
    if trades.empty:
        print("No trade exceeded the transaction cost threshold.")
        return
    trades.to_csv(f"{out}/{name.lower()}_trades.csv", index=False)
    ann = (trades["return"] * DAYS_IN_YEAR / trades["days_held"]).mean()
    print(f"Trades:                  {len(trades)} "
          f"({(trades['signal'] == 'undervalued').sum()} undervalued, "
          f"{(trades['signal'] == 'overvalued').sum()} overvalued)")
    print(f"Mean profit per share:   {trades['profit_per_share'].mean():.2f} PLN")
    print(f"Total profit per share:  {trades['profit_per_share'].sum():.2f} PLN")
    print(f"Mean return per trade:   {trades['return'].mean():.2%}")
    print(f"Mean annualised return:  {ann:.2%}")

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.step(trades["entry_date"], trades["return"].cumsum(), where="post")
    ax.set(title=f"{name}: cumulative arbitrage return (sum of per-trade returns)", ylabel="return")
    ax.grid(alpha=.3); fig.autofmt_xdate()
    fig.savefig(f"{out}/{name.lower()}_cumulative.png", dpi=130, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    p = argparse.ArgumentParser(description="Futures cash-and-carry arbitrage backtest")
    p.add_argument("names", nargs="+", help="e.g. KGHM PKO (files data/<name>_spot.csv, _futures.csv)")
    p.add_argument("--r", type=float, default=0.0524, help="constant risk-free rate (WIBOR 3M)")
    p.add_argument("--rates", help="CSV date,r with time-varying WIBOR 3M (overrides --r)")
    p.add_argument("--q", type=float, default=0.0545, help="annual dividend yield")
    p.add_argument("--cost", type=float, default=0.003, help="round-trip costs as fraction of spot")
    p.add_argument("--min-days", type=int, default=5, help="min days to expiry for an entry")
    p.add_argument("--out", default="output")
    a = p.parse_args()

    for name in a.names:
        name = name.lower()
        df = build(load(name, a.rates, a.r), a.q)
        report(name.upper(), df, backtest(df, a.cost, a.min_days), a.out)


if __name__ == "__main__":
    main()