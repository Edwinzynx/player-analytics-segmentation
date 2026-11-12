"""Build a portable native PBIP report, TMDL model, and embedded refresh snapshot.

All observations come from the validated BI exports / metrics. Schema validation
uses the vendored Microsoft schemas, with no network required at build time.
"""
import base64
import json
import re
import uuid
import zlib
from pathlib import Path

import pandas as pd
from jsonschema import Draft7Validator
from referencing import Registry, Resource
from common import ROOT, OUT, metrics, update_metrics, digest

BASE = 'https://developer.microsoft.com/json-schemas/'
DEST = OUT / 'powerbi'
REPORT = DEST / 'ProductAnalytics.Report'
MODEL = DEST / 'ProductAnalytics.SemanticModel'
SCHEMAS = ROOT / 'scripts/powerbi_schemas'
INK = '#172C40'
TEAL = '#007F7A'


def schema(path):
    return BASE + path + '/schema.json'


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')


def write_text(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip()+'\n', encoding='utf-8')


def tag(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'player-analytics/'+name))


def q(name):
    return "'" + name.replace("'", "''") + "'"


def read_measures():
    measures = {}
    for line in (OUT/'bi/powerbi_measures.dax').read_text().splitlines():
        if not line.strip() or line.startswith('//'):
            continue
        match = re.match(r'^([^ ].*?) = (.*)', line)
        if match:
            name, expression = match.groups()
            measures[name] = expression
        else:
            measures[name] += '\n' + line.strip()
    return measures


def measure_format(name):
    if name.endswith(' pp'):
        return '0.00" pp";-0.00" pp";0.00" pp"'
    if any(s in name for s in ['Retention','Gate 30','Gate 40','Difference','Lift','Share','Given']):
        return '0.0%;-0.0%;0.0%'
    return '#,0.0' if name in ['Mean Rounds','Median Rounds'] else '#,0'


def encode_rows(df):
    raw = df.to_json(orient='values', force_ascii=False, double_precision=15).encode()
    compressor = zlib.compressobj(level=9, wbits=-15)
    return base64.b64encode(compressor.compress(raw)+compressor.flush()).decode()


def build_model(tables, measures):
    write_json(MODEL/'definition.pbism', {
        '$schema':schema('fabric/item/semanticModel/definitionProperties/1.0.0'),
        'version':'4.0','settings':{'qnaEnabled':False}})
    write_text(MODEL/'definition/database.tmdl', 'database\n\tcompatibilityLevel: 1601')
    model = ['model Model','\tculture: en-US','\tdefaultPowerBIDataSourceVersion: powerBI_V3',
             '\tsourceQueryCulture: en-US','\tdataAccessOptions','\t\tlegacyRedirects','\t\treturnErrorValuesAsNull', '']
    model += ['ref table '+name for name in tables]
    write_text(MODEL/'definition/model.tmdl', '\n'.join(model))
    for name, df in tables.items():
        lines = ['table '+name, '\tlineageTag: '+tag(name),'']
        if name == 'fact_players':
            for measure, expression in measures.items():
                lines += ['\tmeasure '+q(measure)+' =', *['\t\t\t'+s for s in expression.splitlines()],
                          '\t\tformatString: '+measure_format(measure),
                          '\t\tdisplayFolder: '+('Experiment' if any(s in measure for s in ['Gate','Difference','Lift']) else 'Performance'),
                          '\t\tlineageTag: '+tag(name+'/'+measure),'']
        types = []
        for col in df.columns:
            dtype = ('int64' if pd.api.types.is_integer_dtype(df[col]) else
                     'double' if pd.api.types.is_float_dtype(df[col]) else
                     'boolean' if pd.api.types.is_bool_dtype(df[col]) else 'string')
            types.append((col, {'int64':'Int64.Type','double':'type number','boolean':'type logical','string':'type text'}[dtype]))
            lines += ['\tcolumn '+q(col), '\t\tdataType: '+dtype,
                      '\t\tsourceColumn: '+col, '\t\tsummarizeBy: none',
                      '\t\tlineageTag: '+tag(name+'/'+col)]
            if name == 'fact_players' and col != 'version':
                lines += ['\t\tisHidden']
            if name == 'dim_tier' and col == 'tier':
                lines += ['\t\tsortByColumn: tier_id']
            if name == 'dim_cohort' and col == 'cohort':
                lines += ['\t\tsortByColumn: cohort_order']
            if dtype == 'double':
                lines += ['\t\tformatString: 0.0000']
            lines += ['']
        columns = '{'+', '.join(json.dumps(col) for col in df.columns)+'}'
        typing = '{'+', '.join('{'+json.dumps(col)+', '+typ+'}' for col,typ in types)+'}'
        lines += ['\tpartition '+name+' = m','\t\tmode: import','\t\tsource =',
                  '\t\t\t\tlet',
                  '\t\t\t\t    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("'+encode_rows(df)+'", BinaryEncoding.Base64), Compression.Deflate)), '+columns+'),',
                  '\t\t\t\t    Typed = Table.TransformColumnTypes(Source, '+typing+')',
                  '\t\t\t\tin','\t\t\t\t    Typed']
        write_text(MODEL/'definition/tables'/(name+'.tmdl'), '\n'.join(lines))
    relations=[]
    for dim,key in [('dim_tier','tier_id'),('dim_cohort','cohort'),('dim_decile','decile')]:
        relations += ['relationship '+tag('relationship/'+dim),
                      '\tfromColumn: fact_players.'+key, '\ttoColumn: '+dim+'.'+key,
                      '\tcrossFilteringBehavior: oneDirection','']
    write_text(MODEL/'definition/relationships.tmdl','\n'.join(relations))


def literal(value):
    val = str(value).lower() if isinstance(value,bool) else q(value) if isinstance(value,str) else str(value)
    return {'expr':{'Literal':{'Value':val}}}


def field(table, name, measure=False):
    return {('Measure' if measure else 'Column'):{'Expression':{'SourceRef':{'Entity':table}},'Property':name}}


def col(table,name):
    return (table,name,False)


def ms(name):
    return ('fact_players',name,True)


def projection(item):
    table,name,measure=item
    return {'field':field(*item),'queryRef':table+'.'+name,'nativeQueryRef':name}


def visual(page, key, kind, title, box, roles=None, objects=None):
    x,y,w,h=box
    config={'visualType':kind,'drillFilterOtherVisuals':True,
            'visualContainerObjects':{
                'title':[{'properties':{'show':literal(bool(title)), 'text':literal(title),
                    'fontSize':literal(12),'fontColor':{'solid':{'color':literal(INK)}}}}],
                'background':[{'properties':{'show':literal(True),'color':{'solid':{'color':literal('#FFFFFF')}},'transparency':literal(0)}}]}}
    if roles:
        config['query']={'queryState':{role:{'projections':[projection(i) for i in items]} for role,items in roles.items()}}
        first=next(iter(roles.values()))[0]
        if not first[2]:
            config['query']['sortDefinition']={'sort':[{'field':field(*first),'direction':'Ascending'}],'isDefaultSort':False}
    if objects:
        config['objects']=objects
    obj={'$schema':schema('fabric/item/report/definition/visualContainer/2.1.0'),
         'name':key,'position':{'x':x,'y':y,'z':len(page['visuals']),'height':h,'width':w,'tabOrder':len(page['visuals'])},'visual':config}
    page['visuals'].append(obj)
    return obj


def textbox(page,key,text,box,size=14,color=INK):
    return visual(page,key,'textbox','',box,objects={'general':[{'properties':{'paragraphs':[
        {'textRuns':[{'value':text,'textStyle':{'fontFamily':'Segoe UI','fontSize':str(size)+'pt','color':color}}]}]}}]})


def card(page,key,measure,title,x):
    return visual(page,key,'card',title,(x,145,284,112),{'Values':[ms(measure)]},
                  {'labels':[{'properties':{'fontSize':literal(30),'labelDisplayUnits':literal(1),'color':{'solid':{'color':literal(TEAL)}}}}],
                   'categoryLabels':[{'properties':{'show':literal(False)}}]})


def page(name,title,subtitle):
    p={'name':name,'displayName':title,'visuals':[]}
    textbox(p,name+'_title',title,(24,16,1192,58),28)
    textbox(p,name+'_subtitle',subtitle,(24,78,1192,50),12)
    return p


def build_report(m):
    write_json(DEST/'ProductAnalytics.pbip',{'$schema':schema('fabric/pbip/pbipProperties/1.0.0'),
        'version':'1.0','artifacts':[{'report':{'path':'ProductAnalytics.Report'}}],
        'settings':{'enableAutoRecovery':True}})
    write_json(REPORT/'definition.pbir',{'$schema':schema('fabric/item/report/definitionProperties/2.0.0'),
        'version':'4.0','datasetReference':{'byPath':{'path':'../ProductAnalytics.SemanticModel'}}})
    write_json(REPORT/'definition/version.json',{'$schema':schema('fabric/item/report/definition/versionMetadata/1.0.0'),'version':'2.0.0'})
    write_json(REPORT/'definition/report.json',{'$schema':schema('fabric/item/report/definition/report/3.0.0'),
        'themeCollection':{},'settings':{'useStylableVisualContainerHeader':True,'exportDataMode':'AllowSummarized'}})
    overview=page('overview','Product performance | retention & engagement',
        'Cookie Cats • Truncated source extract • Rates follow filters; cohort retention is defined by its flags.')
    for i,(measure,title) in enumerate([('Players','Accepted players'),('D1 Retention','D1 retention'),('D7 Retention','D7 retention'),('Total Rounds','Total rounds')]):
        card(overview,'kpi_'+str(i),measure,title,24+300*i)
    visual(overview,'tier_rates','clusteredColumnChart','Retention rises with observed engagement',(24,280,728,300),
        {'Category':[col('dim_tier','tier')],'Y':[ms('D1 Retention'),ms('D7 Retention')]})
    visual(overview,'version_rates','clusteredColumnChart','Descriptive retention by assigned version',(768,280,448,300),
        {'Category':[col('fact_players','version')],'Y':[ms('D1 Retention'),ms('D7 Retention')]})
    visual(overview,'cohort_profile','tableEx','Transparent retention cohorts | descriptive',(24,604,892,250),
        {'Values':[col('dim_cohort','cohort'),ms('Players'),ms('Share of Players'),ms('Share of Rounds'),ms('Mean Rounds'),ms('Median Rounds')]})
    visual(overview,'version_slicer','slicer','Version',(936,604,280,110),{'Values':[col('fact_players','version')]})
    visual(overview,'tier_slicer','slicer','Engagement tier',(936,730,280,124),{'Values':[col('dim_tier','tier')]})
    textbox(overview,'overview_note','So what: describe behavioral concentration; retention-defined cohorts cannot establish causal drivers.',(24,872,1192,48),12)

    exp=page('experiment','Experiment | effect size before decisions',
        'Truncated source extract • Primary: two-sided tests with Holm across D1 and D7. Effect = gate_40 − gate_30.')
    for i,(measure,title) in enumerate([('D1 Difference','D1 absolute difference'),('D7 Difference','D7 absolute difference'),('D7 Relative Lift','D7 relative lift'),('Players','Experiment population')]):
        card(exp,'experiment_kpi_'+str(i),measure,title,24+300*i)
    visual(exp,'experiment_rates','clusteredColumnChart','Observed arm rates',(24,280,520,300),
        {'Category':[col('fact_players','version')],'Y':[ms('D1 Retention'),ms('D7 Retention')]})
    d7=m['ab']['D7']
    textbox(exp,'decision','Decision\n'+d7['conclusion']+'\n\nKeep the current setting while collecting a larger, complete randomized sample. Predefine decision thresholds before another test.',(568,280,648,300),18)
    available=pd.read_csv(OUT/'bi/ab_statistics.csv').columns
    # Explicit aliases retain the validated source fields, not recomputed visual tests.
    names=['metric','difference','ci_low','ci_high','p_two_sided','p_holm','bootstrap_ci_low','bootstrap_ci_high']
    assert set(names).issubset(available), 'Inference export is missing required fields'
    visual(exp,'inference','tableEx','Fixed full-sample inference | rate-unit effects and confidence bounds',(24,604,1192,172),
        {'Values':[col('ab_statistics',n) for n in names]})
    textbox(exp,'inference_note','Confidence intervals: Newcombe–Wilson for the absolute difference; percentile bootstrap as a sensitivity check. Inferential results are fixed full-sample outputs; chart selections do not rerun the test.',(24,792,1192,70),13)
    textbox(exp,'association_note','The engagement-tier association is a separate descriptive test. Retention and engagement share an observation window; association is not a treatment effect.',(24,876,1192,48),12)

    conc=page('concentration','Concentration | cohorts & analytical boundaries',
        'Truncated source extract • Deciles rank the full sample by rounds, then userid. Slicers filter fixed deciles; no reranking.')
    for i,(measure,title) in enumerate([('Players','Selected players'),('Total Rounds','Selected rounds'),('Mean Rounds','Mean rounds'),('Median Rounds','Median rounds')]):
        card(conc,'concentration_kpi_'+str(i),measure,title,24+300*i)
    visual(conc,'pareto','lineClusteredColumnComboChart','Decile contribution and cumulative share',(24,280,792,324),
        {'Category':[col('dim_decile','decile')],'Y':[ms('Total Rounds')],'Y2':[ms('Cumulative Share')]})
    visual(conc,'cohort_slicer','slicer','Retention cohort',(840,280,376,160),{'Values':[col('dim_cohort','cohort')]})
    visual(conc,'concentration_version','slicer','Assigned version',(840,460,376,144),{'Values':[col('fact_players','version')]})
    visual(conc,'cohort_version','tableEx','Cohort × version | size and engagement',(24,628,792,236),
        {'Values':[col('dim_cohort','cohort'),col('fact_players','version'),ms('Players'),ms('Share of Rounds'),ms('Mean Rounds'),ms('D7 Retention')]})
    textbox(conc,'quality_note',
        'Quality & scope\nComplete local extract; malformed rows excluded by the pipeline. No valid outliers removed.\n\nNo revenue, timestamps or longitudinal trends. Cohort retention is true by construction.',(840,628,376,236),14)
    textbox(conc,'scope_note','So what: prioritize investigation of concentrated usage. Do not infer customer value, future retention, or segment-specific causal effects.',(24,880,1192,40),12)
    pages=[overview,exp,conc]
    write_json(REPORT/'definition/pages/pages.json',{'$schema':schema('fabric/item/report/definition/pagesMetadata/1.0.0'),
        'pageOrder':[p['name'] for p in pages],'activePageName':pages[0]['name']})
    for p in pages:
        definition={'$schema':schema('fabric/item/report/definition/page/2.0.0'), 'name':p['name'],
            'displayName':p['displayName'],'displayOption':'FitToPage','width':1240,'height':940}
        if p is exp:
            definition['visualInteractions']=[{'source':s['name'],'target':t['name'],'type':'NoFilter'}
                for s in p['visuals'] for t in p['visuals'] if s is not t]
        write_json(REPORT/'definition/pages'/p['name']/'page.json',definition)
        for v in p['visuals']:
            write_json(REPORT/'definition/pages'/p['name']/'visuals'/v['name']/'visual.json',v)
    return pages


def validate_schemas():
    resources=[]
    for path in SCHEMAS.rglob('schema*.json'):
        data=json.loads(path.read_text())
        resource=Resource.from_contents(data)
        resources += [(BASE+path.relative_to(SCHEMAS).as_posix(),resource)]
        if '$id' in data:
            resources += [(data['$id'],resource)]
    registry=Registry().with_resources(resources)
    checked=[]
    for path in sorted(DEST.rglob('*')):
        if path.suffix not in ['.json','.pbip','.pbir','.pbism'] or '.pbi' in path.parts:
            continue
        data=json.loads(path.read_text(encoding='utf-8'))
        if '$schema' not in data:
            continue
        contract=registry.contents(data['$schema'])
        errors=list(Draft7Validator(contract,registry=registry).iter_errors(data))
        if errors:
            raise ValueError(str(path)+'\n'+'\n'.join(str(e) for e in errors))
        checked.append(path.relative_to(DEST).as_posix())
    return checked


def main():
    m=metrics()
    tables={name:pd.read_csv(OUT/'bi'/(name+'.csv')) for name in
            ['fact_players','dim_tier','dim_cohort','dim_decile','ab_statistics']}
    measures=read_measures()
    build_model(tables, measures)
    pages=build_report(m)
    from powerbi_validation import build_cases
    cases=build_cases(tables, measures)
    write_json(DEST/'validation_queries.json',cases)
    write_text(DEST/'validation_queries.dax', '\n\n'.join('// '+c['name']+'\n'+c['query'] for c in cases))
    checked=validate_schemas()
    write_text(DEST/'README.md', '''# Native Power BI report

Open `ProductAnalytics.pbip` in current Power BI Desktop. Choose **Home → Refresh**
on first open: the project stores a portable, compressed data snapshot in its M
partitions. No local path editing, credentials, gateway, or online source is needed.
Keep the `.Report` and `.SemanticModel` folders beside the `.pbip` file.

Use the page tabs for performance, experiment inference, and concentration.
Slicers affect descriptive pages. The experiment page has no slicers and disables
cross-visual filtering: its inferential table is a disconnected full-sample snapshot.
Percent-format effect cards display differences in rate units (read as percentage
points); confidence bounds in the inference table use rate units.

Rebuild after changing the analytical inputs:
`python scripts/run_all.py`. Close Desktop before rebuilding; reopen and refresh.
The report is generated from `outputs/bi` and `outputs/metrics.json`. Editing a
generated report is supported, but the next build overwrites generated definitions.
Keep custom layouts in a separate project or edit the Python generator.

The model uses single-direction dimension-to-fact filters. Cohorts are descriptive
retention patterns; segment-specific retention is partly true by construction.
Deciles are fixed full-population rankings. All statistical decisions use Python
outputs; slicers do not produce new tests. The sample is an incomplete local prefix
of the published Cookie Cats file, not a verified representative sample.

No PBIX or cloud publication is required. Desktop's local cache is ignored by Git.
See `validation.md` for actual engine and layout checks.
''')
    files={p.relative_to(DEST).as_posix():digest(p) for p in sorted(DEST.rglob('*'))
           if p.is_file() and p.suffix in ['.pbip','.pbir','.pbism','.tmdl','.json']
           and '.pbi' not in p.parts and p.name != 'engine_results.json'}
    update_metrics(powerbi={'format':'PBIP/PBIR/TMDL','tables':{n:len(t) for n,t in tables.items()},
        'measures':len(measures),'pages':len(pages),'visuals':sum(len(p['visuals']) for p in pages),
        'schema_validated_files':len(checked),'files':files,
        'validation_expected':{c['name']:c['expected'] for c in cases},
        'snapshot_source':'outputs/bi CSVs recorded in metrics.bi.files',
        'engine_validation':'Run scripts/validate_powerbi.ps1 against an open Desktop project.'})
    from powerbi_validation import validate_results, definition_hashes
    evidence=DEST/'engine_results.json'
    if evidence.exists() and json.loads(evidence.read_text(encoding='utf-8-sig'))['definition_sha256']==definition_hashes():
        validate_results(evidence)
    else:
        write_text(DEST/'validation.md', '# Native validation\n\nReport JSON schemas passed. '
            'Current model definitions do not have matching engine evidence. Open the project in Desktop, '
            'run scripts/validate_powerbi.ps1, then scripts/powerbi_validation.py. '
            'Visual rendering has not been reviewed because the app-control runtime failed to initialize.')
    print('Native Power BI project generated and schemas validated.')


if __name__=='__main__':
    main()
