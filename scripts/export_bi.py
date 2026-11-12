"""Tidy fact/dimensions and aggregate snapshots with manifest lineage."""
import pandas as pd
from common import ROOT, OUT, metrics, load_players, update_metrics, digest, TIERS, COHORTS

def main():
    m=metrics(); df=load_players(); dest=OUT/'bi'; dest.mkdir(exist_ok=True)
    tables={'fact_players':df[['userid','version','sum_gamerounds','retention_1','retention_7','tier_id','tier','cohort','cohort_tier','decile','secondary_segment']],
        'dim_tier':pd.DataFrame({'tier_id':range(len(TIERS)),'tier':TIERS}),
        'dim_cohort':pd.DataFrame({'cohort':COHORTS,'cohort_order':range(len(COHORTS)),
            'retention_1':[0,1,0,1],'retention_7':[0,0,1,1]}),
        'dim_decile':pd.DataFrame({'decile':range(1,11),'direction':['highest rounds first']*10})}
    for key,rows in m['profiles'].items():
        tables['aggregate_'+key]=pd.DataFrame(rows)
    tables['aggregate_segment_version']=pd.DataFrame(m['sql']['segment_version'])
    tables['ab_statistics']=pd.DataFrame([{k:v for k,v in r.items() if not isinstance(v,list)}|{'metric':name,
        'ci_low':r['ci95'][0],'ci_high':r['ci95'][1],
        'bootstrap_ci_low':r['bootstrap_ci95'][0],'bootstrap_ci_high':r['bootstrap_ci95'][1]}
        for name,r in m['ab'].items()])
    manifest={}
    for name,table in tables.items():
        path=dest/(name+'.csv'); table.to_csv(path,index=False)
        manifest[name]={'rows':len(table),'sha256':digest(path),'columns':list(table.columns),
            'metric_source':('profiles/'+name.removeprefix('aggregate_') if name.startswith('aggregate_') else
                'ab' if name=='ab_statistics' else 'data_contract + accepted player artifact')}
    update_metrics(bi={'files':manifest,'fact_source_sha256':digest(ROOT/'data/player_segments.csv'),
        'validation_totals':{'players':len(df),'rounds':int(df.sum_gamerounds.sum()),
            'd1_n':int(df.retention_1.sum()),'d7_n':int(df.retention_7.sum())},
        'dax_engine_validation':'not executed: Power BI/Tabular engine unavailable'})

if __name__=='__main__':
    main()

