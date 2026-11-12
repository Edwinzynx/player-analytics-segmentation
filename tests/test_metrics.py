import numpy as np
import pytest
from scipy.stats import chi2_contingency
from common import metrics,load_players,features,ROOT
from phase7_statistical_testing import analyze,difference
from phase5_player_segmentation import segment
import pandas as pd

def test_statistical_reproducibility():
    m=metrics(); result=analyze(load_players())
    for section in ['ab','association','srm','analysis_plan']:
        assert result[section]==m[section]
    for r in result['ab'].values():
        assert r['p_two_sided']==pytest.approx(r['chi_p_two_sided'])
        assert r['p_one_sided_gate40_lower']==pytest.approx(r['chi_directional_p_gate40_lower'])
        assert r['ci95'][0]<=r['difference']<=r['ci95'][1]
        assert r['odds_ci95'][0]<=r['odds_ratio']<=r['odds_ci95'][1]
        assert r['p_holm']>=r['p_two_sided']

def test_secondary_model_reproducibility():
    df=features(pd.read_csv(ROOT/'data/cookie_cats_cleaned.csv'))
    result,details=segment(df)
    assert result.secondary_segment.tolist()==load_players().secondary_segment.tolist()
    assert details['ari_cohort']==pytest.approx(metrics()['segmentation']['ari_cohort'],abs=1e-12)

def test_rule_cohorts_and_boundaries():
    rounds=[0,1,5,6,15,16,50,51,150,151,500,501]
    df=pd.DataFrame({'userid':range(len(rounds)),'sum_gamerounds':rounds,
        'retention_1':[0,1,0,1]*3,'retention_7':[0,0,1,1]*3})
    got=features(df)
    assert got.tier_id.tolist()==[0,1,1,2,2,3,3,4,4,5,5,6]
    assert got.cohort.tolist()==['none','D1 only','D7 only','both']*3
    assert len(set(got.decile))==10

def test_boundary_cis_are_not_false_certainty():
    assert difference(0,20,0,20)['ci95'][0]<0<difference(0,20,0,20)['ci95'][1]
    assert difference(20,20,20,20)['ci95'][0]<0<difference(20,20,20,20)['ci95'][1]
    assert difference(0,0,1,2)['difference'] is None

def test_profiles_reconcile_and_retention_is_defined():
    m=metrics()
    for key,rows in m['profiles'].items():
        assert sum(r['n'] for r in rows)==m['overall']['n']
        assert sum(r['rounds'] for r in rows)==m['overall']['total_rounds']
        assert sum(r['size_share'] for r in rows)==pytest.approx(1)
    for r in m['profiles']['cohort']:
        assert r['d1']==int(r['cohort'] in ['D1 only','both'])
        assert r['d7']==int(r['cohort'] in ['D7 only','both'])

