import pandas as pd
from common import metrics,OUT,digest

def test_bi_manifest_and_totals():
    m=metrics()
    for name,item in m['bi']['files'].items():
        path=OUT/'bi'/f'{name}.csv'
        assert digest(path)==item['sha256']
        assert len(pd.read_csv(path))==item['rows']
    fact=pd.read_csv(OUT/'bi/fact_players.csv')
    assert fact.userid.is_unique
    assert len(fact)==m['overall']['n']
    assert fact.sum_gamerounds.sum()==m['overall']['total_rounds']
    assert fact.retention_1.sum()==m['overall']['d1_n']
    assert fact.retention_7.sum()==m['overall']['d7_n']
    for col,file in [('tier_id','dim_tier'),('cohort','dim_cohort'),('decile','dim_decile')]:
        dim=pd.read_csv(OUT/'bi'/f'{file}.csv')
        assert dim[col].is_unique
        assert set(fact[col])<=set(dim[col])

