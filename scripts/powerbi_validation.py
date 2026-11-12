"""Independent expected results for every DAX measure and filter behavior."""
import json
import math
import hashlib
import pandas as pd
from common import OUT, metrics, update_metrics, digest


def expected_measures(group, population, measures, decile=None):
    def rate(frame, day):
        return float(frame['retention_'+day].mean()) if len(frame) else None
    result={'Players':len(group),'Total Rounds':int(group.sum_gamerounds.sum()),
        'Mean Rounds':float(group.sum_gamerounds.mean()),'Median Rounds':float(group.sum_gamerounds.median()),
        'D1 Retained':int(group.retention_1.sum()),'D7 Retained':int(group.retention_7.sum()),
        'Both Retained':int(((group.retention_1==1)&(group.retention_7==1)).sum()),
        'Share of Players':len(group)/len(population),
        'Share of Rounds':float(group.sum_gamerounds.sum()/population.sum_gamerounds.sum())}
    result['D7 Given D1']=result['Both Retained']/result['D1 Retained'] if result['D1 Retained'] else None
    for day in ['1','7']:
        prefix='D'+day
        result[prefix+' Retention']=rate(group,day)
        for arm in ['30','40']:
            result[prefix+' Gate '+arm]=rate(group[group.version=='gate_'+arm],day)
        control=result[prefix+' Gate 30']; treatment=result[prefix+' Gate 40']
        result[prefix+' Difference']=treatment-control if control is not None and treatment is not None else None
        result[prefix+' Relative Lift']=result[prefix+' Difference']/control if control and result[prefix+' Difference'] is not None else None
    result['D7 Difference pp']=result['D7 Difference']*100 if result['D7 Difference'] is not None else None
    cumulative=population[population.decile<=decile] if decile is not None else group
    result['Cumulative Rounds']=int(cumulative.sum_gamerounds.sum())
    denominator=(population if decile is not None else group).sum_gamerounds.sum()
    result['Cumulative Share']=float(cumulative.sum_gamerounds.sum()/denominator) if denominator else None
    return {k:result[k] for k in measures}


def build_cases(tables,measures):
    df=tables['fact_players']
    args=', '.join('"'+n+'", ['+n+']' for n in measures)
    cases=[{'name':'all_measures_full_sample','query':'EVALUATE ROW('+args+')',
            'expected':[expected_measures(df,df,measures)]}]
    for table,column in [('dim_tier','tier'),('dim_cohort','cohort'),('dim_decile','decile')]:
        rows=[]
        for key,part in df.groupby(column,sort=True):
            rows.append({column:int(key) if column=='decile' else key}|
                expected_measures(part,df,measures,int(key) if column=='decile' else None))
        cases.append({'name':'by_'+column,'query':f'EVALUATE SUMMARIZECOLUMNS({table}[{column}], '+args+')',
                      'keys':[column],'expected':rows})
    for cohort in ['both','none']:
        selected=df[df.cohort==cohort]
        rows=[{'decile':int(key)}|expected_measures(part,selected,measures,int(key))
              for key,part in selected.groupby('decile')]
        cases.append({'name':'deciles_sliced_'+cohort,
            'query':'EVALUATE CALCULATETABLE(SUMMARIZECOLUMNS(dim_decile[decile], '+args+'), TREATAS({"'+cohort+'"}, dim_cohort[cohort]))',
            'keys':['decile'],'expected':rows})
    # Version filters should be replaced by explicit arm measures, while counts
    # and rates still describe the selected version.
    for version in ['gate_30','gate_40']:
        part=df[df.version==version]
        expected=expected_measures(part,part,measures)
        full=expected_measures(df,df,measures)
        for key in measures:
            if any(s in key for s in ['Gate 30','Gate 40','Difference','Lift']):
                expected[key]=full[key]
        cases.append({'name':'version_sliced_'+version,'query':'EVALUATE CALCULATETABLE(ROW('+args+'), TREATAS({"'+version+'"}, fact_players[version]))',
                      'expected':[expected]})
    inference=tables['ab_statistics']
    cases.append({'name':'fixed_inference_snapshot','query':'EVALUATE ab_statistics','keys':['metric'],
                  'expected':json.loads(inference.to_json(orient='records',double_precision=15))})
    return cases


def definition_hashes():
    folder=OUT/'powerbi/ProductAnalytics.SemanticModel/definition'
    # Canonical newlines make the archived engine evidence portable across Git checkouts.
    return {p.relative_to(folder).as_posix():hashlib.sha256(p.read_text(encoding='utf-8').encode()).hexdigest()
            for p in sorted(folder.rglob('*.tmdl'))}


def validate_results(path=OUT/'powerbi/engine_results.json'):
    results=json.loads(path.read_text(encoding='utf-8-sig'))
    assert results['definition_sha256']==definition_hashes(), 'Engine evidence is stale for these model definitions'
    m=metrics(); expected=m['powerbi']['validation_expected']; comparisons=0
    for case in json.loads((OUT/'powerbi/validation_queries.json').read_text()):
        actual=results['queries'][case['name']]
        want=expected[case['name']]
        assert len(actual)==len(want),case['name']
        keys=case.get('keys',[])
        if keys:
            sort=lambda row:tuple(row[k] for k in keys)
            actual=sorted(actual,key=sort); want=sorted(want,key=sort)
        for a,b in zip(actual,want):
            assert set(a)==set(b),(case['name'],set(a)^set(b))
            for key,value in b.items():
                observed=a[key]
                if isinstance(value,(int,float)):
                    assert observed is not None and math.isclose(value,observed,abs_tol=1e-11,rel_tol=1e-11),(case['name'],key,value,observed)
                else:
                    assert observed==value,(case['name'],key,value,observed)
                comparisons+=1
    result={'status':'passed','comparisons':comparisons,'queries':len(expected),
            'desktop_version':results['desktop_version'],'engine_version':results['engine_version'],
            'model_refreshed':results['model_refreshed'],'definition_sha256':results['definition_sha256'],
            'results_sha256':digest(path),
            'visual_review':'Not performed: computer-use runtime failed to initialize.'}
    m['powerbi']['engine_validation']=result
    m['bi']['dax_engine_validation']='Passed local Power BI Desktop engine checks; see powerbi.engine_validation.'
    update_metrics(powerbi=m['powerbi'],bi=m['bi'])
    (OUT/'powerbi/validation.md').write_text(
        '# Native validation\n\n'+f"Power BI Desktop {result['desktop_version']}; analysis engine {result['engine_version']}. "
        f"Refreshed the generated embedded snapshot and executed {result['queries']} DAX queries; "
        f"{comparisons} field comparisons matched independent pandas expectations recorded in metrics.powerbi.validation_expected.\n\n"
        'Checks cover all measures, tier/cohort/decile groups, cumulative shares under cohort filters, '
        'and version-filter replacement for arm contrasts. Microsoft JSON schemas validate the report definitions; '
        'the installed Microsoft TMDL serializer parses the model.\n\n'
        'Visual rendering and interactive click behavior were not reviewed: both available computer-use runtimes '
        'failed to initialize before window capture. Open the project, refresh, and inspect each page before presenting it.\n\n'
        'Recheck: open the generated project in Desktop, then run '
        '`pwsh -File scripts/validate_powerbi.ps1`, followed by '
        '`python scripts/powerbi_validation.py`. The script only refreshes the specifically identified local project.\n',encoding='utf-8')
    print(f'Power BI engine: {comparisons} comparisons passed.')


if __name__=='__main__':
    validate_results()
