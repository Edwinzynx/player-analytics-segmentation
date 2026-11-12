"""Primary rule cohorts; secondary fixed legacy K-means with leakage disclosed."""
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import adjusted_rand_score, silhouette_score
from threadpoolctl import threadpool_limits
from common import ROOT, SEED, update_metrics

def segment(df):
    cols = ['log_gamerounds','retention_1','retention_7','retention_score']
    x = StandardScaler().fit_transform(df[cols])
    evaluations = []
    with threadpool_limits(limits=1):
        for k in range(2,8):
            model = KMeans(n_clusters=k,random_state=SEED,n_init=20,max_iter=500)
            labels = model.fit_predict(x)
            evaluations.append({'k':k,'inertia':float(model.inertia_),
                'silhouette':float(silhouette_score(x,labels,sample_size=min(3000,len(df)),random_state=SEED))})
            if k == 4:
                final_labels = labels.copy()
    df = df.copy()
    df['cluster_id'] = final_labels
    ordered = df.groupby('cluster_id').sum_gamerounds.mean().sort_values().index
    df['secondary_segment'] = df.cluster_id.map({c:f'K{i+1}' for i,c in enumerate(ordered)})
    df['segment_name'] = df.cohort
    return df, {'selected_k':4,'selection_reason':'legacy comparability, not claimed optimal',
        'evaluations':evaluations,'features':cols,'silhouette_sample_size':min(3000,len(df)),
        'ari_cohort':float(adjusted_rand_score(df.cohort,final_labels)),
        'ari_cohort_tier':float(adjusted_rand_score(df.cohort_tier,final_labels)),
        'limitation':'Retention flags and their composite enter the model. Retention profiles are partly true by construction; unsuitable for prospective prediction.'}

def main():
    df,result = segment(pd.read_csv(ROOT/'data/player_features.csv',keep_default_na=False))
    df.to_csv(ROOT/'data/player_segments.csv',index=False)
    update_metrics(segmentation=result)

if __name__ == '__main__':
    main()

