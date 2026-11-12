import base64
import json
import re
import zlib
import pandas as pd
from common import OUT,metrics,digest
from build_powerbi_project import DEST,MODEL,REPORT,validate_schemas,read_measures
from powerbi_validation import definition_hashes


def test_native_project_schemas_and_lineage():
    m=metrics()['powerbi']
    assert len(validate_schemas())==m['schema_validated_files']
    for name,expected_hash in m['files'].items():
        assert digest(DEST/name)==expected_hash
    manifest=json.loads((REPORT/'definition/pages/pages.json').read_text())
    assert len(manifest['pageOrder'])==m['pages']
    fields={name:set(pd.read_csv(OUT/'bi'/(name+'.csv')).columns) for name in m['tables']}
    measures=read_measures()
    count=0
    for name in manifest['pageOrder']:
        path=REPORT/'definition/pages'/name
        page=json.loads((path/'page.json').read_text())
        visuals=[json.loads(p.read_text()) for p in path.glob('visuals/*/visual.json')]
        count+=len(visuals)
        for v in visuals:
            box=v['position']
            assert 0<=box['x'] and box['x']+box['width']<=page['width']
            assert 0<=box['y'] and box['y']+box['height']<=page['height']
            for role in v['visual'].get('query',{}).get('queryState',{}).values():
                for projection in role['projections']:
                    kind,value=next(iter(projection['field'].items()))
                    table=value['Expression']['SourceRef']['Entity']
                    assert value['Property'] in (measures if kind=='Measure' else fields[table])
        if name=='experiment':
            blocked={(i['source'],i['target']) for i in page['visualInteractions'] if i['type']=='NoFilter'}
            assert all((s['name'],t['name']) in blocked for s in visuals for t in visuals if s is not t)
            inference=next(v for v in visuals if v['name']=='inference')
            names={p['field']['Column']['Property'] for p in inference['visual']['query']['queryState']['Values']['projections']}
            assert {'p_holm','p_two_sided','ci_low','ci_high'}<=names
    assert count==m['visuals']


def test_embedded_snapshots_match_validated_csvs():
    for name,count in metrics()['powerbi']['tables'].items():
        tmdl=(MODEL/'definition/tables'/(name+'.tmdl')).read_text()
        encoded=re.search(r'Binary.FromText\("([A-Za-z0-9+/=]+)"',tmdl).group(1)
        rows=json.loads(zlib.decompress(base64.b64decode(encoded),wbits=-15))
        expected=pd.read_csv(OUT/'bi'/(name+'.csv'))
        assert len(rows)==count
        pd.testing.assert_frame_equal(pd.DataFrame(rows,columns=expected.columns),expected,check_dtype=False,atol=1e-14,rtol=1e-14)


def test_archived_dax_execution_matches_current_model_and_expectations():
    import math
    m=metrics()['powerbi']
    evidence=json.loads((DEST/'engine_results.json').read_text(encoding='utf-8-sig'))
    assert evidence['definition_sha256']==definition_hashes()
    assert m['engine_validation']['status']=='passed'
    assert evidence['model_refreshed']
    cases=json.loads((DEST/'validation_queries.json').read_text())
    comparisons=0
    for case in cases:
        expected=m['validation_expected'][case['name']]
        actual=evidence['queries'][case['name']]
        keys=case.get('keys',[])
        sort=lambda row:tuple(row[k] for k in keys)
        assert len(actual)==len(expected)
        for a,b in zip(sorted(actual,key=sort),sorted(expected,key=sort)):
            assert set(a)==set(b)
            for key,value in b.items():
                if isinstance(value,(int,float)):
                    assert a[key] is not None and math.isclose(a[key],value,rel_tol=1e-11,abs_tol=1e-11)
                else:
                    assert a[key]==value
                comparisons+=1
    assert comparisons==m['engine_validation']['comparisons']
