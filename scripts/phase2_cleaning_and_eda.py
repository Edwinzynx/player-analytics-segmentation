import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configure visual aesthetics
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300

os.makedirs('outputs/figures', exist_ok=True)
os.makedirs('data', exist_ok=True)

# -------------------------------------------------------------
# 1. DATA CLEANING
# -------------------------------------------------------------
print("="*60)
print("PHASE 2: DATA CLEANING & EXPLORATORY ANALYSIS")
print("="*60)

raw_df = pd.read_csv('data/cookie_cats.csv')
initial_count = len(raw_df)
print(f"Initial raw player count: {initial_count:,}")

# Step 1: Filter out corrupted records (missing values / invalid version strings)
# In our audit, row with version 'gate_4' contained NaNs across retention and gamerounds.
valid_versions = ['gate_30', 'gate_40']
cleaned_df = raw_df[raw_df['version'].isin(valid_versions)].copy()
cleaned_df = cleaned_df.dropna(subset=['sum_gamerounds', 'retention_1', 'retention_7'])

# Step 2: Ensure correct data types
cleaned_df['sum_gamerounds'] = cleaned_df['sum_gamerounds'].astype(int)
cleaned_df['retention_1'] = cleaned_df['retention_1'].astype(bool)
cleaned_df['retention_7'] = cleaned_df['retention_7'].astype(bool)

# Step 3: Outlier and domain validation check
# Check negative rounds
assert (cleaned_df['sum_gamerounds'] >= 0).all(), "Negative game rounds detected!"

# Check top percentiles of sum_gamerounds
p99_9 = cleaned_df['sum_gamerounds'].quantile(0.999)
max_rounds = cleaned_df['sum_gamerounds'].max()
print(f"Data Cleaning Summary:")
print(f" - Records removed: {initial_count - len(cleaned_df):,} corrupted/invalid record(s)")
print(f" - Cleaned player count: {len(cleaned_df):,}")
print(f" - 99.9th percentile of game rounds: {p99_9:.1f}")
print(f" - Maximum game rounds: {max_rounds:,}")

# Save cleaned dataset
cleaned_df.to_csv('data/cookie_cats_cleaned.csv', index=False)
print(f"[OK] Saved cleaned dataset to data/cookie_cats_cleaned.csv\n")

# -------------------------------------------------------------
# 2. KEY METRICS & EXPLORATORY ANALYSIS
# -------------------------------------------------------------
total_players = len(cleaned_df)
d1_overall = cleaned_df['retention_1'].mean() * 100
d7_overall = cleaned_df['retention_7'].mean() * 100
mean_rounds = cleaned_df['sum_gamerounds'].mean()
median_rounds = cleaned_df['sum_gamerounds'].median()
std_rounds = cleaned_df['sum_gamerounds'].std()
iqr_rounds = cleaned_df['sum_gamerounds'].quantile(0.75) - cleaned_df['sum_gamerounds'].quantile(0.25)

print("--- OVERALL METRICS ---")
print(f"Total Players: {total_players:,}")
print(f"Overall Day 1 Retention: {d1_overall:.2f}% ({cleaned_df['retention_1'].sum():,} players)")
print(f"Overall Day 7 Retention: {d7_overall:.2f}% ({cleaned_df['retention_7'].sum():,} players)")
print(f"Game Rounds - Mean: {mean_rounds:.2f} | Median: {median_rounds:.1f} | Std: {std_rounds:.2f} | IQR: {iqr_rounds:.1f}")

# Retention by game version
version_summary = cleaned_df.groupby('version').agg(
    player_count=('userid', 'count'),
    mean_rounds=('sum_gamerounds', 'mean'),
    median_rounds=('sum_gamerounds', 'median'),
    d1_retention_rate=('retention_1', 'mean'),
    d7_retention_rate=('retention_7', 'mean')
).reset_index()

version_summary['d1_retention_rate'] *= 100
version_summary['d7_retention_rate'] *= 100

print("\n--- RETENTION BY GAME VERSION (A/B TEST) ---")
print(version_summary.to_string(index=False))

# Create engagement buckets for granular behavioral exploration
bins = [-1, 0, 5, 15, 50, 150, 500, float('inf')]
labels = ['0 rounds (Churned)', '1-5 (Bouncer)', '6-15 (Light)', '16-50 (Core)', '51-150 (Engaged)', '151-500 (Heavy)', '500+ (Hardcore)']
cleaned_df['engagement_bucket'] = pd.cut(cleaned_df['sum_gamerounds'], bins=bins, labels=labels)

bucket_summary = cleaned_df.groupby('engagement_bucket', observed=False).agg(
    player_count=('userid', 'count'),
    pct_players=('userid', lambda x: len(x) / total_players * 100),
    d1_retention=('retention_1', lambda x: x.mean() * 100),
    d7_retention=('retention_7', lambda x: x.mean() * 100)
).reset_index()

print("\n--- BEHAVIORAL ENGAGEMENT BUCKETS ---")
print(bucket_summary.to_string(index=False))

# -------------------------------------------------------------
# 3. HIGH-RESOLUTION VISUALIZATIONS
# -------------------------------------------------------------
palette = {'gate_30': '#1f77b4', 'gate_40': '#ff7f0e'}

# Chart 1: Game Rounds Distribution (Log scale & Percentiles)
fig, ax = plt.subplots(figsize=(10, 5.5))
sns.histplot(cleaned_df['sum_gamerounds'], bins=60, kde=True, color='#2b5c8f', ax=ax, log_scale=(True, False))
ax.axvline(median_rounds, color='#d62728', linestyle='--', linewidth=2, label=f'Median: {median_rounds:.0f} rounds')
ax.axvline(mean_rounds, color='#2ca02c', linestyle='-', linewidth=2, label=f'Mean: {mean_rounds:.1f} rounds')
ax.axvline(cleaned_df['sum_gamerounds'].quantile(0.90), color='#9467bd', linestyle=':', linewidth=2, label=f'90th Pct: {cleaned_df["sum_gamerounds"].quantile(0.90):.0f} rounds')

ax.set_title("Distribution of Player Gameplay Rounds (Log-Scale X Axis)", fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel("Total Game Rounds Played (First 14 Days)", fontsize=12)
ax.set_ylabel("Player Count (Volume)", fontsize=12)
ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=11)
plt.tight_layout()
fig1_path = 'outputs/figures/01_gamerounds_distribution.png'
plt.savefig(fig1_path)
plt.close()
print(f"[OK] Generated {fig1_path}")

# Chart 2: Day 1 vs Day 7 Overall Retention Funnel Drop-off
fig, ax = plt.subplots(figsize=(8, 5.5))
ret_metrics = pd.DataFrame({
    'Stage': ['Day 1 Retention', 'Day 7 Retention'],
    'Retention_Rate': [d1_overall, d7_overall],
    'Drop': [0, d1_overall - d7_overall]
})
bars = ax.bar(ret_metrics['Stage'], ret_metrics['Retention_Rate'], color=['#337ab7', '#e74c3c'], width=0.45, edgecolor='black', linewidth=0.8)

for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 1.2, f'{yval:.2f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')

ax.set_ylim(0, 60)
ax.set_title("Overall Player Retention Benchmark (D1 vs D7)", fontsize=14, fontweight='bold', pad=15)
ax.set_ylabel("Retention Rate (%)", fontsize=12)
ax.annotate(f"D1 -> D7 Steep Drop-off:\n-{d1_overall - d7_overall:.2f}% points ({((d1_overall - d7_overall)/d1_overall)*100:.1f}% relative loss)",
            xy=(0.5, (d1_overall + d7_overall)/2), xytext=(0.55, 38),
            arrowprops=dict(facecolor='black', shrink=0.08, width=1.5, headwidth=8),
            fontsize=11, bbox=dict(boxstyle="round,pad=0.4", fc="yellow", alpha=0.3))
plt.tight_layout()
fig2_path = 'outputs/figures/02_d1_vs_d7_retention.png'
plt.savefig(fig2_path)
plt.close()
print(f"[OK] Generated {fig2_path}")

# Chart 3: Retention Comparison by Game Version (A/B Test Gate 30 vs Gate 40)
fig, ax = plt.subplots(figsize=(9, 5.5))
x = np.arange(2)
width = 0.35

g30_vals = [version_summary.loc[version_summary['version']=='gate_30', 'd1_retention_rate'].values[0],
            version_summary.loc[version_summary['version']=='gate_30', 'd7_retention_rate'].values[0]]
g40_vals = [version_summary.loc[version_summary['version']=='gate_40', 'd1_retention_rate'].values[0],
            version_summary.loc[version_summary['version']=='gate_40', 'd7_retention_rate'].values[0]]

rects1 = ax.bar(x - width/2, g30_vals, width, label='Gate 30 (Control)', color='#1f77b4', edgecolor='black', linewidth=0.8)
rects2 = ax.bar(x + width/2, g40_vals, width, label='Gate 40 (Test)', color='#ff7f0e', edgecolor='black', linewidth=0.8)

for rect in rects1:
    h = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2., h + 0.8, f"{h:.2f}%", ha='center', va='bottom', fontsize=11, fontweight='bold')

for rect in rects2:
    h = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2., h + 0.8, f"{h:.2f}%", ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_xticks(x)
ax.set_xticklabels(['Day 1 Retention', 'Day 7 Retention'], fontsize=12, fontweight='bold')
ax.set_ylim(0, 55)
ax.set_ylabel("Retention Rate (%)", fontsize=12)
ax.set_title("Retention Rate by Game Version (A/B Test: Gate 30 vs Gate 40)", fontsize=14, fontweight='bold', pad=15)
ax.legend(frameon=True, facecolor='white', fontsize=11)
plt.tight_layout()
fig3_path = 'outputs/figures/03_retention_by_version.png'
plt.savefig(fig3_path)
plt.close()
print(f"[OK] Generated {fig3_path}")

# Chart 4: Engagement Bucket vs Retention Rates
fig, ax1 = plt.subplots(figsize=(11, 6))

x_pos = np.arange(len(bucket_summary))
width = 0.35

rects1 = ax1.bar(x_pos - width/2, bucket_summary['d1_retention'], width, label='Day 1 Retention (%)', color='#2b5c8f', edgecolor='black', linewidth=0.6)
rects2 = ax1.bar(x_pos + width/2, bucket_summary['d7_retention'], width, label='Day 7 Retention (%)', color='#e67e22', edgecolor='black', linewidth=0.6)

for rect in rects1:
    h = rect.get_height()
    ax1.text(rect.get_x() + rect.get_width()/2., h + 1.0, f"{h:.1f}%", ha='center', va='bottom', fontsize=9, fontweight='bold')

for rect in rects2:
    h = rect.get_height()
    ax1.text(rect.get_x() + rect.get_width()/2., h + 1.0, f"{h:.1f}%", ha='center', va='bottom', fontsize=9, fontweight='bold')

ax1.set_xticks(x_pos)
ax1.set_xticklabels(bucket_summary['engagement_bucket'], rotation=25, ha='right', fontsize=10, fontweight='bold')
ax1.set_ylabel("Retention Rate (%)", fontsize=12)
ax1.set_ylim(0, 105)
ax1.set_title("Player Retention Scaling Across Behavioral Engagement Buckets", fontsize=14, fontweight='bold', pad=15)
ax1.legend(loc='upper left', frameon=True, facecolor='white', fontsize=11)

plt.tight_layout()
fig4_path = 'outputs/figures/04_engagement_vs_retention_buckets.png'
plt.savefig(fig4_path)
plt.close()
print(f"[OK] Generated {fig4_path}")
print("\n" + "="*60)
print("PHASE 2 COMPLETE")
print("="*60)
