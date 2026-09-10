import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configure visual styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 300

os.makedirs('outputs/figures', exist_ok=True)
os.makedirs('data', exist_ok=True)

print("="*75)
print("PHASE 6: IN-DEPTH SEGMENT RETENTION & PRODUCT DYNAMICS ANALYSIS")
print("="*75)

# 1. Load segmented dataset
df = pd.read_csv('data/player_segments.csv')
total_players = len(df)
grand_total_rounds = df['sum_gamerounds'].sum()

print(f"Total Analyzed Players: {total_players:,}")
print(f"Total Cumulative Game Rounds: {grand_total_rounds:,}")

# 2. Segment Comprehensive Metrics
segment_summary = df.groupby('segment_name').agg(
    player_count=('userid', 'count'),
    pct_of_players=('userid', lambda x: len(x) / total_players * 100),
    total_rounds_generated=('sum_gamerounds', 'sum'),
    mean_rounds=('sum_gamerounds', 'mean'),
    median_rounds=('sum_gamerounds', 'median'),
    std_rounds=('sum_gamerounds', 'std'),
    iqr_rounds=('sum_gamerounds', lambda x: x.quantile(0.75) - x.quantile(0.25)),
    d1_retention_pct=('retention_1_int', lambda x: x.mean() * 100),
    d7_retention_pct=('retention_7_int', lambda x: x.mean() * 100),
    both_retained_pct=('retention_score', lambda x: (x == 3).mean() * 100)
).reset_index()

segment_summary['pct_of_total_rounds'] = (segment_summary['total_rounds_generated'] / grand_total_rounds) * 100
segment_summary = segment_summary.sort_values(by='mean_rounds', ascending=True)

print("\n" + "="*75)
print("COMPREHENSIVE SEGMENT RETENTION & ENGAGEMENT METRICS")
print("="*75)
cols_to_print = ['segment_name', 'player_count', 'pct_of_players', 'pct_of_total_rounds', 'mean_rounds', 'median_rounds', 'd1_retention_pct', 'd7_retention_pct']
print(segment_summary[cols_to_print].round(2).to_string(index=False))

# 3. A/B Variant (Gate 30 vs Gate 40) Distribution Within Segments
ab_segment_summary = df.groupby(['segment_name', 'version']).agg(
    player_count=('userid', 'count'),
    mean_rounds=('sum_gamerounds', 'mean'),
    median_rounds=('sum_gamerounds', 'median')
).reset_index()

ab_pivot = ab_segment_summary.pivot(index='segment_name', columns='version', values=['player_count', 'mean_rounds'])
print("\n" + "="*75)
print("A/B VARIANT (GATE 30 VS GATE 40) BREAKDOWN BY SEGMENT")
print("="*75)
print(ab_pivot.round(2))

# -------------------------------------------------------------
# VISUALIZATIONS
# -------------------------------------------------------------

# Chart 1: Segment Retention Funnel (D1 vs D7) with Population Share
fig, ax = plt.subplots(figsize=(11, 6))
x = np.arange(len(segment_summary))
width = 0.35

rects1 = ax.bar(x - width/2, segment_summary['d1_retention_pct'], width, label='Day 1 Retention (%)', color='#2980b9', edgecolor='black', linewidth=0.7)
rects2 = ax.bar(x + width/2, segment_summary['d7_retention_pct'], width, label='Day 7 Retention (%)', color='#27ae60', edgecolor='black', linewidth=0.7)

for rect in rects1:
    h = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2., h + 1.2, f"{h:.1f}%", ha='center', va='bottom', fontsize=9.5, fontweight='bold')

for rect in rects2:
    h = rect.get_height()
    ax.text(rect.get_x() + rect.get_width()/2., h + 1.2, f"{h:.1f}%", ha='center', va='bottom', fontsize=9.5, fontweight='bold')

ax.set_xticks(x)
ax.set_xticklabels(segment_summary['segment_name'], rotation=15, ha='right', fontsize=11, fontweight='bold')
ax.set_ylabel("Retention Rate (%)", fontsize=12)
ax.set_ylim(0, 115)
ax.set_title("Retention Trajectory (D1 vs D7) Across Behavioral Player Segments", fontsize=14, fontweight='bold', pad=15)
ax.legend(frameon=True, facecolor='white', fontsize=10, loc='upper left')

# Annotations highlighting key product findings
ax.annotate("Catastrophic Retention Drop:\n100% D1 -> 0% D7 (30.0% of Players)",
            xy=(2, 50), xytext=(1.3, 75),
            arrowprops=dict(facecolor='#c0392b', shrink=0.08, width=1.5, headwidth=7),
            fontsize=9.5, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="#f9ebea", ec="#c0392b", alpha=0.9))

plt.tight_layout()
fig9_path = 'outputs/figures/09_segment_retention_comparison.png'
plt.savefig(fig9_path)
plt.close()
print(f"\n[OK] Generated {fig9_path}")

# Chart 2: Gameplay Engagement Boxplot / Violin Plot by Segment (Log Scale)
fig, ax = plt.subplots(figsize=(11, 6))
order = segment_summary['segment_name'].tolist()
palette = ["#c0392b", "#e67e22", "#2980b9", "#27ae60"]

sns.boxplot(data=df, x='segment_name', y='sum_gamerounds', order=order, palette=palette, ax=ax, showfliers=False, width=0.5)
sns.stripplot(data=df.sample(2000, random_state=42), x='segment_name', y='sum_gamerounds', order=order, color='black', alpha=0.15, jitter=0.2, size=3, ax=ax)

ax.set_yscale('log')
ax.set_title("Gameplay Intensity Distribution Across Player Segments (Log Scale)", fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel("Behavioral Segment", fontsize=11, fontweight='bold')
ax.set_ylabel("Game Rounds Played (Log Scale)", fontsize=11, fontweight='bold')
ax.set_xticklabels(order, rotation=15, ha='right', fontsize=11)

plt.tight_layout()
fig10_path = 'outputs/figures/10_segment_engagement_distribution.png'
plt.savefig(fig10_path)
plt.close()
print(f"[OK] Generated {fig10_path}")

# Chart 3: Population Share vs Gameplay Volume Share (Power Law in Segments)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

colors = ['#c0392b', '#e67e22', '#2980b9', '#27ae60']

# Population Pie/Donut
wedges1, texts1, autotexts1 = ax1.pie(
    segment_summary['pct_of_players'], labels=segment_summary['segment_name'], autopct='%1.1f%%',
    startangle=140, colors=colors, pctdistance=0.75, wedgeprops=dict(width=0.45, edgecolor='black')
)
ax1.set_title("Player Population Share (% of Users)", fontsize=13, fontweight='bold')

# Volume Pie/Donut
wedges2, texts2, autotexts2 = ax2.pie(
    segment_summary['pct_of_total_rounds'], labels=segment_summary['segment_name'], autopct='%1.1f%%',
    startangle=140, colors=colors, pctdistance=0.75, wedgeprops=dict(width=0.45, edgecolor='black')
)
ax2.set_title("Total Gameplay Volume Share (% of Rounds)", fontsize=13, fontweight='bold')

for autotext in autotexts1 + autotexts2:
    autotext.set_fontsize(10)
    autotext.set_fontweight('bold')

plt.suptitle("The Gameplay Value Disproportion: Population Share vs Total Rounds Generated", fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
fig11_path = 'outputs/figures/11_gameplay_volume_share_by_segment.png'
plt.savefig(fig11_path)
plt.close()
print(f"[OK] Generated {fig11_path}")

# Chart 4: A/B Test Gate Impact Across Segments
fig, ax = plt.subplots(figsize=(11, 5.5))
ab_counts = df.groupby(['segment_name', 'version']).size().unstack()
ab_pcts = (ab_counts.T / ab_counts.sum(axis=1)).T * 100

ab_pcts.plot(kind='bar', stacked=False, color=['#1f77b4', '#ff7f0e'], ax=ax, edgecolor='black', linewidth=0.7, width=0.6)
ax.set_title("A/B Test Cohort Distribution (Gate 30 vs Gate 40) Across Player Segments", fontsize=13, fontweight='bold', pad=15)
ax.set_ylabel("Share Within Segment (%)", fontsize=11)
ax.set_xlabel("Behavioral Segment", fontsize=11, fontweight='bold')
ax.set_ylim(0, 60)
ax.axhline(50, color='gray', linestyle='--', linewidth=1, label='Expected 50/50 Split')
ax.set_xticklabels(ab_pcts.index, rotation=15, ha='right', fontsize=10.5)
ax.legend(title="Version Cohort", frameon=True, facecolor='white', fontsize=10)

for p in ax.patches:
    h = p.get_height()
    if h > 0:
        ax.annotate(f"{h:.1f}%", (p.get_x() + p.get_width() / 2., h + 0.8),
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
fig12_path = 'outputs/figures/12_segment_ab_gate_impact.png'
plt.savefig(fig12_path)
plt.close()
print(f"[OK] Generated {fig12_path}")

print("\n" + "="*75)
print("PHASE 6 COMPLETE")
print("="*75)
