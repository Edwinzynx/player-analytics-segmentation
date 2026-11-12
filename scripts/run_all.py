"""Reproduce every analytical phase offline from the unchanged checked-in raw file."""
import importlib
import importlib.metadata
import json
import platform
from common import ROOT,OUT,digest,save_json,update_metrics

STEPS=['phase2_cleaning_and_eda','phase4_feature_engineering','phase5_player_segmentation',
    'phase6_retention_analysis','phase7_statistical_testing','run_sql_analysis',
    'phase8_executive_dashboard','build_excel_workbook','export_bi',
    'build_insights_brief','update_readme_metrics']

def main():
    before=digest(ROOT/'data/cookie_cats.csv')
    audit=json.loads((OUT/'audit_baseline.json').read_text())
    save_json(OUT/'metrics.json',{'audit':audit})
    for module in STEPS:
        print('Running '+module,flush=True)
        importlib.import_module(module).main()
    # Documentation generator is added in the final cleanup phase.
    if (ROOT/'scripts/build_documentation.py').exists():
        importlib.import_module('build_documentation').main()
    assert digest(ROOT/'data/cookie_cats.csv')==before,'Raw file changed'
    versions={p:importlib.metadata.version(p) for p in [
        'pandas','numpy','scipy','scikit-learn','matplotlib','pytest','openpyxl','XlsxWriter']}
    update_metrics(reproducibility={'seed':42,'python':platform.python_version(),
        'packages':versions,'raw_sha256':before,'offline_analysis':True,
        'source_note':'Upstream evidence captured during audit; normal runs require no network.'})
    print('Pipeline completed; metrics.json is the numerical source of truth.',flush=True)

if __name__=='__main__':
    main()

