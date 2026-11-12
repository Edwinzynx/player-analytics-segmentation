"""Final release check: two complete runs, identical metrics, and the test suite."""
import hashlib
import subprocess
import sys
import xml.etree.ElementTree as ET
from common import ROOT,OUT,digest,update_metrics,metrics
from build_excel_workbook import libreoffice

def main():
    raw_before=digest(ROOT/'data/cookie_cats.csv')
    for run in range(2):
        subprocess.run([sys.executable,str(ROOT/'scripts/run_all.py')],cwd=ROOT,check=True)
        current=(OUT/'metrics.json').read_bytes()
        if run==0:
            first=current
        else:
            assert current==first,'Full pipeline metrics are not reproducible'
    result=subprocess.run([sys.executable,'-m','pytest','-q','--junitxml=outputs/test_results.xml'],cwd=ROOT)
    tree=ET.parse(OUT/'test_results.xml')
    cases=tree.findall('.//testcase')
    failed=sum(c.find('failure') is not None or c.find('error') is not None for c in cases)
    skipped=sum(c.find('skipped') is not None for c in cases)
    validation={'test_cases':len(cases),'passed':len(cases)-failed-skipped,
        'failed':failed,'skipped':skipped,'exit_code':result.returncode,
        'full_runs':2,'identical_metrics':True,
        'metrics_sha256_before_validation':hashlib.sha256(current).hexdigest(),
        'raw_unchanged':raw_before==digest(ROOT/'data/cookie_cats.csv'),
        'limitations':[('LibreOffice not available locally: native recalculation skipped.' if not libreoffice()
            else 'LibreOffice recalculation included in the test suite.'),
            ('Power BI engine checks passed; native visual review blocked by app-control runtime failure.'
             if isinstance(metrics().get('powerbi',{}).get('engine_validation'),dict)
             else 'Current Power BI model engine execution has not been verified.'),
            'Original acquisition/assignment protocol and truncation cause unverified.',
            'Native Excel rendering not verified; cached-value previews reviewed separately.']}
    update_metrics(validation=validation)
    text=(f"# Final validation\n\n"
        f"Complete pipeline runs: {validation['full_runs']}; identical metrics before this validation record: {validation['identical_metrics']}.\n\n"
        f"Tests: {validation['passed']} passed, {failed} failed, {skipped} skipped. Raw file unchanged: {validation['raw_unchanged']}.\n\n"
        "SQL queries, statistical reproducibility, cohort rules, BI totals, Excel formulas/caches and generated reports are covered.\n\n"
        "## Unverified or intentionally skipped\n\n"+'\n'.join('- '+s for s in validation['limitations'])+'\n')
    (OUT/'validation_results.md').write_text(text,encoding='utf-8')
    if result.returncode:
        raise SystemExit(result.returncode)

if __name__=='__main__':
    main()
