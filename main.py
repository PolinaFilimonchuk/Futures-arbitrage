
import argparse
import os

import arbitrage
from src.plotting import plot_prices, plot_mispricing


def main() -> None:
    p = argparse.ArgumentParser(description="Futures fair-value analysis and arbitrage backtest")
    p.add_argument("names", nargs="*", default=["KGHM", "PKO"], help="e.g. KGHM PKO")
    p.add_argument("--r", type=float, default=0.0524, help="constant risk-free rate (WIBOR 3M)")
    p.add_argument("--rates", help="CSV date,r with time-varying WIBOR 3M (overrides --r)")
    p.add_argument("--q", type=float, default=0.0545, help="annual dividend yield")
    p.add_argument("--cost", type=float, default=0.003, help="round-trip costs as fraction of spot")
    p.add_argument("--min-days", type=int, default=5, help="min days to expiry for an entry")
    p.add_argument("--out", default="output")
    a = p.parse_args()

    os.makedirs(a.out, exist_ok=True)
    for name in (n.lower() for n in a.names):
        try:
            raw = arbitrage.load(name, a.rates, a.r)
        except FileNotFoundError as e:
            print(f"\n[{name.upper()}] missing file: {e.filename}\n"
                  f"  spot: python download_data.py {name.upper()}\n"
                  f"  src: export it yourself to data/{name}_futures.csv (date,src)")
            continue

        df = arbitrage.build(raw, a.q)
        trades = arbitrage.backtest(df, a.cost, a.min_days)
        arbitrage.report(name.upper(), df, trades, a.out)

        df.to_csv(f"{a.out}/{name}_results.csv", index=False)
        plot_prices(df, f"{name.upper()}: spot vs src", f"{a.out}/{name}_prices.png")
        plot_mispricing(df, name.upper(), f"{a.out}/{name}_mispricing.png")


if __name__ == "__main__":
    main()