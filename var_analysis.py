# =============================================================
# A.1  Libraries and Data Setup
# =============================================================
import numpy as np

# Parameters
np.random.seed(42)

n_days = 1512
W = 1000000

# Nifty 50 parameters
mu = 0.001011      # 0.1011% daily return
sigma = 0.012676   # 1.2676% daily volatility

# Generate simulated returns
returns = np.random.normal(mu, sigma, n_days)


# =============================================================
# A.2  Historical Simulation VaR and ES
# =============================================================

# Historical VaR 95%
h95 = -np.percentile(returns, 5)
h95_money = h95 * W

# Historical VaR 99%
h99 = -np.percentile(returns, 1)
h99_money = h99 * W

# Historical ES 95%
h_es95_money = -returns[returns < -h95].mean() * W

# Historical ES 99%
h_es99_money = -returns[returns < -h99].mean() * W

# 10-day scaling
h95_10 = h95_money * np.sqrt(10)
h99_10 = h99_money * np.sqrt(10)

print("\nHistorical VaR")
print("95% 1-day  :", round(h95_money))
print("95% 10-day :", round(h95_10))
print("99% 1-day  :", round(h99_money))
print("99% 10-day :", round(h99_10))

print("\nHistorical Expected Shortfall")
print("ES 95%     :", round(h_es95_money))
print("ES 99%     :", round(h_es99_money))


# =============================================================
# A.3  Parametric VaR and ES
# =============================================================
from scipy import stats

# Z values
z95 = 1.6449
z99 = 2.3263

# Parametric VaR
p95 = (z95 * sigma - mu) * W
p99 = (z99 * sigma - mu) * W

# Parametric ES
p_es95 = (stats.norm.pdf(z95) / 0.05 * sigma - mu) * W
p_es99 = (stats.norm.pdf(z99) / 0.01 * sigma - mu) * W

# 10-day scaling
p95_10 = p95 * np.sqrt(10)
p99_10 = p99 * np.sqrt(10)

print("\nParametric VaR")
print("95% 1-day  :", round(p95))
print("95% 10-day :", round(p95_10))
print("99% 1-day  :", round(p99))
print("99% 10-day :", round(p99_10))

print("\nParametric Expected Shortfall")
print("ES 95%     :", round(p_es95))
print("ES 99%     :", round(p_es99))


# =============================================================
# A.4  Backtesting (Rolling 252-day Window)
# =============================================================

window = 252

h95_breach = 0
h99_breach = 0
p95_breach = 0
p99_breach = 0

for i in range(window, len(returns)):
    sample = returns[i-window:i]

    loss = max(-returns[i] * W, 0)

    h95_var = -np.percentile(sample, 5) * W
    h99_var = -np.percentile(sample, 1) * W

    mu_window = sample.mean()
    sigma_window = sample.std()

    p95_var = (1.6449 * sigma_window - mu_window) * W
    p99_var = (2.3263 * sigma_window - mu_window) * W

    if loss > h95_var:
        h95_breach += 1
    if loss > h99_var:
        h99_breach += 1
    if loss > p95_var:
        p95_breach += 1
    if loss > p99_var:
        p99_breach += 1

obs = len(returns) - window

print("\nBacktesting Results")
print("Observations:", obs)
print("Historical 95%:", h95_breach, f"({h95_breach/obs*100:.2f}%)")
print("Historical 99%:", h99_breach, f"({h99_breach/obs*100:.2f}%)")
print("Parametric 95%:", p95_breach, f"({p95_breach/obs*100:.2f}%)")
print("Parametric 99%:", p99_breach, f"({p99_breach/obs*100:.2f}%)")


# =============================================================
# A.5  Visualizations
# =============================================================
import matplotlib.pyplot as plt

# --- Plot 1: Return Distribution with VaR and ES ---
plt.figure(figsize=(10, 5))
plt.hist(returns * W, bins=60, color='steelblue', edgecolor='white', alpha=0.7)
plt.axvline(-h95_money, color='orange', linewidth=2, label=f'Historical VaR 95% (₹{round(h95_money):,})')
plt.axvline(-h99_money, color='red', linewidth=2, label=f'Historical VaR 99% (₹{round(h99_money):,})')
plt.axvline(-h_es95_money, color='orange', linewidth=2, linestyle='--', label=f'Historical ES 95% (₹{round(h_es95_money):,})')
plt.axvline(-h_es99_money, color='red', linewidth=2, linestyle='--', label=f'Historical ES 99% (₹{round(h_es99_money):,})')
plt.title('Portfolio Daily P&L Distribution with VaR and ES')
plt.xlabel('Daily P&L (₹)')
plt.ylabel('Frequency')
plt.legend()
plt.tight_layout()
plt.savefig('d:/python/market_risk_analysis/plot1_distribution.png', dpi=150)
plt.show()
print("Plot 1 saved.")

# --- Plot 2: Backtesting — Actual Losses vs Rolling VaR ---
actual_losses = []
rolling_h95 = []

for i in range(window, len(returns)):
    sample = returns[i-window:i]
    actual_losses.append(max(-returns[i] * W, 0))
    rolling_h95.append(-np.percentile(sample, 5) * W)

plt.figure(figsize=(12, 5))
plt.plot(actual_losses, color='steelblue', alpha=0.5, linewidth=0.8, label='Actual Daily Loss')
plt.plot(rolling_h95, color='orange', linewidth=1.5, label='Rolling Historical VaR 95%')

breaches = [i for i in range(len(actual_losses)) if actual_losses[i] > rolling_h95[i]]
plt.scatter(breaches, [actual_losses[i] for i in breaches], color='red', s=15, zorder=5, label=f'Breaches ({len(breaches)})')

plt.title('Backtesting: Actual Losses vs Rolling Historical VaR 95%')
plt.xlabel('Trading Day')
plt.ylabel('Loss (₹)')
plt.legend()
plt.tight_layout()
plt.savefig('d:/python/market_risk_analysis/plot2_backtesting.png', dpi=150)
plt.show()
print("Plot 2 saved.")
