"""Execute the SQL file itself and compare every result to independent pandas logic."""
import re
import sqlite3
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
from common import ROOT, OUT, load_players, records, update_metrics

def queries():
    text=(ROOT/'sql/analysis.sql').read_text(encoding='utf-8-sig')
    return {name:body.strip() for name,body in re.findall(r'-- name: (\w+)\s*\n(.*?)(?=-- name:|\Z)',text,re.S)}

def build_database(df, path=None):
    conn=sqlite3.connect(path or ':memory:')
    df.to_sql('player_activity',conn,index=False,if_exists='replace')
    pd.read_csv(ROOT/'data/cookie_cats.csv').to_sql('raw_player_activity',conn,index=False,if_exists='replace')
    conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_user ON player_activity(userid)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_version ON player_activity(version)')
    conn.commit()
    return conn

def aggregate(df,key):
    return df.groupby(key,sort=True).agg(n=('userid','size'),rounds=('sum_gamerounds','sum'),
        mean_rounds=('sum_gamerounds','mean'),d1=('retention_1','mean'),d7=('retention_7','mean')).reset_index()

def quality(df,flags=True):
    row={'n':len(df),'duplicate_userids':int(df.userid.duplicated().sum()),
        'rows_with_null':int(df[['userid','version','sum_gamerounds','retention_1','retention_7']].isna().any(axis=1).sum()),
        'invalid_version':int((~df.version.isin(['gate_30','gate_40'])).sum())}
    if flags:
        row.update(negative_rounds=int(df.sum_gamerounds.lt(0).sum()),
            invalid_flags=int((~df.retention_1.isin([0,1])|~df.retention_7.isin([0,1])).sum()))
    return pd.DataFrame([row])

def pandas_results(df):
    r={}
    r['summary']=pd.DataFrame([dict(n=len(df),rounds=int(df.sum_gamerounds.sum()),
        mean_rounds=df.sum_gamerounds.mean(),min_rounds=int(df.sum_gamerounds.min()),
        max_rounds=int(df.sum_gamerounds.max()),d1=df.retention_1.mean(),d7=df.retention_7.mean())])
    r['version']=aggregate(df,'version')
    r['tier']=aggregate(df,'tier_id')
    ranked=df.sort_values(['sum_gamerounds','userid'],ascending=[False,True]).copy()
    sizes=np.full(4,len(df)//4); sizes[:len(df)%4]+=1
    ranked['quartile']=np.repeat(np.arange(1,5),sizes)
    r['quartile']=aggregate(ranked,'quartile')
    t=r['tier'][['tier_id','n','d7']].copy()
    t['prior_d7']=t.d7.shift(); t['d7_step']=t.d7-t.prior_d7
    r['tier_lag']=t
    d=df.groupby('decile').agg(n=('userid','size'),rounds=('sum_gamerounds','sum')).reset_index()
    d['rounds_share']=d['rounds']/d['rounds'].sum()
    d['cumulative_rounds_share']=d['rounds'].cumsum()/d['rounds'].sum()
    r['decile']=d
    r['quality']=quality(df)
    r['raw_quality']=quality(pd.read_csv(ROOT/'data/cookie_cats.csv'),False)
    both=int((df.retention_1.eq(1)&df.retention_7.eq(1)).sum())
    r['funnel']=pd.DataFrame([dict(all_players=len(df),d1=int(df.retention_1.sum()),both=both,
        d7_only=int((df.retention_1.eq(0)&df.retention_7.eq(1)).sum()),d7_given_d1=both/df.retention_1.sum())])
    r['segment_version']=aggregate(df,['cohort','tier_id','version']).drop(columns='mean_rounds')
    return r

def compare(conn,df):
    expected=pandas_results(df)
    results={}
    for name,query in queries().items():
        actual=pd.read_sql_query(query,conn)
        assert_frame_equal(actual,expected[name],check_dtype=False,rtol=1e-12,atol=1e-12)
        results[name]=records(actual)
    assert set(results)==set(expected)
    return results

def main():
    df=load_players()
    with build_database(df,ROOT/'data/cookie_cats.db') as conn:
        results=compare(conn,df)
    update_metrics(sql=results,sql_validation={'all_queries_match':True,'query_count':len(results)})
    (OUT/'sql').mkdir(exist_ok=True)
    for name,rows in results.items():
        pd.DataFrame(rows).to_csv(OUT/'sql'/f'{name}.csv',index=False)
    print(f'SQL/pandas parity passed for {len(results)} queries.')

if __name__=='__main__':
    main()

