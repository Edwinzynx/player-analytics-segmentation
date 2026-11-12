"""Retrospective plan: two-sided tests, alpha=.05, Holm family D1 + D7.

Effect convention: gate_40 minus gate_30. One-sided gate_40 < gate_30 tests
are exploratory. Pearson chi-square is nondirectional: its directional
tail uses the signed square root, rather than blindly halving its p-value.
"""
import numpy as np
import pandas as pd
from scipy import stats
from common import ALPHA, BOOTSTRAPS, SEED, TIERS, load_players, update_metrics

def wilson(x, n):
    if not n:
        return (None, None)
    z = stats.norm.ppf(1 - ALPHA / 2)
    p = x / n
    center = (p + z*z/(2*n)) / (1 + z*z/n)
    half = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1 + z*z/n)
    return float(center-half), float(center+half)

def difference(x0, n0, x1, n1):
    """Newcombe independent Wilson-score interval, no continuity correction."""
    if not n0 or not n1:
        return {'difference': None, 'ci95': [None, None], 'status': 'missing arm'}
    p0, p1 = x0/n0, x1/n1
    l0, u0 = wilson(x0, n0)
    l1, u1 = wilson(x1, n1)
    delta = p1-p0
    return {'difference': delta,
            'ci95': [delta - np.sqrt((p1-l1)**2+(u0-p0)**2),
                     delta + np.sqrt((u1-p1)**2+(p0-l0)**2)],
            'status': 'descriptive'}

def test_metric(df, col, seed=SEED):
    a = df.loc[df.version.eq('gate_30'), col]
    b = df.loc[df.version.eq('gate_40'), col]
    n0, n1, x0, x1 = len(a), len(b), int(a.sum()), int(b.sum())
    p0, p1 = x0/n0, x1/n1
    pooled = (x0+x1)/(n0+n1)
    z = (p1-p0)/np.sqrt(pooled*(1-pooled)*(1/n0+1/n1))
    chi, pchi, _, expected = stats.chi2_contingency([[x0,n0-x0],[x1,n1-x1]], correction=False)
    signed_root = np.copysign(np.sqrt(chi), p1-p0)
    # Exact empirical binary bootstrap using binomial counts, without huge arrays.
    rng = np.random.default_rng(seed)
    boot = rng.binomial(n1,p1,BOOTSTRAPS)/n1 - rng.binomial(n0,p0,BOOTSTRAPS)/n0
    cells = np.array([x1,n1-x1,x0,n0-x0], dtype=float)
    corrected = bool((cells == 0).any())
    if corrected:
        cells += 0.5
    odds = cells[0]*cells[3]/(cells[1]*cells[2])
    se = np.sqrt((1/cells).sum())
    critical = stats.norm.ppf(1-ALPHA/2)
    return dict(n_gate30=n0,n_gate40=n1,retained_gate30=x0,retained_gate40=x1,
        rate_gate30=p0,rate_gate40=p1,**difference(x0,n0,x1,n1),
        z=float(z),p_two_sided=float(2*stats.norm.sf(abs(z))),
        p_one_sided_gate40_lower=float(stats.norm.cdf(z)),
        chi_square=float(chi),chi_p_two_sided=float(pchi),
        chi_directional_p_gate40_lower=float(stats.norm.cdf(signed_root)),
        min_expected=float(expected.min()),relative_lift=p1/p0-1,
        odds_ratio=float(odds),odds_ci95=list(np.exp(np.log(odds)+np.array([-1,1])*critical*se)),
        odds_zero_cell_correction=corrected,
        bootstrap_ci95=list(np.quantile(boot,[ALPHA/2,1-ALPHA/2])),
        bootstrap_mean=float(boot.mean()),
        bootstrap_share_gate30_exceeds_gate40=float((boot<0).mean()),
        bootstrap_differences=boot.tolist())

def analyze(df):
    results = {name:test_metric(df,col,SEED+i) for i,(name,col) in enumerate(
        [('D1','retention_1'),('D7','retention_7')])}
    ordered = sorted(results, key=lambda k:results[k]['p_two_sided'])
    running = 0.0
    for rank,name in enumerate(ordered):
        r = results[name]
        running = max(running, min(1.0,(len(ordered)-rank)*r['p_two_sided']))
        r['p_holm'] = running
        r['significant_holm'] = bool(running < ALPHA)
        direction = 'negative' if r['difference'] < 0 else 'positive'
        r['conclusion'] = (direction + ' and significant after Holm' if r['significant_holm']
            else 'directionally ' + direction + ', not conclusive at 5%')
    counts = df.version.value_counts().reindex(['gate_30','gate_40'])
    srm = stats.chisquare(counts.to_numpy())
    table = pd.crosstab(df.tier,df.retention_7).reindex(TIERS)
    chi,p,dof,expected = stats.chi2_contingency(table,correction=False)
    association = {'chi_square':float(chi),'p_value':float(p),'p_underflow':bool(p==0),
        'df':int(dof),'cramers_v':float(np.sqrt(chi/len(df))),
        'min_expected':float(expected.min()),'observed':table.values.tolist(),
        'expected':expected.tolist(),'pearson_residuals':((table.values-expected)/np.sqrt(expected)).tolist()}
    return {'ab':results,'association':association,
        'srm':{'chi_square':float(srm.statistic),'p_value':float(srm.pvalue),
            'expected_allocation':[0.5,0.5],'allocation_assumption':'equal assignment; original protocol unavailable'},
        'analysis_plan':{'alpha':ALPHA,'primary':'two-sided pooled two-proportion z tests',
            'family':['D1','D7'],'adjustment':'Holm','effect':'gate_40 minus gate_30',
            'difference_ci':'Newcombe independent Wilson-score, no continuity correction',
            'odds_ci':'log-Wald; add 0.5 to all cells only if any is zero',
            'bootstrap':'independent empirical binary bootstrap via equivalent binomial counts',
            'resamples':BOOTSTRAPS,'seed':SEED,'ci_level':1-ALPHA,
            'one_sided':'exploratory gate_40 < gate_30; directional Pearson tail from signed root',
            'retrospective':True}}

def main():
    result = analyze(load_players())
    update_metrics(**result)
    print({k:{x:v for x,v in r.items() if x in ['difference','p_two_sided','p_holm','conclusion']} for k,r in result['ab'].items()})

if __name__ == '__main__':
    main()

