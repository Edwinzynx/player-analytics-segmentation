"""Render statistical evidence only from metrics.json."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from common import metrics, OUT, TIERS

def main():
    m=metrics()
    lines=['# Statistical results','',
        'Primary: two-sided pooled z tests; Holm correction across D1 and D7. '
        'The plan is retrospective, declared before this corrected run, not an original preregistration.',
        f"Alpha: {m['analysis_plan']['alpha']}. Effects and all intervals: gate_40 minus gate_30. "
        'Difference CI: Newcombe independent Wilson score. Odds ratio: gate_40 / gate_30; log-Wald CI. '
        'Intervals are marginal, not simultaneous family-adjusted intervals.','',
        '| Metric | Gate 30 | Gate 40 | Difference (pp), CI | Relative lift | OR, CI | z | Two-sided p | One-sided p | Holm p |',
        '|---|---:|---:|---|---:|---|---:|---:|---:|---:|']
    for name,r in m['ab'].items():
        lines.append(f"| {name} | {r['rate_gate30']:.4%} | {r['rate_gate40']:.4%} | {100*r['difference']:.4f} [{100*r['ci95'][0]:.4f}, {100*r['ci95'][1]:.4f}] | {r['relative_lift']:.4%} | {r['odds_ratio']:.5f} [{r['odds_ci95'][0]:.5f}, {r['odds_ci95'][1]:.5f}] | {r['z']:.5f} | {r['p_two_sided']:.6f} | {r['p_one_sided_gate40_lower']:.6f} | {r['p_holm']:.6f} |")
    lines += ['', '## Pearson cross-check and empirical bootstrap', '',
        'Pearson chi-square has no intrinsic direction. The exploratory directional p-value uses its signed square root, with gate_40 < gate_30 fixed as the alternative.',
        f"Independent empirical bootstrap: {m['analysis_plan']['resamples']:,} replicates, seed {m['analysis_plan']['seed']} (D7 uses the next seed). Binomial draws exactly reproduce resampling binary outcomes within each arm.",'']
    for name,r in m['ab'].items():
        lines += [f"- {name}: Pearson chi-square {r['chi_square']:.6f}; two-sided p {r['chi_p_two_sided']:.6f}; signed-root directional p {r['chi_directional_p_gate40_lower']:.6f}; minimum expected cell {r['min_expected']:.3f}. Bootstrap CI (pp) [{100*r['bootstrap_ci95'][0]:.4f}, {100*r['bootstrap_ci95'][1]:.4f}]; share of resamples where gate_30 exceeds gate_40 {r['bootstrap_share_gate30_exceeds_gate40']:.2%}. Conclusion: {r['conclusion']}."]
    a=m['association']
    lines += ['', '## Engagement-tier association with D7 (not the A/B test)', '',
        f"Pearson chi-square {a['chi_square']:.6f}, df {a['df']}, Cramer's V {a['cramers_v']:.6f}; minimum expected cell {a['min_expected']:.3f}.",
        ('The computed p-value underflows double precision; it is not exactly zero.' if a['p_underflow'] else f"p = {a['p_value']:.6g}."),
        'This is concurrent association across the observation window, not evidence that raising activity improves retention. Independence is assumed, not verified.',
        '', '## Sample ratio mismatch','',
        f"Assuming equal assignment, chi-square {m['srm']['chi_square']:.6f}, p {m['srm']['p_value']:.6f}. A nonsignificant SRM check cannot establish randomization or eliminate prefix-selection bias."]
    (OUT/'statistical_results.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    fig,ax=plt.subplots(figsize=(9,5))
    values=np.asarray(a['pearson_residuals'])
    im=ax.imshow(values,cmap='RdBu_r',vmin=-abs(values).max(),vmax=abs(values).max(),aspect='auto')
    ax.set_yticks(range(len(TIERS)),TIERS); ax.set_xticks([0,1],['D7 absent','D7 present'])
    for i in range(len(TIERS)):
        for j in range(2):
            ax.text(j,i,f'{values[i,j]:.1f}',ha='center',va='center')
    ax.set_title("Engagement tier and D7: association, not treatment effect")
    fig.colorbar(im,ax=ax,label='Pearson residual'); fig.tight_layout()
    fig.savefig(OUT/'figures/13_statistical_chi_square_residuals.png',dpi=160); plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12,4))
    for ax,(name,r) in zip(axes,m['ab'].items()):
        ax.hist(np.asarray(r['bootstrap_differences'])*100,bins=40,color='#376a91')
        ax.axvline(0,color='black',ls='--')
        for limit in r['bootstrap_ci95']:
            ax.axvline(limit*100,color='#be7220',ls=':')
        ax.set(title=f'{name} bootstrap sampling distribution',xlabel='Gate 40 - Gate 30 (percentage points)',ylabel='Resamples')
    fig.tight_layout(); fig.savefig(OUT/'figures/14_ab_bootstrap_retention_distribution.png',dpi=160); plt.close(fig)

if __name__=='__main__':
    main()

