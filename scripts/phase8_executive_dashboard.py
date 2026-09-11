"""
Phase 8: Final Visual Story & Executive Analytics Dashboard
Script: scripts/phase8_executive_dashboard.py

Generates a unified, publication-grade 6-to-8 panel Executive Analytics Dashboard
integrating the complete analytical narrative from raw gameplay distribution
to behavioral clustering, retention collapse, and A/B gate impact.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

def generate_executive_dashboard():
    # Style configuration
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
    plt.rcParams['axes.edgecolor'] = '#CCCCCC'
    plt.rcParams['axes.linewidth'] = 0.8
    
    # Load dataset with segments
    segments_path = os.path.join('data', 'player_segments.csv')
    if not os.path.exists(segments_path):
        raise FileNotFoundError(f"Missing {segments_path}. Run Phase 5 first.")
    
    df = pd.read_csv(segments_path)
    
    # Map retention columns if needed
    d1_col = 'retention_1_int' if 'retention_1_int' in df.columns else 'retention_1'
    d7_col = 'retention_7_int' if 'retention_7_int' in df.columns else 'retention_7'
    
    fig = plt.figure(figsize=(20, 14), dpi=300)
    fig.patch.set_facecolor('#F8F9FA')
    
    # Grid layout: 3 rows x 3 columns
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.38, wspace=0.28,
                           top=0.92, bottom=0.06, left=0.06, right=0.96)
    
    # Main Title & Subtitle
    fig.suptitle('EA Slingshot Studios | Player Telemetry & Behavioral Analytics Dashboard\n'
                 'End-to-End Retention Dynamics, K-Means Archetypes & Level Progression A/B Evaluation (N = 31,331)',
                 fontsize=16, fontweight='bold', color='#1A1A1A', y=0.97)
    
    # Segment naming map
    seg_names_full = [
        'Immediate Bouncers',
        'Day-0 Bingers (Unretained)',
        'Short-Term Adopters (D1 Only)',
        'Loyal Core Champions (D7 Retained)'
    ]
    seg_labels_short = ['Bouncers', 'D0 Bingers', 'Adopters', 'Champions']
    seg_colors = ['#8C92AC', '#F5A623', '#E74C3C', '#2ECC71']
    color_map = dict(zip(seg_names_full, seg_colors))
    
    # -------------------------------------------------------------
    # Panel 1: Gameplay Distribution (Raw vs Log1p)
    # -------------------------------------------------------------
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor('#FFFFFF')
    sns.histplot(df['log_gamerounds'], bins=35, kde=True, color='#2B5B84', ax=ax1, edgecolor='none', alpha=0.7)
    ax1.axvline(np.log1p(16), color='#E74C3C', linestyle='--', linewidth=1.5, label='Median = 16 rds')
    ax1.axvline(np.log1p(51.16), color='#F5A623', linestyle=':', linewidth=1.5, label='Mean = 51.2 rds')
    ax1.set_title('1. Engagement Distribution (Log-Transformed)', fontsize=11, fontweight='bold', color='#2B5B84', pad=8)
    ax1.set_xlabel('log1p(sum_gamerounds)', fontsize=9, fontweight='bold')
    ax1.set_ylabel('Player Count', fontsize=9, fontweight='bold')
    ax1.legend(loc='upper right', fontsize=8, frameon=True)
    ax1.grid(True, linestyle=':', alpha=0.6)
    
    # -------------------------------------------------------------
    # Panel 2: Overall Macro Retention Funnel
    # -------------------------------------------------------------
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor('#FFFFFF')
    d1_rate = df[d1_col].mean() * 100
    d7_rate = df[d7_col].mean() * 100
    stages = ['Install (D0)', 'Day 1 Return', 'Day 7 Return']
    values = [100.0, d1_rate, d7_rate]
    bars2 = ax2.bar(stages, values, color=['#2B5B84', '#3498DB', '#1ABC9C'], width=0.55, edgecolor='#333333', linewidth=0.8)
    for bar in bars2:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., h + 2, f'{h:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax2.set_ylim(0, 115)
    ax2.set_title('2. Macro Retention Funnel (D0 -> D1 -> D7)', fontsize=11, fontweight='bold', color='#2B5B84', pad=8)
    ax2.set_ylabel('Active Player Percentage (%)', fontsize=9, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.6)
    
    # -------------------------------------------------------------
    # Panel 3: A/B Gate Placement Impact (Gate 30 vs Gate 40)
    # -------------------------------------------------------------
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.set_facecolor('#FFFFFF')
    v_agg = df.groupby('version')[[d1_col, d7_col]].mean() * 100
    x3 = np.arange(2)
    w = 0.35
    b3_1 = ax3.bar(x3 - w/2, v_agg[d1_col], width=w, label='Day 1', color='#4A90E2', edgecolor='#333333', linewidth=0.8)
    b3_2 = ax3.bar(x3 + w/2, v_agg[d7_col], width=w, label='Day 7', color='#E67E22', edgecolor='#333333', linewidth=0.8)
    ax3.set_xticks(x3)
    ax3.set_xticklabels(['Gate 30 (N=15,621)', 'Gate 40 (N=15,710)'], fontsize=9, fontweight='bold')
    ax3.set_ylim(0, 55)
    for bar in b3_1:
        ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1, f'{bar.get_height():.2f}%', ha='center', va='bottom', fontsize=8, fontweight='bold')
    for bar in b3_2:
        ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1, f'{bar.get_height():.2f}%', ha='center', va='bottom', fontsize=8, fontweight='bold', color='#B94A00')
    ax3.set_title('3. Progression Gate A/B Impact', fontsize=11, fontweight='bold', color='#2B5B84', pad=8)
    ax3.set_ylabel('Retention Rate (%)', fontsize=9, fontweight='bold')
    ax3.legend(loc='upper right', fontsize=8, frameon=True)
    ax3.grid(True, linestyle=':', alpha=0.6)
    
    # -------------------------------------------------------------
    # Panel 4: Population Share by Segment (Donut Chart)
    # -------------------------------------------------------------
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.set_facecolor('#FFFFFF')
    seg_counts = df['segment_name'].value_counts()[seg_names_full]
    donut_colors = [color_map[s] for s in seg_counts.index]
    wedges, texts, autotexts = ax4.pie(seg_counts, labels=None, autopct='%1.1f%%', startangle=140,
                                       colors=donut_colors, pctdistance=0.75,
                                       wedgeprops=dict(width=0.45, edgecolor='#FFFFFF', linewidth=2))
    for at in autotexts:
        at.set_color('#FFFFFF')
        at.set_fontweight('bold')
        at.set_fontsize(9)
    ax4.set_title('4. Player Population by Segment', fontsize=11, fontweight='bold', color='#2B5B84', pad=8)
    ax4.legend(wedges, seg_labels_short, loc='center', fontsize=8, frameon=False)
    
    # -------------------------------------------------------------
    # Panel 5: Segment Retention Trajectories (D1 vs D7)
    # -------------------------------------------------------------
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.set_facecolor('#FFFFFF')
    seg_ret = df.groupby('segment_name')[[d1_col, d7_col]].mean().loc[seg_names_full] * 100
    x5 = np.arange(4)
    w5 = 0.35
    b5_1 = ax5.bar(x5 - w5/2, seg_ret[d1_col], width=w5, label='Day 1', color='#3498DB', edgecolor='#333333', linewidth=0.8)
    b5_2 = ax5.bar(x5 + w5/2, seg_ret[d7_col], width=w5, label='Day 7', color='#2ECC71', edgecolor='#333333', linewidth=0.8)
    ax5.set_xticks(x5)
    ax5.set_xticklabels(seg_labels_short, fontsize=8.5, fontweight='bold')
    ax5.set_ylim(0, 115)
    for bar in b5_1:
        if bar.get_height() > 0:
            ax5.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1.5, f'{bar.get_height():.1f}%', ha='center', va='bottom', fontsize=7.5, fontweight='bold')
    for bar in b5_2:
        if bar.get_height() > 0:
            ax5.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1.5, f'{bar.get_height():.1f}%', ha='center', va='bottom', fontsize=7.5, fontweight='bold', color='#196F3D')
    ax5.set_title('5. Segment Retention: D1 vs D7 Cliff', fontsize=11, fontweight='bold', color='#2B5B84', pad=8)
    ax5.set_ylabel('Retention Rate (%)', fontsize=9, fontweight='bold')
    ax5.legend(loc='upper left', fontsize=8, frameon=True)
    ax5.grid(True, linestyle=':', alpha=0.6)
    
    # -------------------------------------------------------------
    # Panel 6: Gameplay Volume Share Disproportion (The 80/20 Rule)
    # -------------------------------------------------------------
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.set_facecolor('#FFFFFF')
    vol_share = (df.groupby('segment_name')['sum_gamerounds'].sum() / df['sum_gamerounds'].sum() * 100).loc[seg_names_full]
    pop_share = (df['segment_name'].value_counts(normalize=True) * 100).loc[seg_names_full]
    x6 = np.arange(4)
    w6 = 0.35
    ax6.bar(x6 - w6/2, pop_share, width=w6, label='% of Players', color='#BDC3C7', edgecolor='#333333', linewidth=0.8)
    bars_vol = ax6.bar(x6 + w6/2, vol_share, width=w6, label='% of Total Rounds', color=[color_map[s] for s in vol_share.index], edgecolor='#333333', linewidth=0.8)
    ax6.set_xticks(x6)
    ax6.set_xticklabels(seg_labels_short, fontsize=8.5, fontweight='bold')
    ax6.set_ylim(0, 70)
    for bar in bars_vol:
        ax6.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1, f'{bar.get_height():.1f}%', ha='center', va='bottom', fontsize=8, fontweight='bold')
    ax6.set_title('6. Volume Disproportion (Champions = 59%)', fontsize=11, fontweight='bold', color='#2B5B84', pad=8)
    ax6.set_ylabel('Percentage Share (%)', fontsize=9, fontweight='bold')
    ax6.legend(loc='upper left', fontsize=8, frameon=True)
    ax6.grid(True, linestyle=':', alpha=0.6)
    
    # -------------------------------------------------------------
    # Panel 7: Engagement Tier vs D7 Retention Residuals (Chi-Square)
    # -------------------------------------------------------------
    ax7 = fig.add_subplot(gs[2, 0])
    ax7.set_facecolor('#FFFFFF')
    tiers = ['0', '1-5', '6-15', '16-50', '51-150', '151-500', '500+']
    ret_rates = [0.73, 1.35, 4.11, 13.44, 42.48, 77.47, 95.68]
    ax7.plot(tiers, ret_rates, marker='o', color='#8E44AD', linewidth=2.5, markersize=6)
    for i, r in enumerate(ret_rates):
        ax7.text(i, r + 4, f'{r:.1f}%', ha='center', va='bottom', fontsize=7.5, fontweight='bold', color='#5B2C6F')
    ax7.set_title('7. D7 Retention by Engagement (Chi2 p<1e-16)', fontsize=11, fontweight='bold', color='#2B5B84', pad=8)
    ax7.set_xlabel('Gameplay Rounds Tier', fontsize=9, fontweight='bold')
    ax7.set_ylabel('D7 Retention Rate (%)', fontsize=9, fontweight='bold')
    ax7.set_ylim(-5, 110)
    ax7.grid(True, linestyle=':', alpha=0.6)
    
    # -------------------------------------------------------------
    # Panel 8: Non-Parametric Bootstrap Posterior Lift Distribution
    # -------------------------------------------------------------
    ax8 = fig.add_subplot(gs[2, 1])
    ax8.set_facecolor('#FFFFFF')
    np.random.seed(42)
    g30_d7 = df[df['version'] == 'gate_30'][d7_col].values
    g40_d7 = df[df['version'] == 'gate_40'][d7_col].values
    boot_diffs = []
    for _ in range(1000):
        b30 = np.random.choice(g30_d7, size=len(g30_d7), replace=True).mean()
        b40 = np.random.choice(g40_d7, size=len(g40_d7), replace=True).mean()
        boot_diffs.append((b30 - b40) * 100)
    boot_diffs = np.array(boot_diffs)
    
    sns.histplot(boot_diffs, bins=30, kde=True, color='#16A085', ax=ax8, edgecolor='none', alpha=0.7)
    ax8.axvline(0, color='#C0392B', linestyle='--', linewidth=1.8, label='Zero Lift')
    ax8.axvline(boot_diffs.mean(), color='#2980B9', linestyle='-', linewidth=1.8, label=f'Mean = +{boot_diffs.mean():.2f}%')
    ax8.set_title('8. Bootstrap D7 Lift (95.1% Prob Gate 30 Win)', fontsize=11, fontweight='bold', color='#2B5B84', pad=8)
    ax8.set_xlabel('Day 7 Retention Difference (% pts)', fontsize=9, fontweight='bold')
    ax8.set_ylabel('Bootstrap Density', fontsize=9, fontweight='bold')
    ax8.legend(loc='upper right', fontsize=8, frameon=True)
    ax8.grid(True, linestyle=':', alpha=0.6)
    
    # -------------------------------------------------------------
    # Panel 9: Strategic Product Action Matrix (Summary Box)
    # -------------------------------------------------------------
    ax9 = fig.add_subplot(gs[2, 2])
    ax9.set_facecolor('#FFFFFF')
    ax9.axis('off')
    
    summary_text = (
        "EXECUTIVE PRODUCT TAKEAWAYS:\n\n"
        "1. ROLLBACK TO GATE 30:\n"
        "   Gate 40 caused a 0.73% pt D7 drop\n"
        "   and lost 95 Core Champions (-3.2%).\n\n"
        "2. TARGET SHORT-TERM ADOPTERS (30.0%):\n"
        "   High initial engagement (49.7 rds),\n"
        "   100% D1 return, but 0% D7 retention.\n"
        "   Prime target for D3-D5 streak mechanics.\n\n"
        "3. PROTECT CORE CHAMPIONS (18.6%):\n"
        "   Generate 59.0% of all rounds played.\n"
        "   Maintain level progression flow.\n\n"
        "4. DAY-0 FATIGUE INTERVENTION:\n"
        "   23.7% play 22.5 rds in D0, 0% return.\n"
        "   Introduce session pacing prompts."
    )
    
    ax9.text(0.05, 0.95, summary_text, transform=ax9.transAxes, fontsize=9.5,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round,pad=0.8', facecolor='#EBF5FB', edgecolor='#3498DB', linewidth=1.5))
    
    output_path = os.path.join('outputs', 'figures', '15_executive_analytics_dashboard.png')
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    
    print(f"[Phase 8 SUCCESS] Executive Analytics Dashboard saved to {output_path}")

if __name__ == '__main__':
    generate_executive_dashboard()
