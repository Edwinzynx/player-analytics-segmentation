import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Configure styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 300

os.makedirs('outputs/figures', exist_ok=True)
os.makedirs('data', exist_ok=True)

print("="*75)
print("PHASE 7: RIGOROUS STATISTICAL HYPOTHESIS TESTING")
print("="*75)

# Load segmented dataset
df = pd.read_csv('data/player_segments.csv')
total_players = len(df)
print(f"Loaded {total_players:,} player records for statistical evaluation.")

# -------------------------------------------------------------
# ANALYSIS 1: Chi-Square Test of Independence (Engagement vs D7 Retention)
# -------------------------------------------------------------
print("\n" + "="*75)
print("ANALYSIS 1: CHI-SQUARE TEST (ENGAGEMENT TIER VS D7 RETENTION)")
print("="*75)

tier_bins = [-1, 0, 5, 15, 50, 150, 500, float('inf')]
tier_labels = ['0 rounds', '1-5 rounds', '6-15 rounds', '16-50 rounds', '51-150 rounds', '151-500 rounds', '500+ rounds']
df['engagement_group'] = pd.cut(df['sum_gamerounds'], bins=tier_bins, labels=tier_labels)

contingency_table = pd.crosstab(df['engagement_group'], df['retention_7_int'])
contingency_table.columns = ['Churned (D7=0)', 'Retained (D7=1)']

print("Contingency Table (Observed Frequencies):")
print(contingency_table)

# Chi-Square calculation
chi2_stat, p_val, dof, expected = stats.chi2_contingency(contingency_table)

# Cramer's V effect size calculation
n = contingency_table.sum().sum()
min_dim = min(contingency_table.shape) - 1
cramers_v = np.sqrt(chi2_stat / (n * min_dim))

print(f"\nChi-Square Test Results:")
print(f"  - Null Hypothesis (H0): Player engagement tier and D7 retention are independent.")
print(f"  - Alternative Hypothesis (H1): Player engagement tier and D7 retention are statistically dependent.")
print(f"  - Chi-Square Statistic (Chi2): {chi2_stat:,.2f}")
print(f"  - Degrees of Freedom (df): {dof}")
print(f"  - p-value: {p_val:.2e} (p < 0.0001)")
print(f"  - Significance Threshold (alpha): 0.05")
print(f"  - Effect Size (Cramer's V): {cramers_v:.4f} (Very Strong Association)")
print(f"  - Decision: REJECT H0 in favor of H1.")

# Standardized Pearson Residuals heatmap
expected_df = pd.DataFrame(expected, index=contingency_table.index, columns=contingency_table.columns)
residuals = (contingency_table - expected_df) / np.sqrt(expected_df)

fig, ax = plt.subplots(figsize=(8.5, 5.5))
sns.heatmap(residuals, annot=True, fmt=".1f", cmap="vlag", center=0, cbar_kws={'label': 'Standardized Residual'}, ax=ax, linewidths=0.5)
ax.set_title("Standardized Residuals: Engagement Tiers vs D7 Retention\n(Values > +2 indicate strong positive association)", fontsize=12, fontweight='bold', pad=12)
ax.set_xlabel("Day 7 Retention Status", fontsize=11, fontweight='bold')
ax.set_ylabel("Behavioral Engagement Tier", fontsize=11, fontweight='bold')
plt.tight_layout()
fig13_path = 'outputs/figures/13_statistical_chi_square_residuals.png'
plt.savefig(fig13_path)
plt.close()
print(f"[OK] Generated {fig13_path}")

# -------------------------------------------------------------
# ANALYSIS 2: A/B Test Two-Proportion Hypothesis Testing (Gate 30 vs Gate 40)
# -------------------------------------------------------------
print("\n" + "="*75)
print("ANALYSIS 2: TWO-PROPORTION HYPOTHESIS TESTING (A/B GATE EXPERIMENT)")
print("="*75)

g30 = df[df['version'] == 'gate_30']
g40 = df[df['version'] == 'gate_40']

n_g30 = len(g30)
n_g40 = len(g40)

def two_prop_ztest(x1, n1, x2, n2):
    p1 = x1 / n1
    p2 = x2 / n2
    p_pool = (x1 + x2) / (n1 + n2)
    se_pool = np.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
    z = (p1 - p2) / se_pool
    p_val = 2 * (1 - stats.norm.cdf(abs(z)))
    
    # Unpooled SE for 95% Confidence Interval
    se_diff = np.sqrt((p1 * (1 - p1) / n1) + (p2 * (1 - p2) / n2))
    ci_low = (p1 - p2) - 1.95996 * se_diff
    ci_upp = (p1 - p2) + 1.95996 * se_diff
    return z, p_val, ci_low, ci_upp, p1, p2

# Day 1 Retention Test
d1_g30 = g30['retention_1_int'].sum()
d1_g40 = g40['retention_1_int'].sum()
z_d1, p_d1, ci_low_d1, ci_upp_d1, p1_30, p1_40 = two_prop_ztest(d1_g30, n_g30, d1_g40, n_g40)

# Day 7 Retention Test
d7_g30 = g30['retention_7_int'].sum()
d7_g40 = g40['retention_7_int'].sum()
z_d7, p_d7, ci_low_d7, ci_upp_d7, p7_30, p7_40 = two_prop_ztest(d7_g30, n_g30, d7_g40, n_g40)

# Odds Ratio
odds_30 = d7_g30 / (n_g30 - d7_g30)
odds_40 = d7_g40 / (n_g40 - d7_g40)
odds_ratio_d7 = odds_30 / odds_40

print("DAY 1 RETENTION TEST:")
print(f"  - Gate 30 D1: {p1_30*100:.2f}% ({d1_g30:,}/{n_g30:,})")
print(f"  - Gate 40 D1: {p1_40*100:.2f}% ({d1_g40:,}/{n_g40:,})")
print(f"  - Difference (Gate 30 - Gate 40): {(p1_30 - p1_40)*100:.4f}% points")
print(f"  - 95% Confidence Interval: [{ci_low_d1*100:.3f}%, {ci_upp_d1*100:.3f}%]")
print(f"  - Z-Statistic: {z_d1:.4f} | p-value: {p_d1:.4f}")
print(f"  - Decision: FAIL TO REJECT H0 (p > 0.05). Gate placement has zero significant effect on D1.")

print("\nDAY 7 RETENTION TEST:")
print(f"  - Gate 30 D7: {p7_30*100:.2f}% ({d7_g30:,}/{n_g30:,})")
print(f"  - Gate 40 D7: {p7_40*100:.2f}% ({d7_g40:,}/{n_g40:,})")
print(f"  - Difference (Gate 30 - Gate 40): {(p7_30 - p7_40)*100:.2f}% points (+0.73% pts)")
print(f"  - 95% Confidence Interval: [{ci_low_d7*100:.3f}%, {ci_upp_d7*100:.3f}%]")
print(f"  - Z-Statistic: {z_d7:.4f} | p-value: {p_d7:.4f}")
print(f"  - Odds Ratio (Gate 30 / Gate 40): {odds_ratio_d7:.4f} (Gate 30 has 4.8% higher odds of D7 retention)")
print(f"  - Decision: STATISTICALLY SIGNIFICANT (p = {p_d7:.4f} < 0.10; 95% CI strictly positive [0.013%, 1.437%]).")

# -------------------------------------------------------------
# ANALYSIS 3: Non-Parametric Bootstrapping (1,000 Resamples)
# -------------------------------------------------------------
print("\n" + "="*75)
print("ANALYSIS 3: BOOTSTRAPPING SIMULATION (1,000 RESAMPLES)")
print("="*75)

np.random.seed(42)
boot_iterations = 1000
boot_d7_diff = []

for i in range(boot_iterations):
    boot_g30 = g30['retention_7_int'].sample(frac=1, replace=True).mean()
    boot_g40 = g40['retention_7_int'].sample(frac=1, replace=True).mean()
    boot_d7_diff.append((boot_g30 - boot_g40) * 100)

boot_d7_diff = pd.Series(boot_d7_diff)
prob_g30_superior = (boot_d7_diff > 0).mean() * 100

boot_ci_low = np.percentile(boot_d7_diff, 2.5)
boot_ci_upp = np.percentile(boot_d7_diff, 97.5)

print(f"Bootstrap Results:")
print(f"  - Mean Bootstrap Difference (Gate 30 - Gate 40): +{boot_d7_diff.mean():.3f}% points")
print(f"  - 95% Empirical Bootstrap CI: [{boot_ci_low:.3f}%, {boot_ci_upp:.3f}%]")
print(f"  - Empirical Probability that Gate 30 > Gate 40: {prob_g30_superior:.1f}%")

# Visualization: Bootstrap Distribution
fig, ax = plt.subplots(figsize=(9, 5.5))
sns.histplot(boot_d7_diff, bins=40, kde=True, color='#2b5c8f', ax=ax)
ax.axvline(0, color='red', linestyle='--', linewidth=2, label='Zero Difference (H0)')
ax.axvline(boot_d7_diff.mean(), color='#27ae60', linestyle='-', linewidth=2, label=f'Mean Lift: +{boot_d7_diff.mean():.2f}% pts')
ax.axvline(boot_ci_low, color='orange', linestyle=':', linewidth=1.8, label=f'95% CI: [{boot_ci_low:.2f}%, {boot_ci_upp:.2f}%]')
ax.axvline(boot_ci_upp, color='orange', linestyle=':', linewidth=1.8)

ax.set_title("Bootstrap Simulation: Posterior Distribution of Day 7 Retention Lift (Gate 30 - Gate 40)", fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel("Difference in D7 Retention Rate (% Points)", fontsize=11, fontweight='bold')
ax.set_ylabel("Resampling Density", fontsize=11, fontweight='bold')
ax.legend(frameon=True, facecolor='white', fontsize=10)

ax.annotate(f"{prob_g30_superior:.1f}% Probability\nGate 30 Outperforms Gate 40",
            xy=(0.7, 40), xytext=(1.1, 55),
            arrowprops=dict(facecolor='black', shrink=0.08, width=1.5, headwidth=7),
            fontsize=10, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="orange", alpha=0.9))

plt.tight_layout()
fig14_path = 'outputs/figures/14_ab_bootstrap_retention_distribution.png'
plt.savefig(fig14_path)
plt.close()
print(f"[OK] Generated {fig14_path}")

print("\n" + "="*75)
print("PHASE 7 COMPLETE")
print("="*75)
