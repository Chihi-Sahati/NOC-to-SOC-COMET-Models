import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(BASE, "paper", "jtit_submission", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

def plot_edns():
    months = np.linspace(0, 36, 500)
    # Expected demand grows exponentially
    D_exp = 100 * np.exp(0.05 * months)
    
    # Served capacity grows stepwise (e.g., infrastructure upgrades)
    S_cap = np.zeros_like(months)
    S_cap[months < 12] = 120
    S_cap[(months >= 12) & (months < 24)] = 250
    S_cap[months >= 24] = 450
    
    gap = np.maximum(D_exp - S_cap, 0)
    edns = np.cumsum(gap) * (months[1] - months[0]) # integral approximation
    
    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    
    color1 = 'tab:blue'
    ax1.set_xlabel('Time (Months)', fontsize=12)
    ax1.set_ylabel('Demand / Capacity', color=color1, fontsize=12)
    ax1.plot(months, D_exp, color='blue', linestyle='--', label='Expected Demand ($D_{exp}$)')
    ax1.plot(months, S_cap, color='green', linestyle='-', label='Served Capacity ($S_{cap}$)')
    ax1.fill_between(months, S_cap, D_exp, where=(D_exp > S_cap), color='red', alpha=0.3, label='Unserved Demand')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.legend(loc='upper left')
    
    ax2 = ax1.twinx()
    color2 = 'tab:red'
    ax2.set_ylabel('Cumulative EDNS', color=color2, fontsize=12)
    ax2.plot(months, edns, color=color2, linewidth=2.5, label='EDNS(T)')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.legend(loc='lower right')
    
    plt.title('Expected Demand Not Served (EDNS) over 36 Months', fontsize=14, fontweight='bold')
    fig.tight_layout()
    
    out_path = os.path.join(FIG_DIR, "edns.png")
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    plot_edns()
