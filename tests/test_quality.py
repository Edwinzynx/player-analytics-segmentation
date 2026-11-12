import pandas as pd
import pytest
from common import ROOT,metrics,digest
from data_quality_checks import validate,load_and_check

def valid():
    return pd.DataFrame({'userid':['1','2'],'version':['gate_30','gate_40'],
        'sum_gamerounds':['0','5'],'retention_1':['False','True'],'retention_7':['True','False']})

@pytest.mark.parametrize('column,value',[('userid','1.5'),('userid','-1'),
    ('version','gate_4'),('sum_gamerounds','-1'),('sum_gamerounds','3.5'),
    ('sum_gamerounds','inf'),('retention_1','false-ish'),('retention_7',None)])
def test_hard_rules(column,value):
    df=valid(); df.loc[0,column]=value
    assert validate(df)[0]

def test_duplicate_and_schema_fail():
    df=valid(); df.loc[1,'userid']='1'
    assert 'duplicate userid' in validate(df)[0]
    assert validate(df.drop(columns='version'))[0]
    df=valid(); df.loc[1,'userid']='01'
    assert 'duplicate userid after integer normalization' in validate(df)[0]

def test_known_quarantine_and_unchanged_raw():
    m=metrics()
    clean,report=load_and_check(write=False)
    assert len(clean)==m['overall']['n']
    assert report['quarantined_rows']==m['audit']['raw_rows']-m['audit']['complete_rows']
    assert digest(ROOT/'data/cookie_cats.csv')==m['audit']['raw_sha256']
    assert clean.sum_gamerounds.max()==m['audit']['local_max_rounds']
    pd.testing.assert_frame_equal(clean.reset_index(drop=True),pd.read_csv(ROOT/'data/cookie_cats_cleaned.csv'))
    assert not validate(clean)[0]

