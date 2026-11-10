"""
Plotting Module
---------------
Generates visual comparisons between spot prices, market futures, and theoretical values.
"""

import matplotlib.pyplot as plt
import pandas as pd
import os

def plot_prices(df, title, filename):
    """
    Plots spot vs market futures over time with custom styling and saves the figure.
    """
    plt.figure(figsize=(10, 5))

    if 'Market_Futures' in df.columns:
        plt.plot(df['Date'], df['Market_Futures'], label='Cena zamknięcia kontraktu futures', color='#2b5c8f', linewidth=2, marker='o')
    if 'Spot' in df.columns:
        plt.plot(df['Date'], df['Spot'], label='Cena zamknięcia akcji', color='#e87d3e', linewidth=2, marker='s')
    if 'Theoretical_Futures' in df.columns:
        plt.plot(df['Date'], df['Theoretical_Futures'], label='Cena teoretyczna (F0)', linestyle='--', color='#2ca02c', linewidth=1.5)

    plt.title(title, fontsize=14, pad=15)
    plt.xlabel('Data')
    plt.ylabel('Cena')
    plt.xticks(rotation=45)

    plt.grid(axis='y', linestyle='-', alpha=0.6)
    plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=False)
    plt.tight_layout()

    os.makedirs('output', exist_ok=True)
    save_path = os.path.join('output', filename)
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Plot saved successfully to {save_path}")

def plot_mispricing(df, title, filename):
    """
    Plots the price spread / mispricing (Market Futures vs Theoretical Futures).
    """
    plt.figure(figsize=(10, 4))

    if 'Theoretical_Futures' in df.columns and 'Market_Futures' in df.columns:
        spread = df['Market_Futures'] - df['Theoretical_Futures']
        plt.bar(df['Date'], spread, color=['#d9534f' if x > 0 else '#5cb85c' for x in spread])

    plt.title(f"{title} - Mispricing Spread", fontsize=14, pad=15)
    plt.xlabel('Data')
    plt.ylabel('Spread (Market - Theoretical)')
    plt.xticks(rotation=45)
    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
    plt.grid(axis='y', linestyle='-', alpha=0.6)
    plt.tight_layout()

    os.makedirs('output', exist_ok=True)
    save_path = os.path.join('output', filename)
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Mispricing plot saved successfully to {save_path}")