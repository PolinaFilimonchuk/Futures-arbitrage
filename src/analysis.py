"""Basis, mispricing and arbitrage-signal logic (slides 2, 5, 6, 7, 10)."""
from dataclasses import dataclass
import pandas as pd
from .pricing import theoretical_price, years_to_expiry


@dataclass(frozen=True)
class Signal:
    status: str       # "undervalued" | "overvalued" | "fair"
    futures_leg: str  # position in the src contract
    spot_leg: str     # position in the underlying


SIGNALS = {
    "undervalued": Signal("undervalued", "long (buy)", "short (sell)"),
    "overvalued": Signal("overvalued", "short (sell)", "long (buy)"),
    "fair": Signal("fair", "none", "none"),
}


def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    return df.dropna(subset=["spot", "src"]).sort_values("date").reset_index(drop=True)


def analyze(df, r, q, expiry=None, tolerance=0.0) -> pd.DataFrame:
    """Add T, theoretical price, basis, mispricing and status columns.

    basis       = spot - src                (slide 2 definition)
    mispricing  = src - theoretical price   (<0 undervalued, >0 overvalued)
    tolerance   = |mispricing| band treated as fair (e.g. transaction costs)
    """
    out = df.copy()
    expiry = pd.Timestamp(expiry) if expiry else out["date"].max()
    out["T"] = years_to_expiry(out["date"], expiry)
    out["theoretical"] = theoretical_price(out["spot"], r, q, out["T"])
    out["basis"] = out["spot"] - out["src"]
    out["mispricing"] = out["src"] - out["theoretical"]
    out["abs_diff"] = out["mispricing"].abs()
    out["status"] = "fair"
    out.loc[out["mispricing"] < -tolerance, "status"] = "undervalued"
    out.loc[out["mispricing"] > tolerance, "status"] = "overvalued"
    return out


def summarize(res: pd.DataFrame) -> dict:
    worst = res.loc[res["abs_diff"].idxmax()]
    return {
        "n_days": len(res),
        "largest_gap_date": worst["date"].date(),
        "largest_gap": float(worst["abs_diff"]),
        "largest_gap_signal": SIGNALS[worst["status"]],
        "mean_mispricing": float(res["mispricing"].mean()),
        "mean_basis": float(res["basis"].mean()),
        "status_counts": res["status"].value_counts().to_dict(),
    }