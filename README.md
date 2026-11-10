# Futures Valuation & Arbitrage Analysis (GPW: KGHM & PKO BP)

A Python-based quantitative finance project designed to evaluate stock futures contracts traded on the Warsaw Stock Exchange (GPW), specifically focusing on **KGHM Polska Miedź** and **PKO Bank Polski**. The project implements the classical **cost-of-carry pricing model**, identifies market misalignments, evaluates arbitrage opportunities, and accounts for transaction costs.

---

## Project Structure

```text
futures-arbitrage-analysis/
│
├── data/                  # Historical CSV datasets for spot & futures prices
│   ├── kghm_data.csv      # KGHM market data
│   └── pko_data.csv       # PKO BP market data
│
├── output/                # Generated visualizations and analysis reports
│   └── kghm_valuation.png
│
├── src/                   # Core source package
│   ├── __init__.py
│   ├── analysis.py        # Spread computation and arbitrage status classification
│   ├── plotting.py        # Data visualization generator (Matplotlib)
│   └── pricing.py         # Cost-of-carry theoretical pricing engine
│
├── Test/                  # Test modules and experimental scripts
├── arbitrage.py           # Feasibility analysis factoring in transaction costs
├── download_data.py       # Utility for downloading/fetching market data feeds
├── extract_data.py        # Data parser and preprocessing utility
├── main.py                # Main orchestration pipeline script
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```

---

##  Mathematical Model

The theoretical futures price is modeled using continuous compounding under the cost-of-carry framework:

$$F_0 = S_0 e^{(r - q)T}$$

Where:
* $S_0$ = Current spot price of the underlying asset
* $r$ = Risk-free interest rate (e.g., WIBOR 3M = $5.24\%$)
* $q$ = Annualized dividend yield (5.45\%)
* $T$ = Time to maturity expressed in years

---

## Arbitrage Strategies

Depending on the relationship between the market futures price and the theoretical price :

1. **Overvalued Contract:**
   * **Strategy:** Sell (short) futures contracts and buy (long) the underlying stock in the spot market.
2. **Undervalued Contract:**
   * **Strategy:** Buy (long) futures contracts and sell (short) the underlying stock.
   *(Note: Execution requires verifying that the absolute spread exceeds transaction costs and borrowing fees).*


---

## Key Results & Findings

Based on historical pricing runs across KGHM Polska Miedź and PKO Bank Polski datasets:

* **KGHM Contracts:** Demonstrated persistent mispricings during volatile periods (March 2025 – March 2026), with maximum absolute pricing spreads exceeding $78.00$ PLN. Contracts frequently oscillated between overvalued and undervalued states, providing viable windows for cash-and-carry arbitrage once transaction costs are factored in.
* **PKO BP Contracts:** Showed consistent alignment with theoretical cost-of-carry boundaries during mid-2025, with localized peaks reaching up to $33.59$ PLN spread divergence on July 10, 2025 (S0 = 72.36 vs $F_{market} = 76.13$).
* **Strategy Execution:** Confirmed that automated theoretical pricing flags successfully isolate optimal entry points for both long futures/short spot and short futures/long spot positions.



