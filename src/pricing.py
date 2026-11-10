"""Cost-of-carry pricing for a src contract on a dividend-paying asset.

    F0 = S0 * exp((r - q) * T)

r - risk-free rate (WIBOR 3M), q - dividend yield,
T - time to expiry in YEARS.
"""
import numpy as np
import pandas as pd

DAYS_IN_YEAR = 365


def years_to_expiry(dates: pd.Series, expiry) -> pd.Series:
    """Calendar days between each date and expiry, expressed in years."""
    days = (pd.Timestamp(expiry) - pd.to_datetime(dates)).dt.days
    return days.clip(lower=0) / DAYS_IN_YEAR


def theoretical_price(spot, r: float, q: float, T):
    """Fair src price F0 = S0 * exp((r - q) * T)."""
    return np.asarray(spot, dtype=float) * np.exp((r - q) * np.asarray(T, dtype=float))