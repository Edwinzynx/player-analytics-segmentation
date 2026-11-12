"""Shared paths, reporting contract and deterministic business definitions."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs'
SEED = 42
ALPHA = 0.05
BOOTSTRAPS = 10_000
TIERS = ['0', '1-5', '6-15', '16-50', '51-150', '151-500', '>500']
BINS = [-1, 0, 5, 15, 50, 150, 500, float('inf')]
COHORTS = ['none', 'D1 only', 'D7 only', 'both']

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')

def metrics():
    return json.loads((OUT / 'metrics.json').read_text(encoding='utf-8'))

def update_metrics(**sections):
    m = metrics() if (OUT / 'metrics.json').exists() else {}
    m.update(sections)
    save_json(OUT / 'metrics.json', m)
    return m

def records(df):
    return json.loads(df.to_json(orient='records', double_precision=15))

def features(df):
    df = df.copy()
    for col in ['retention_1', 'retention_7']:
        df[col] = df[col].astype(int)
        df[col + '_int'] = df[col]
    df['retention_score'] = df.retention_1 + 2 * df.retention_7
    df['cohort'] = df.retention_score.map(dict(enumerate(COHORTS)))
    df['tier_id'] = pd.cut(df.sum_gamerounds, BINS, labels=False).astype(int)
    df['tier'] = df.tier_id.map(dict(enumerate(TIERS)))
    df['cohort_tier'] = df.cohort + ' / ' + df.tier
    df['log_gamerounds'] = np.log1p(df.sum_gamerounds)
    # SQL NTILE: descending rounds, userid ascending, larger buckets first.
    order = df.sort_values(['sum_gamerounds', 'userid'], ascending=[False, True]).index
    sizes = np.full(10, len(df) // 10)
    sizes[:len(df) % 10] += 1
    df.loc[order, 'decile'] = np.repeat(np.arange(1, 11), sizes)
    df['decile'] = df.decile.astype(int)
    return df

def load_players():
    return pd.read_csv(ROOT / 'data/player_segments.csv', keep_default_na=False)

def simple_profile(df, key):
    p = df.groupby(key, sort=True, observed=True).agg(
        n=('userid', 'size'), rounds=('sum_gamerounds', 'sum'),
        mean_rounds=('sum_gamerounds', 'mean'), median_rounds=('sum_gamerounds', 'median'),
        d1=('retention_1', 'mean'), d7=('retention_7', 'mean')).reset_index()
    p['size_share'] = p.n / len(df)
    p['rounds_share'] = p['rounds'] / df.sum_gamerounds.sum()
    return p

