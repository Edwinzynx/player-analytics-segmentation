"""All figures read chart inputs and results from metrics.json, never literals."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from common import metrics,OUT,TIERS,COHORTS
from report_statistics import main as statistics_figures

FILES={1:'01_gamerounds_distribution.png',2:'02_d1_vs_d7_retention.png',
3:'03_retention_by_version.png',4:'04_engagement_vs_retention_buckets.png',
5:'05_skewness_and_log_transformation.png',6:'06_kmeans_elbow_and_silhouette.png',
7:'07_cluster_profiles.png',8:'08_cluster_scatter_pca.png',
9:'09_segment_retention_comparison.png',10:'10_segment_engagement_distribution.png',
11:'11_gameplay_volume_share_by_segment.png',12:'12_segment_ab_gate_impact.png',
15:'15_executive_analytics_dashboard.png'}

def save(fig,n):
    fig.tight_layout()
    fig.savefig(OUT/'figures'/FILES[n],dpi=160,facecolor='white')
    plt.close(fig)

def retention(ax,rows,key,title):
    labels=[r[key] for r in rows]; x=np.arange(len(rows))
    ax.bar(x-.18,[100*r['d1'] for r in rows],.36,label='D1',color='#376a91')
    ax.bar(x+.18,[100*r['d7'] for r in rows],.36,label='D7',color='#c48537')
    ax.set_xticks(x,labels,rotation=20,ha='right')
    ax.set(title=title,ylabel='Observed retention (%)',ylim=(0,105))
    ax.legend()

def main():
    m=metrics(); o=m['overall']; d=m['distribution']
    p=m['profiles']; tiers=sorted(p['tier'],key=lambda r:TIERS.index(r['tier']))
    cohorts=sorted(p['cohort'],key=lambda r:COHORTS.index(r['cohort']))
    (OUT/'figures').mkdir(exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(9,5))
    ax.stairs(d['log_counts'],d['log_edges'],fill=True,color='#376a91')
    ax.set(title='Activity distribution (zero-round players included)',xlabel='log(1 + total rounds)',ylabel='Players')
    save(fig,1)
    fig,ax=plt.subplots(figsize=(7,4))
    vals=[o['d1'],o['d7']]
    bars=ax.bar(['D1','D7'],np.array(vals)*100,color=['#376a91','#c48537'])
    ax.bar_label(bars,labels=[f'{v:.2%}' for v in vals],padding=4)
    ax.set(title='Marginal return rates: not a survival curve',ylabel='Players retained (%)',ylim=(0,60))
    save(fig,2)
    for n,rows,key,title in [(3,p['version'],'version','Assigned-version comparison'),
        (4,tiers,'tier','Concurrent engagement and retention: association'),
        (9,cohorts,'cohort','Primary rule cohorts: retention defined by membership')]:
        fig,ax=plt.subplots(figsize=(10,5)); retention(ax,rows,key,title); save(fig,n)
    fig,axes=plt.subplots(1,2,figsize=(11,4))
    for ax,prefix,sk in [(axes[0],'raw',o['skew_rounds']),(axes[1],'log',o['skew_log_rounds'])]:
        ax.stairs(d[prefix+'_counts'],d[prefix+'_edges'],fill=True,color='#376a91')
        ax.set(title=f'{prefix.title()} rounds, skewness {sk:.3f}',ylabel='Players',
            xlabel='Rounds' if prefix=='raw' else 'log(1 + rounds)')
    save(fig,5)
    e=m['segmentation']['evaluations']; fig,axes=plt.subplots(1,2,figsize=(11,4))
    for ax,col in zip(axes,['inertia','silhouette']):
        ax.plot([r['k'] for r in e],[r[col] for r in e],marker='o')
        ax.set(xlabel='Clusters',ylabel=col,title='Secondary model diagnostics')
        ax.axvline(m['segmentation']['selected_k'],ls=':',color='#c48537',label='Fixed legacy comparison')
        ax.legend()
    save(fig,6)
    fig,axes=plt.subplots(1,2,figsize=(11,4))
    k=p['secondary_segment']; labels=[r['secondary_segment'] for r in k]
    axes[0].bar(labels,[100*r['size_share'] for r in k],color='#376a91')
    axes[0].set(title='Secondary K-means size',ylabel='Players (%)')
    axes[1].bar(labels,[r['mean_rounds'] for r in k],color='#c48537')
    axes[1].set(title='Secondary K-means activity',ylabel='Mean rounds')
    fig.suptitle('Descriptive model using retention features; not predictive validation')
    save(fig,7)
    fig,ax=plt.subplots(figsize=(9,5))
    sample=m['segmentation']['pca_sample']
    for label in labels:
        points=[r for r in sample if r['segment']==label]
        ax.scatter([r['x'] for r in points],[r['y'] for r in points],s=9,alpha=.4,label=label)
    variance=m['segmentation']['pca_explained_variance']
    ax.set(title='PCA of secondary model features (retention included)',
        xlabel=f'PC1 ({variance[0]:.1%} variance)',ylabel=f'PC2 ({variance[1]:.1%} variance)')
    ax.legend(); save(fig,8)
    fig,ax=plt.subplots(figsize=(9,5))
    ax.bxp([{'label':r['cohort'],'med':r['median_rounds'],'q1':r['rounds_q25'],
        'q3':r['rounds_q75'],'whislo':r['rounds_q5'],'whishi':r['rounds_q95']} for r in cohorts],showfliers=False)
    ax.set_yscale('symlog',linthresh=1)
    ax.set(title='Cohort activity: median, IQR and central percentile range',
        ylabel='Rounds (symmetric log scale; zero retained)')
    save(fig,10)
    fig,ax=plt.subplots(figsize=(9,5)); x=np.arange(len(cohorts))
    ax.bar(x-.18,[100*r['size_share'] for r in cohorts],.36,label='Players')
    ax.bar(x+.18,[100*r['rounds_share'] for r in cohorts],.36,label='Rounds')
    ax.set_xticks(x,[r['cohort'] for r in cohorts]); ax.set(ylabel='Share (%)',title='Primary cohort size and activity contribution')
    ax.legend(); save(fig,11)
    fig,ax=plt.subplots(figsize=(10,5))
    delta=np.array([r['d7_gate_difference'] for r in tiers])*100
    lo=np.array([r['d7_ci_low'] for r in tiers])*100
    hi=np.array([r['d7_ci_high'] for r in tiers])*100
    ax.errorbar(range(len(tiers)),delta,yerr=np.array([delta-lo,hi-delta]),fmt='o',capsize=4)
    ax.axhline(0,color='gray',ls='--'); ax.set_xticks(range(len(tiers)),[r['tier'] for r in tiers])
    ax.set(title='Within-tier D7 contrasts: post-assignment, descriptive only',
        ylabel='Gate 40 - Gate 30 (pp), marginal CI',xlabel='Engagement tier')
    save(fig,12)
    statistics_figures()
    fig,axes=plt.subplots(2,2,figsize=(14,10))
    retention(axes[0,0],p['version'],'version','Observed version retention')
    x=np.arange(len(cohorts))
    axes[0,1].bar(x,[100*r['size_share'] for r in cohorts],color='#376a91')
    axes[0,1].set_xticks(x,[r['cohort'] for r in cohorts])
    axes[0,1].set(title='Primary retention patterns',ylabel='Players (%)')
    dec=p['decile']
    axes[1,0].bar([r['decile'] for r in dec],[100*r['rounds_share'] for r in dec],color='#376a91')
    axes[1,0].plot([r['decile'] for r in dec],[100*r['cumulative_rounds_share'] for r in dec],color='#c48537',marker='o')
    axes[1,0].set(title='Activity concentration',xlabel='Decile, highest rounds first',ylabel='Rounds share / cumulative (%)')
    axes[1,1].axis('off'); a=m['ab']['D7']
    text=(f"Accepted players: {o['n']:,}\n\n"
        f"D7 difference: {100*a['difference']:+.3f} pp\n"
        f"CI: [{100*a['ci95'][0]:+.3f}, {100*a['ci95'][1]:+.3f}] pp\n"
        f"Two-sided p: {a['p_two_sided']:.5f}\nHolm p: {a['p_holm']:.5f}\n\n"
        f"{a['conclusion'].capitalize()}.\n\n"
        "Next: recover the full experiment and validate assignment.\n"
        "Truncated source; no revenue or session timestamps.\n"
        "Rule cohorts are descriptive, not prospective targets.")
    axes[1,1].text(.02,.94,text,va='top',fontsize=12,linespacing=1.5)
    fig.suptitle('Product retention and activity analysis',fontsize=17)
    save(fig,15)

if __name__=='__main__':
    main()

