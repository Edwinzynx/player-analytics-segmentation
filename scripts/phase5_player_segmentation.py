import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.decomposition import PCA

# Configure visual styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 300

os.makedirs('outputs/figures', exist_ok=True)
os.makedirs('data', exist_ok=True)

print("="*75)
print("PHASE 5: REFINED UNSUPERVISED PLAYER SEGMENTATION (K-MEANS)")
print("="*75)

# 1. Load engineered features
df = pd.read_csv('data/player_features.csv')
feature_cols = ['log_gamerounds_scaled', 'retention_1_int_scaled', 'retention_7_int_scaled', 'retention_score_scaled']
X = df[feature_cols].values

# 2. Evaluate K values from K=2 to K=7
k_range = list(range(2, 8))
inertias = []
silhouette_scores = []
calinski_scores = []
davies_bouldin_scores = []

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10, max_iter=300)
    labels = kmeans.fit_predict(X)
    
    wcss = kmeans.inertia_
    sil = silhouette_score(X, labels, sample_size=10000, random_state=42)
    ch = calinski_harabasz_score(X, labels)
    db = davies_bouldin_score(X, labels)
    
    inertias.append(wcss)
    silhouette_scores.append(sil)
    calinski_scores.append(ch)
    davies_bouldin_scores.append(db)

# 3. Plot Elbow and Silhouette Evaluation
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

# Elbow Plot (Inertia)
ax1.plot(k_range, inertias, marker='o', linewidth=2.5, markersize=8, color='#2980b9')
ax1.set_title("Elbow Method: Inertia (WCSS) vs K", fontsize=13, fontweight='bold')
ax1.set_xlabel("Number of Clusters (K)", fontsize=11)
ax1.set_ylabel("Within-Cluster Sum of Squares (Inertia)", fontsize=11)
ax1.set_xticks(k_range)
ax1.grid(True, linestyle='--', alpha=0.6)

# Silhouette Plot
ax2.plot(k_range, silhouette_scores, marker='s', linewidth=2.5, markersize=8, color='#e74c3c')
ax2.set_title("Silhouette Score vs K (Cluster Cohesion & Separation)", fontsize=13, fontweight='bold')
ax2.set_xlabel("Number of Clusters (K)", fontsize=11)
ax2.set_ylabel("Average Silhouette Coefficient", fontsize=11)
ax2.set_xticks(k_range)
ax2.grid(True, linestyle='--', alpha=0.6)

plt.suptitle("K-Means Model Selection: Elbow Curve & Silhouette Analysis", fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
fig6_path = 'outputs/figures/06_kmeans_elbow_and_silhouette.png'
plt.savefig(fig6_path)
plt.close()
print(f"[OK] Generated {fig6_path}")

# 4. Train Final K-Means with K=4
selected_k = 4
final_kmeans = KMeans(n_clusters=selected_k, random_state=42, n_init=20, max_iter=500)
df['cluster_id'] = final_kmeans.fit_predict(X)

# 5. Distinct Segment Naming Based on Empirical Behavioral Signatures
def assign_segment_name(row):
    # Cluster 0: Low rounds (2.5), 0% D1, 0% D7
    # Cluster 3: Moderate rounds (22.5), 0% D1, 0% D7 (Day-0 binge, dropped out)
    # Cluster 2: Moderate-high rounds (49.7), 100% D1, 0% D7 (Short-term adopter)
    # Cluster 1: High rounds (162.1), 78.8% D1, 100% D7 (Loyal Core Champions)
    c = row['cluster_id']
    if c == 0:
        return "Immediate Bouncers"
    elif c == 3:
        return "Day-0 Bingers (Unretained)"
    elif c == 2:
        return "Short-Term Adopters (D1 Only)"
    elif c == 1:
        return "Loyal Core Champions (D7 Retained)"
    return f"Cluster {c}"

df['segment_name'] = df.apply(assign_segment_name, axis=1)

# Save segmented dataset
df.to_csv('data/player_segments.csv', index=False)
print(f"[OK] Saved segmented data to data/player_segments.csv")

# 6. Final Segment Profile Table
profile_final = df.groupby(['cluster_id', 'segment_name']).agg(
    player_count=('userid', 'count'),
    pct_players=('userid', lambda x: len(x) / len(df) * 100),
    mean_rounds=('sum_gamerounds', 'mean'),
    median_rounds=('sum_gamerounds', 'median'),
    d1_retention=('retention_1_int', lambda x: x.mean() * 100),
    d7_retention=('retention_7_int', lambda x: x.mean() * 100),
    both_retained=('retention_score', lambda x: (x == 3).mean() * 100)
).reset_index().sort_values(by='mean_rounds', ascending=True)

print("\n" + "="*75)
print("FINAL PLAYER SEGMENT PROFILES")
print("="*75)
print(profile_final.round(2).to_string(index=False))

# 7. Generate Segment Profile Comparison Chart
fig, ax = plt.subplots(figsize=(12, 6))

x = np.arange(len(profile_final))
width = 0.22

rects1 = ax.bar(x - width*1.5, profile_final['pct_players'], width, label='% of Player Base', color='#7f8c8d', edgecolor='black', linewidth=0.7)
rects2 = ax.bar(x - width*0.5, profile_final['mean_rounds'], width, label='Mean Game Rounds', color='#f39c12', edgecolor='black', linewidth=0.7)
rects3 = ax.bar(x + width*0.5, profile_final['d1_retention'], width, label='Day 1 Retention (%)', color='#2980b9', edgecolor='black', linewidth=0.7)
rects4 = ax.bar(x + width*1.5, profile_final['d7_retention'], width, label='Day 7 Retention (%)', color='#27ae60', edgecolor='black', linewidth=0.7)

for rects in [rects1, rects2, rects3, rects4]:
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., h + 1.2, f"{h:.1f}", ha='center', va='bottom', fontsize=8.5, fontweight='bold')

ax.set_xticks(x)
ax.set_xticklabels(profile_final['segment_name'], rotation=15, ha='right', fontsize=11, fontweight='bold')
ax.set_ylabel("Metric Value / Percentage", fontsize=12)
ax.set_ylim(0, 190)
ax.set_title("Behavioral Player Archetypes: Engagement, Retention & Population Share", fontsize=14, fontweight='bold', pad=15)
ax.legend(frameon=True, facecolor='white', fontsize=10, loc='upper left')

plt.tight_layout()
fig7_path = 'outputs/figures/07_cluster_profiles.png'
plt.savefig(fig7_path)
plt.close()
print(f"[OK] Generated {fig7_path}")

# 8. 2D PCA Visualization of Clusters
pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X)
df['pca_1'] = X_pca[:, 0]
df['pca_2'] = X_pca[:, 1]

fig, ax = plt.subplots(figsize=(10, 6.5))
palette = {
    "Immediate Bouncers": "#c0392b",
    "Day-0 Bingers (Unretained)": "#e67e22",
    "Short-Term Adopters (D1 Only)": "#2980b9",
    "Loyal Core Champions (D7 Retained)": "#27ae60"
}

df_sample = df.sample(n=min(5000, len(df)), random_state=42)
sns.scatterplot(
    data=df_sample, x='pca_1', y='pca_2', hue='segment_name', palette=palette,
    alpha=0.6, s=25, ax=ax, edgecolor='none'
)

ax.set_title(f"2D PCA Projection of Behavioral Player Clusters (Variance Explained: {pca.explained_variance_ratio_.sum()*100:.1f}%)", fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel(f"Principal Component 1 ({pca.explained_variance_ratio_[0]*100:.1f}% Variance)", fontsize=11)
ax.set_ylabel(f"Principal Component 2 ({pca.explained_variance_ratio_[1]*100:.1f}% Variance)", fontsize=11)
ax.legend(title="Behavioral Segment", frameon=True, facecolor='white', framealpha=0.9, fontsize=10)

plt.tight_layout()
fig8_path = 'outputs/figures/08_cluster_scatter_pca.png'
plt.savefig(fig8_path)
plt.close()
print(f"[OK] Generated {fig8_path}")

print("\n" + "="*75)
print("PHASE 5 COMPLETED SUCCESSFULLY")
print("="*75)
