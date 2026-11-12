"""One-time audit enrichment: parse old claims from Git; never type old results."""
import json
import re
import io
import pandas as pd
import numpy as np
from scipy import stats
from audit_baseline import git_text
from common import OUT,save_json

def main():
    readme=git_text('README.md')
    report=git_text('PROJECT_MASTER_REPORT.md')
    stats_script=git_text('scripts/phase7_statistical_testing.py')
    def number(text,pattern):
        hit=re.search(pattern,text,re.I)
        if not hit: raise ValueError('Missing baseline evidence: '+pattern)
        return float(hit.group(1).replace(',',''))
    claims={
        'headline_d7_p':number(readme,r'\$p=([\d.]+)\$ one-tailed'),
        'headline_bootstrap_share_pct':number(readme,r'([\d.]+)% bootstrap win probability'),
        'headline_odds_gate30_over_gate40':number(readme,r'Odds Ratio = ([\d.]+)'),
        'headline_silhouette':number(readme,r'Silhouette Score = ([\d.]+)'),
        'association_expected_min':number(report,r'minimum expected cell count = ([\d.]+)'),
        'interview_calinski_harabasz':number(report,r'Calinski-Harabasz index \(([\d,]+)\)'),
        'interview_davies_bouldin':number(report,r'Davies-Bouldin index \(([\d.]+)\)'),
        'old_bootstrap_iterations':number(stats_script,r'boot_iterations = (\d+)'),
        'old_d7_script_ci_low_pp':number(stats_script,r'CI strictly positive \[([\d.]+)%'),
        'old_d7_script_ci_high_pp':number(stats_script,r'CI strictly positive \[[\d.]+%, ([\d.]+)%'),
        'old_bootstrap_mean_pp':number(report,r'Bootstrap Posterior Mean Lift\*\*: \*\*\+([\d.]+)%'),
        'old_bootstrap_low_pp':number(report,r'Empirical Bootstrap CI\*\*: \$\[(-[\d.]+)'),
        'old_bootstrap_high_pp':number(report,r'Empirical Bootstrap CI\*\*: \$\[-[\d.]+\\%, \+([\d.]+)')}
    # Preserve all numerical table rows as audit evidence, without promotional prose.
    tables=[]
    for path,text in [('README.md',readme),('PROJECT_MASTER_REPORT.md',report)]:
        for line_no,line in enumerate(text.splitlines(),1):
            if line.startswith('|') and re.search(r'\d',line):
                tables.append({'file':path,'line':line_no,
                    'values':re.findall(r'[-+]?\d[\d,.]*',line)})
    baseline=json.loads((OUT/'audit_baseline.json').read_text())
    baseline['legacy_selected_claims']=claims
    # Reconstruct the original script's computed results (distinct from prose claims).
    original=pd.read_csv(io.StringIO(git_text('data/player_segments.csv')))
    legacy_ab={}
    critical=number(stats_script,r'\(p1 - p2\) - ([\d.]+) \* se_diff')
    for name,col in [('D1','retention_1_int'),('D7','retention_7_int')]:
        control=original.loc[original.version.eq('gate_30'),col]
        test=original.loc[original.version.eq('gate_40'),col]
        p0,p1=control.mean(),test.mean()
        pool=(control.sum()+test.sum())/len(original)
        z=(p0-p1)/np.sqrt(pool*(1-pool)*(1/len(control)+1/len(test)))
        se=np.sqrt(p0*(1-p0)/len(control)+p1*(1-p1)/len(test))
        legacy_ab[name]={'difference':float(p0-p1),'z':float(z),
            'p_two_sided':float(2*(1-stats.norm.cdf(abs(z)))),
            'ci95':[float(p0-p1-critical*se),float(p0-p1+critical*se)]}
        if name=='D7':
            legacy_ab[name]['odds_ratio']=float((p0/(1-p0))/(p1/(1-p1)))
    baseline['legacy_computed_ab']=legacy_ab
    model=[]
    deciles=[]
    for line in report.splitlines():
        if re.match(r'\| \*\*\$K=\d',line):
            cells=line.split('|')[1:-1]
            k=int(re.search(r'K=(\d+)',cells[0]).group(1))
            values=[float(re.search(r'[\d,]+(?:\.\d+)?',v).group().replace(',','')) for v in cells[1:]]
            model.append(dict(zip(['k','inertia','silhouette','calinski_harabasz','davies_bouldin'],[k]+values)))
        if line.startswith('| **Decile '):
            cells=line.split('|')[1:-1]
            d=int(re.search(r'Decile (\d+)',cells[0]).group(1))
            values=[float(re.search(r'[\d,]+(?:\.\d+)?',v).group().replace(',','')) for v in cells[1:]]
            row=dict(zip(['decile','n','min_rounds','max_rounds','rounds','rounds_share','cumulative_rounds_share'],[d]+values))
            row['rounds_share']/=100
            row['cumulative_rounds_share']/=100
            deciles.append(row)
    baseline['legacy_model_evaluations']=model
    baseline['legacy_deciles']=deciles
    # Distinguish hand-written report tables from the saved original data.
    reported_segments=[]
    section=report.split('#### 1. Comprehensive Segment Retention & Value Distribution')[1].split('#### 2.')[0]
    for line in section.splitlines():
        if line.startswith('| **') and 'Total /' not in line:
            cells=line.split('|')[1:-1]
            values=[float(re.search(r'[\d,]+(?:\.\d+)?',v).group().replace(',','')) for v in cells[1:]]
            row=dict(zip(['n','size_share','rounds','rounds_share','mean_rounds','median_rounds','d1','d7'],values))
            for key in ['size_share','rounds_share','d1','d7']: row[key]/=100
            reported_segments.append(row)
    baseline['legacy_reported_segments']=reported_segments
    split=[]
    section=report.split('#### 3. A/B Gate Placement Sensitivity Within Segments')[1].split('## Generated')[0]
    for line in section.splitlines():
        if line.startswith('| **'):
            cells=line.split('|')[2:6]
            values=[float(re.search(r'[\d,]+(?:\.\d+)?',v).group().replace(',','')) for v in cells]
            split.append(dict(zip(['gate30_n','gate40_n','gate30_mean_rounds','gate40_mean_rounds'],values)))
    baseline['legacy_reported_segment_versions']=split
    baseline['legacy_table_numbers']=tables
    save_json(OUT/'audit_baseline.json',baseline)

if __name__=='__main__':
    main()

