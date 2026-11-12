"""Strict raw-data contract with one evidenced, hash-bound quarantine exception."""
import json
import warnings
import numpy as np
import pandas as pd
from common import ROOT, OUT, digest, records, update_metrics

COLUMNS=['userid','version','sum_gamerounds','retention_1','retention_7']

def validate(df):
    errors=[]
    if list(df.columns)!=COLUMNS:
        return ['schema: exact columns/order required'], {}
    for col in COLUMNS:
        if df[col].isna().any() or df[col].astype(str).eq('').any():
            errors.append(f'nulls: {col}')
    for col in ['userid','sum_gamerounds']:
        values=pd.to_numeric(df[col],errors='coerce')
        if values.isna().any() or not np.isfinite(values).all() or not values.mod(1).eq(0).all():
            errors.append(f'integer dtype/domain: {col}')
        if values.lt(0).any():
            errors.append(f'non-negative: {col}')
    if df.userid.duplicated().any():
        errors.append('duplicate userid')
    if not df.version.isin(['gate_30','gate_40']).all():
        errors.append('invalid version')
    for col in ['retention_1','retention_7']:
        if not df[col].astype(str).isin(['True','False','0','1']).all():
            errors.append(f'invalid binary flag: {col}')
    counts={'nulls':df.isna().sum().astype(int).to_dict(),
            'duplicates':int(df.userid.duplicated().sum()),
            'invalid_versions':int((~df.version.isin(['gate_30','gate_40'])).sum())}
    return errors,counts

def load_and_check(raw_path=None, write=True):
    path=raw_path or ROOT/'data/cookie_cats.csv'
    audit=json.loads((OUT/'audit_baseline.json').read_text())
    raw=pd.read_csv(path,dtype=str)
    raw_errors,raw_counts=validate(raw)
    quarantine=pd.DataFrame(columns=COLUMNS)
    clean=raw.copy()
    # Exception is authorized only for the exact audited artifact and its exact row.
    if digest(path)==audit['raw_sha256']:
        expected=audit['incomplete_row']
        mask=pd.Series(True,index=raw.index)
        for key,value in expected.items():
            mask &= raw[key].isna() if value is None else raw[key].eq(value)
        quarantine=raw.loc[mask].copy()
        clean=raw.loc[~mask].copy()
    errors,counts=validate(clean)
    report={'raw_rows':len(raw),'accepted_rows':len(clean),'quarantined_rows':len(quarantine),
        'raw_sha256':digest(path),'raw_violations':raw_errors,'raw_checks':raw_counts,
        'hard_errors':errors,'accepted_checks':counts,
        'inferred_raw_dtypes':pd.read_csv(path).dtypes.astype(str).to_dict(),
        'soft_warnings':[], 'quarantine':records(quarantine)}
    if not errors:
        for col in ['userid','sum_gamerounds']:
            clean[col]=pd.to_numeric(clean[col]).astype('int64')
        for col in ['retention_1','retention_7']:
            clean[col]=clean[col].map({'True':1,'False':0,'0':0,'1':1}).astype('int64')
        q1,q3=clean.sum_gamerounds.quantile([.25,.75])
        cutoff=q3+1.5*(q3-q1)
        outliers=clean[clean.sum_gamerounds.gt(cutoff)]
        inconsistent=clean.sum_gamerounds.eq(0)&(clean.retention_1.eq(1)|clean.retention_7.eq(1))
        report['outliers']={'iqr_upper_fence':float(cutoff),'count':len(outliers),
            'max':int(clean.sum_gamerounds.max()),'p999':float(clean.sum_gamerounds.quantile(.999)),
            'policy':'report and retain all valid values; no trimming or winsorization'}
        report['zero_rounds_with_retention']=int(inconsistent.sum())
        report['accepted_dtypes']=clean.dtypes.astype(str).to_dict()
        if len(outliers): report['soft_warnings'].append('High-round records exceed the IQR fence; retained.')
        if inconsistent.any(): report['soft_warnings'].append('Zero-round records have retention flags; retained pending source clarification.')
        report['soft_warnings'].append('Raw source is a truncated prefix; population representativeness unverified.')
    if write:
        update_metrics(data_quality=report)
        lines=['# Data quality report','',f"Raw records: {report['raw_rows']:,}; accepted: {report['accepted_rows']:,}; quarantined: {report['quarantined_rows']:,}.",
            '',f"Raw SHA-256: {report['raw_sha256']}",'',
            'The exact audited incomplete final row is quarantined. All other violations fail the run.',
            '', '## Hard checks', '', 'Schema, nulls, duplicate identifiers, integer/non-negative domains, valid version and strict binary flags.',
            '', 'Result: '+('FAIL: '+', '.join(errors) if errors else 'PASS on accepted rows'),
            '', '## Raw findings','',*['- '+e for e in raw_errors], '', '## Soft warnings','',
            *['- '+e for e in report['soft_warnings']]]
        if 'outliers' in report:
            o=report['outliers']
            lines += ['',f"IQR upper fence: {o['iqr_upper_fence']:.2f}; flagged: {o['count']:,}; maximum: {o['max']:,}; upper percentile: {o['p999']:.2f}.",
                f"Zero-round records with a retention flag: {report['zero_rounds_with_retention']:,}.",
                '', 'All valid outliers are retained. See metrics.json/data_quality for dtype and check details.']
        (OUT/'data_quality_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
        quarantine.to_csv(OUT/'quarantined_records.csv',index=False)
    if errors:
        raise ValueError('Data quality hard failure: '+'; '.join(errors))
    for message in report['soft_warnings']:
        warnings.warn(message,UserWarning)
    return clean,report

def main():
    clean,_=load_and_check()
    clean.to_csv(ROOT/'data/cookie_cats_cleaned.csv',index=False)

if __name__=='__main__':
    main()

