import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from scipy.stats import skew

# Configure visual styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 300

os.makedirs('data', exist_ok=True)
os.makedirs('outputs/figures', exist_ok=True)

print("="*75)
print("PHASE 4: BEHAVIORAL FEATURE ENGINEERING & MATRIX CONSTRUCTION")
print("="*75)

# 1. Load cleaned player dataset
df = pd.read_csv('data/cookie_cats_cleaned.csv')
total_players = len(df)
print(f"Loaded {total_players:,} cleaned player records.")

# 2. Skewness Analysis & Log Transformation
raw_skew = skew(df['sum_gamerounds'])
df['log_gamerounds'] = np.log1p(df['sum_gamerounds'])
log_skew = skew(df['log_gamerounds'])

print(f"\n1. Engagement Distribution Skewness:")
print(f"   - Raw sum_gamerounds skewness: {raw_skew:.2f} (Extreme right skew)")
print(f"   - Log1p(sum_gamerounds) skewness: {log_skew:.2f} (Near-symmetric / stabilized)")
print(f"   - Raw range: [{df['sum_gamerounds'].min()} to {df['sum_gamerounds'].max():,}]")
print(f"   - Log1p range: [{df['log_gamerounds'].min():.2f} to {df['log_gamerounds'].max():.2f}]")

# 3. Behavioral Feature Engineering
# Feature A: D1 Retention (int 0/1)
df['retention_1_int'] = df['retention_1'].astype(int)

# Feature B: D7 Retention (int 0/1)
df['retention_7_int'] = df['retention_7'].astype(int)

# Feature C: Composite Retention Score (0 to 3)
# 0: Neither D1 nor D7 (Churned immediately)
# 1: D1 only (Early trial, quick drop-off)
# 2: D7 only (Delayed re-engagement/resurrection)
# 3: Both D1 and D7 (Consistent high-loyalty player)
df['retention_score'] = df['retention_1_int'] * 1 + df['retention_7_int'] * 2

# Feature D: Engagement Intensity Ratio (gamerounds relative to median)
df['rounds_to_median_ratio'] = df['sum_gamerounds'] / df['sum_gamerounds'].median()

# Feature E: Retention Consistency Flag (Binary: Retained at both milestones)
df['retained_both'] = (df['retention_1'] & df['retention_7']).astype(int)

# Feature F: Ordinal Engagement Tier Code (0 to 6)
tier_bins = [-1, 0, 5, 15, 50, 150, 500, float('inf')]
df['engagement_tier_code'] = pd.cut(df['sum_gamerounds'], bins=tier_bins, labels=False)

# 4. Feature Correlation Matrix
cluster_feature_cols = ['log_gamerounds', 'retention_1_int', 'retention_7_int', 'retention_score']
corr_matrix = df[cluster_feature_cols].corr()

print("\n2. Feature Correlation Matrix:")
print(corr_matrix.round(3).to_string())

# 5. Feature Scaling (Standardization: Mean=0, Std=1)
scaler = StandardScaler()
scaled_features = scaler.fit_transform(df[cluster_feature_cols])
scaled_df = pd.DataFrame(scaled_features, columns=[f"{col}_scaled" for col in cluster_feature_cols])

# Combine engineered features with player identifiers
final_features_df = pd.concat([
    df[['userid', 'version', 'sum_gamerounds', 'log_gamerounds', 'retention_1_int', 'retention_7_int', 'retention_score', 'engagement_tier_code']],
    scaled_df
], axis=1)

final_features_df.to_csv('data/player_features.csv', index=False)
print(f"\n[OK] Saved final engineered feature matrix to data/player_features.csv ({final_features_df.shape[0]:,} rows, {final_features_df.shape[1]} cols)")

# 6. Generate Skewness & Log-Transformation Comparison Chart
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

# Raw histogram with extreme power tail
sns.histplot(df['sum_gamerounds'], bins=50, ax=ax1, color='#c0392b', kde=False)
ax1.set_title(f"Raw Gameplay Rounds (Skewness = +{raw_skew:.2f})", fontsize=12, fontweight='bold')
ax1.set_xlabel("sum_gamerounds (Unbounded & Extreme Outliers)", fontsize=10)
ax1.set_ylabel("Player Volume", fontsize=10)
ax1.set_xlim(0, 500)  # Zoom in to show the heavy zero/low peak
ax1.annotate("Severe Power-Law Skew\n(Top players at 2,961 rounds)", xy=(150, 3000), xytext=(220, 6000),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1.2, headwidth=6),
             fontsize=10, bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.3))

# Log-transformed distribution
sns.histplot(df['log_gamerounds'], bins=40, ax=ax2, color='#2980b9', kde=True)
ax2.set_title(f"Log1p Transformed Rounds (Skewness = {log_skew:.2f})", fontsize=12, fontweight='bold')
ax2.set_xlabel("log1p(sum_gamerounds) = ln(rounds + 1)", fontsize=10)
ax2.set_ylabel("Player Volume", fontsize=10)
ax2.axvline(df['log_gamerounds'].median(), color='#e67e22', linestyle='--', linewidth=2, label=f"Median: {df['log_gamerounds'].median():.2f}")
ax2.axvline(df['log_gamerounds'].mean(), color='#27ae60', linestyle='-', linewidth=2, label=f"Mean: {df['log_gamerounds'].mean():.2f}")
ax2.legend(frameon=True, facecolor='white', fontsize=10)

plt.suptitle("Feature Engineering: Resolving Severe Skewness for Distance-Based Clustering", fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
fig5_path = 'outputs/figures/05_skewness_and_log_transformation.png'
plt.savefig(fig5_path)
plt.close()
print(f"[OK] Generated visualization: {fig5_path}")

# 7. Print Feature Summary Table for Checkpoint 4
print("\n" + "="*75)
print("FEATURE SUMMARY MATRIX TABLE")
print("="*75)
feature_table = pd.DataFrame({
    'Feature': ['log_gamerounds', 'retention_1_int', 'retention_7_int', 'retention_score', 'sum_gamerounds', 'version'],
    'Meaning': [
        'Log-transformed total gameplay rounds in first 14 days (ln(rounds + 1))',
        'Day 1 player return binary indicator (1 = returned, 0 = did not return)',
        'Day 7 player return binary indicator (1 = returned, 0 = did not return)',
        'Composite longitudinal retention score (0: Churned, 1: D1 only, 2: D7 only, 3: Both D1&D7)',
        'Raw cumulative game rounds played across tracking window',
        'A/B test experimental progression gate cohort (gate_30 vs gate_40)'
    ],
    'Data Type': ['Float64', 'Int64 (Binary)', 'Int64 (Binary)', 'Int64 (Ordinal 0-3)', 'Int64 (Count)', 'Categorical / String'],
    'Transformation': [
        'np.log1p() + StandardScaler (Z-score)',
        'StandardScaler (Z-score)',
        'StandardScaler (Z-score)',
        'StandardScaler (Z-score)',
        'Unscaled (Kept for business profiling)',
        'Categorical (Reserved for cohort cross-tabulation)'
    ],
    'Reason for Inclusion': [
        'Captures player engagement magnitude while normalizing power-law skew for Euclidean distance.',
        'Captures immediate Day 1 onboarding conversion and short-term hook.',
        'Captures sustainable week-1 habituation and long-term retention.',
        'Synthesizes full retention trajectory into a single directional loyalty gradient.',
        'Provides intuitive business metric for segment profiling and interpretation.',
        'Allows measuring how experimental gate versions distribute across discovered behavioral segments.'
    ]
})

print(feature_table[['Feature', 'Data Type', 'Transformation']].to_string(index=False))
print("\n" + "="*75)
print("PHASE 4 COMPLETE")
print("="*75)
