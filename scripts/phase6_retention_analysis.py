"""Profiles and post-treatment comparisons, explicitly noncausal."""
from common import load_players, simple_profile, records, update_metrics, OUT
from phase7_statistical_testing import difference

def profiles(df,key):
    rows = records(simple_profile(df,key))
    for row in rows:
        g = df[df[key].eq(row[key])]
        row['min_rounds']=int(g.sum_gamerounds.min())
        row['max_rounds']=int(g.sum_gamerounds.max())
        for q in [.05,.25,.75,.95]:
            row['rounds_q'+str(int(q*100))] = float(g.sum_gamerounds.quantile(q))
        a,b = g[g.version.eq('gate_30')],g[g.version.eq('gate_40')]
        row['gate30_n'],row['gate40_n'] = len(a),len(b)
        row['gate30_mean_rounds']=float(a.sum_gamerounds.mean()) if len(a) else None
        row['gate40_mean_rounds']=float(b.sum_gamerounds.mean()) if len(b) else None
        row['gate30_share'],row['gate40_share'] = len(a)/len(g),len(b)/len(g)
        for name,col in [('d1','retention_1'),('d7','retention_7')]:
            effect = difference(int(a[col].sum()),len(a),int(b[col].sum()),len(b))
            row[name+'_gate_difference'] = effect['difference']
            row[name+'_ci_low'],row[name+'_ci_high'] = effect['ci95']
        row['effect_interpretation'] = 'descriptive only: post-treatment selection; no subgroup causal inference'
    return rows

def main():
    df = load_players()
    p = {key:profiles(df,key) for key in ['cohort','cohort_tier','secondary_segment','tier','version','decile']}
    cumulative = 0
    for row in p['decile']:
        cumulative += row['rounds_share']
        row['cumulative_rounds_share'] = cumulative
    update_metrics(profiles=p)
    import pandas as pd
    (OUT/'tables').mkdir(exist_ok=True)
    for key,rows in p.items():
        pd.DataFrame(rows).to_csv(OUT/'tables'/f'{key}_profiles.csv',index=False)
if __name__ == '__main__':
    main()

