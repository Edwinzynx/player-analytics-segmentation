"""Compute baseline and chart inputs; all display values enter metrics.json."""
import numpy as np
from scipy.stats import skew
from common import update_metrics, ROOT, OUT, digest
from data_quality_checks import load_and_check

def main():
    df,report=load_and_check()
    df.to_csv(ROOT/'data/cookie_cats_cleaned.csv',index=False)
    rounds=df.sum_gamerounds
    both=int((df.retention_1.eq(1)&df.retention_7.eq(1)).sum())
    overall={'n':len(df),'total_rounds':int(rounds.sum()),'mean_rounds':float(rounds.mean()),
        'median_rounds':float(rounds.median()),'std_rounds':float(rounds.std()),
        'min_rounds':int(rounds.min()),'max_rounds':int(rounds.max()),
        'iqr':float(rounds.quantile(.75)-rounds.quantile(.25)),
        'quantiles':{str(q):float(rounds.quantile(q)) for q in [.25,.5,.75,.9,.99,.999]},
        'skew_rounds':float(skew(rounds)),'skew_log_rounds':float(skew(np.log1p(rounds))),
        'd1':float(df.retention_1.mean()),'d7':float(df.retention_7.mean()),
        'd1_n':int(df.retention_1.sum()),'d7_n':int(df.retention_7.sum()),
        'both_n':both,'d7_only_n':int((df.retention_1.eq(0)&df.retention_7.eq(1)).sum()),
        'd7_given_d1':both/int(df.retention_1.sum()),'zero_rounds':int(rounds.eq(0).sum())}
    hist,edges=np.histogram(np.log1p(rounds),bins=40)
    raw_hist,raw_edges=np.histogram(rounds,bins=40)
    update_metrics(overall=overall,distribution={'log_counts':hist.tolist(),'log_edges':edges.tolist(),
        'raw_counts':raw_hist.tolist(),'raw_edges':raw_edges.tolist()},
        data_contract={'observation_days':14,'retention_days':[1,7],
            'grain':'one player','source_sha256':report['raw_sha256'],
            'clean_sha256':digest(ROOT/'data/cookie_cats_cleaned.csv'),
            'tier_bounds':[0,5,15,50,150,500],'tier_upper_open':True,
            'cohort_labels':['none','D1 only','D7 only','both']})

if __name__=='__main__':
    main()

