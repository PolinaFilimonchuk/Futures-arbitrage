"""Plots from your downloaded spot data (KGHM, PKO). No futures file needed.

    python plots.py                # KGHM and PKO
    python plots.py KGHM

Reads data/<name>_spot.csv. If data/<name>_futures.csv also exists, the futures
price is added to the price chart automatically.
Charts are shown in a window and saved to output/.
"""
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR, OUT_DIR = "data", "output"


def load_spot(name: str) -> pd.DataFrame:
    path = f"{DATA_DIR}/{name}_spot.csv"
    if not os.path.isfile(path):
        raise SystemExit(f"File not found: {os.path.abspath(path)}\nRun download_data.py first.")
    df = pd.read_csv(path, parse_dates=["date"]).dropna().sort_values("date")
    return df.set_index("date")


def plot_stock(name: str) -> pd.Series:
    df = load_spot(name)
    s = df["spot"]

    fig, axes = plt.subplots(3, 1, figsize=(11, 10), sharex=True)
    fig.suptitle(f"{name.upper()} ({s.index.min().date()} -> {s.index.max().date()})")

    ax = axes[0]
    ax.plot(s.index, s, label="Spot", lw=1)
    ax.plot(s.index, s.rolling(50).mean(), label="MA 50", lw=1)
    ax.plot(s.index, s.rolling(200).mean(), label="MA 200", lw=1)
    fut_path = f"{DATA_DIR}/{name}_futures.csv"
    if os.path.isfile(fut_path):
        fut = pd.read_csv(fut_path, parse_dates=["date"]).set_index("date")["futures"]
        ax.plot(fut.index, fut, label="Futures", lw=1)
    ax.set_title("Price"); ax.set_ylabel("PLN"); ax.legend(); ax.grid(alpha=.3)

    ax = axes[1]
    log_ret = np.log(s / s.shift(1))
    vol = log_ret.rolling(30).std() * np.sqrt(252)
    ax.plot(vol.index, vol, color="tab:orange", lw=1)
    ax.set_title("30-day rolling volatility (annualised)"); ax.grid(alpha=.3)

    ax = axes[2]
    drawdown = s / s.cummax() - 1
    ax.fill_between(drawdown.index, drawdown, 0, color="tab:red", alpha=.4)
    ax.set_title("Drawdown from previous peak"); ax.grid(alpha=.3)

    fig.autofmt_xdate()
    fig.tight_layout()
    os.makedirs(OUT_DIR, exist_ok=True)
    fig.savefig(f"{OUT_DIR}/{name}_spot_plots.png", dpi=130, bbox_inches="tight")
    return s


def plot_compare(series: dict) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    for name, s in series.items():
        ax.plot(s.index, s / s.iloc[0] * 100, label=name.upper(), lw=1)
    ax.set_title("Normalised prices (start = 100)")
    ax.legend(); ax.grid(alpha=.3); fig.autofmt_xdate()
    fig.savefig(f"{OUT_DIR}/compare_spot.png", dpi=130, bbox_inches="tight")


def main(names) -> None:
    series = {n.lower(): plot_stock(n.lower()) for n in names}
    if len(series) > 1:
        plot_compare(series)
    plt.show()


if __name__ == "__main__":
    main(sys.argv[1:] or ["KGHM", "PKO"])