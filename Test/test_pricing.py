import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pandas as pd
from src import theoretical_price, analyze, years_to_expiry


def test_fair_price_formula():
    assert math.isclose(float(theoretical_price(100, 0.05, 0.01, 1.0)), 100 * math.exp(0.04))


def test_zero_time_equals_spot():
    assert float(theoretical_price(123.4, 0.05, 0.02, 0.0)) == 123.4


def test_years_to_expiry_uses_years_not_days():
    d = pd.Series(pd.to_datetime(["2025-01-01"]))
    assert math.isclose(years_to_expiry(d, "2026-01-01").iloc[0], 1.0)


def test_signals():
    df = pd.DataFrame({"date": pd.to_datetime(["2025-01-01", "2025-01-01"]),
                       "spot": [100.0, 100.0], "src": [90.0, 120.0]})
    res = analyze(df, 0.05, 0.0, expiry="2025-12-31")
    assert list(res["status"]) == ["undervalued", "overvalued"]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("ok", name)