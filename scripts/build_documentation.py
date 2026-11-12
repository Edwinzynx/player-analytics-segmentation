"""Generate corrected technical documentation and complete numerical comparison tables."""
import math
from common import ROOT,OUT,metrics,update_metrics

def comparison(m):
    old=m['audit']['legacy_selected_claims']; a=m['ab']['D7']
    chosen=next(r for r in m['segmentation']['evaluations'] if r['k']==m['segmentation']['selected_k'])
    rows=[]
    def add(metric,before,after,note):
        rows.append({'metric':metric,'old':before,'new':after,'note':note})
    add('Headline D7 p-value',old['headline_d7_p'],a['p_two_sided'],'Old one-sided headline; new primary two-sided test')
    add('D7 exploratory one-sided p-value',old['headline_d7_p'],a['p_one_sided_gate40_lower'],'Same directional hypothesis; old rounded headline')
    add('D7 Holm p-value',None,a['p_holm'],'Not previously reported; adjusted across D1 and D7')
    add('D1 Holm p-value',None,m['ab']['D1']['p_holm'],'Not previously reported')
    add('D7 odds ratio',old['headline_odds_gate30_over_gate40'],a['odds_ratio'],'Old control/test; new test/control. Direction changed explicitly')
    add('D7 bootstrap positive-share (%)',old['headline_bootstrap_share_pct'],100*a['bootstrap_share_gate30_exceeds_gate40'],'Share where control exceeds test; not a hypothesis probability')
    add('Bootstrap resamples',old['old_bootstrap_iterations'],m['analysis_plan']['resamples'],'Fixed-seed binary empirical bootstrap')
    add('D7 script CI low (pp), control minus test',old['old_d7_script_ci_low_pp'],-100*a['ci95'][1],'Old hardcoded positive interval was incorrect; new Newcombe CI')
    add('D7 script CI high (pp), control minus test',old['old_d7_script_ci_high_pp'],-100*a['ci95'][0],'Same direction for comparison')
    add('D7 bootstrap mean (pp), control minus test',old['old_bootstrap_mean_pp'],-100*a['bootstrap_mean'],'New replicates and random generator')
    add('D7 bootstrap CI low (pp), control minus test',old['old_bootstrap_low_pp'],-100*a['bootstrap_ci95'][1],'Same direction for comparison')
    add('D7 bootstrap CI high (pp), control minus test',old['old_bootstrap_high_pp'],-100*a['bootstrap_ci95'][0],'Same direction for comparison')
    add('Association minimum expected cell',old['association_expected_min'],m['association']['min_expected'],'Corrected expected-cell audit')
    add('Headline secondary silhouette',old['headline_silhouette'],chosen['silhouette'],'New fixed diagnostic subsample size is disclosed')
    add('Conflicting validation CH claim',old['interview_calinski_harabasz'],chosen['calinski_harabasz'],'Original narrative contradicted its own model table')
    add('Conflicting validation DB claim',old['interview_davies_bouldin'],chosen['davies_bouldin'],'Original narrative contradicted its own model table')
    add('ARI: rule cohorts vs secondary clusters',None,m['segmentation']['ari_cohort'],'New agreement diagnostic; no predictive validation')
    add('ARI: cohort/tier vs secondary clusters',None,m['segmentation']['ari_cohort_tier'],'Different granularity, explicitly reported')
    add('SRM p-value',None,m['srm']['p_value'],'New diagnostic; equal allocation assumed')
    for metric in ['difference','relative_lift','z','p_two_sided','chi_square','chi_p_two_sided',
        'chi_directional_p_gate40_lower','odds_ratio','min_expected']:
        for name,result in m['ab'].items():
            legacy=m['audit']['legacy_computed_ab'][name].get(metric)
            add(name+' complete result: '+metric,legacy,result[metric],
                'Old computed test reconstructed with pinned runtime; old effects are control minus test, new test minus control; old odds control/test'
                if legacy is not None else 'Newly reported diagnostic; old source locations preserved in audit evidence')
    for name,result in m['ab'].items():
        legacy=m['audit']['legacy_computed_ab'][name]
        for index,bound in enumerate(['low','high']):
            add(name+' calculated difference CI '+bound+' (pp), control minus test',
                100*legacy['ci95'][index],-100*result['ci95'][1-index],
                'Original computed unpooled Wald vs corrected Newcombe; common orientation for comparison')
    for legacy in m['audit']['legacy_model_evaluations']:
        current=next(r for r in m['segmentation']['evaluations'] if r['k']==legacy['k'])
        for metric in ['inertia','silhouette','calinski_harabasz','davies_bouldin']:
            add(f"Secondary K={legacy['k']} {metric}",legacy[metric],current[metric],
                'Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding')
    for legacy in m['audit']['legacy_deciles']:
        current=m['profiles']['decile'][10-int(legacy['decile'])]
        for metric in ['n','min_rounds','max_rounds','rounds','rounds_share','cumulative_rounds_share']:
            add(f"Activity group: old decile {int(legacy['decile'])} / new {current['decile']}: {metric}",
                legacy[metric],current[metric],
                'Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down')
    old_groups=sorted(m['audit']['legacy_segments'].items(),key=lambda kv:kv[1]['mean_rounds'])
    for (label,legacy),current in zip(old_groups,m['profiles']['secondary_segment']):
        for metric in ['n','size_share','rounds_share','mean_rounds','median_rounds','d1','d7']:
            add(f"Legacy cluster {label} / secondary {current['secondary_segment']}: {metric}",
                legacy[metric],current[metric],'Like-for-like secondary profiles, including unchanged values')
    for legacy,current in zip(m['audit']['legacy_reported_segments'],m['profiles']['secondary_segment']):
        for metric,before in legacy.items():
            add(f"Original report / {current['secondary_segment']}: {metric}",before,current[metric],
                'Reported table vs recomputed secondary model; some original totals contradicted saved data')
    for legacy,current in zip(m['audit']['legacy_reported_segment_versions'],m['profiles']['secondary_segment']):
        for metric,before in legacy.items():
            add(f"Original version table / {current['secondary_segment']}: {metric}",before,current[metric],
                'Assignment counts and mean activity; no players-lost causal interpretation')
    # Primary cohorts are a different definition, so do not imply a one-to-one cluster mapping.
    for current in m['profiles']['cohort']:
        for metric in ['n','size_share','rounds_share','mean_rounds','median_rounds','d1','d7']:
            add(f"Primary cohort {current['cohort']}: {metric}",None,current[metric],
                'New rule definition; not directly comparable with a legacy cluster')
    return rows

def fmt(value):
    if value is None: return 'not previously reported / not comparable'
    if isinstance(value,str): return value
    return f'{value:,.6f}'.rstrip('0').rstrip('.')

def render_comparison(m):
    lines=['# Old and corrected numerical results','',
        'Generated from metrics.json, including the frozen audit evidence. Old values are parsed from the original documents or computed from the original segmented table, never retyped. '
        'This report includes unchanged secondary profiles to make the segmentation transition reviewable. Null old entries mean the old method did not supply a directly comparable statistic. '
        'Every original numerical claim also has a source line in audit.legacy_numeric_claims; numerical table snapshots are retained in audit.legacy_table_numbers.',
        '', 'The full accepted population and its unrounded marginal retention/activity totals are unchanged. '
        'The major changes are inferential interpretation, interval reporting, bootstrap method/count, primary segmentation, diagnostic subsampling and decile ordering. '
        'The complete primary and crossed-cohort profiles, version shares, and descriptive CIs are available in outputs/tables.','',
        '| Metric | Old | New | Explanation |','|---|---:|---:|---|']
    for row in m['comparison']:
        lines.append(f"| {row['metric']} | {fmt(row['old'])} | {fmt(row['new'])} | {row['note']} |")
    return '\n'.join(lines)+'\n'

def render_methodology(m):
    p=m['analysis_plan']; a=m['association']; s=m['segmentation']
    return f"""# Methodology

## Scope, evidence and data lineage

This is retrospective product analytics on Cookie Cats. The input has one record per player. The source is the [CSV named by the original setup script]({m['audit']['source_url']}). Its retrieved byte hash is {m['audit']['source_sha256']}; the checked-in raw hash is {m['audit']['raw_sha256']}. The local file contains {m['audit']['raw_rows']:,} records versus {m['audit']['source_rows']:,} source records and is an exact byte prefix. The final row is incomplete. Acquisition date and interruption mechanism are unknown.

The original cleaner did not trim high-round observations. The accepted prefix has maximum {m['overall']['max_rounds']:,} rounds; the reference source maximum is {m['audit']['source_max_rounds']:,}. Neither maximum should be silently substituted for the other. A future complete-data analysis would be a different population and must be labeled separately.

The stated observation window is {m['data_contract']['observation_days']} days. The file lacks timestamps to independently verify it, exact day boundaries, or experiment duration. Supplied retention flags represent return on the named milestone, not activity throughout an interval. Independent players and original random assignment are assumptions.

## Quality and business definitions

See [business rules](business_rules.md). Only the exact evidenced trailing row is quarantined under a raw-hash guard. Schema, missing data, normalized duplicate keys, integer domains, valid version values and binary flags are hard checks. Valid outliers are retained. The upper IQR fence is {m['data_quality']['outliers']['iqr_upper_fence']:.2f} rounds, flagging {m['data_quality']['outliers']['count']:,} records; {m['data_quality']['zero_rounds_with_retention']:,} zero-round records have a return flag. These are soft warnings, not exclusions.

Raw staging and accepted SQL tables are distinct. CSV schemas, counts, totals and hashes are reconciled across outputs. No type cast is allowed to silently turn an arbitrary nonempty string into a true retention flag.

## Primary descriptive segmentation

Primary cohorts are none, D1 only, D7 only and both, optionally crossed with explicit engagement tiers. These patterns exhaust the accepted population. Their retention rates are true by definition. They describe completed outcomes and cannot support pre-outcome targeting.

Profiles report count, size share, rounds share, mean, median, distribution summaries, marginal D1/D7, version counts/shares, and test-minus-control differences with marginal intervals. Cohorts and tiers are post-assignment variables. Their within-group contrasts are descriptive and vulnerable to selection bias; intervals do not restore randomization. Outcome-fixed rates remain non-predictive even where the score interval has nonzero width. Missing arms produce unavailable effects.

The nested descriptive funnel is all players, D1, then D1 AND D7. D7-only players are reported separately. This avoids falsely treating the ratio of marginal D7 and D1 rates as conditional persistence or continuous survival.

## Secondary K-means

Features are log1p(rounds), D1, D7, and their weighted composite. StandardScaler centers and scales each feature. The log transform reduces extreme influence but does not prove normality. The composite repeats retention information and increases its weight; scaling does not remove that redundancy.

Candidate cluster counts run from {min(r['k'] for r in s['evaluations'])} through {max(r['k'] for r in s['evaluations'])}, using consistent fit settings and seed {p['seed']}. The retained cluster count is {s['selected_k']} for legacy comparability, not claimed optimal. Diagnostics include inertia, silhouette, Calinski-Harabasz and Davies-Bouldin. Silhouette uses a fixed subsample of {s['silhouette_sample_size']:,} players for manageable runtime; this differs from the original diagnostic sample.

Adjusted Rand index is {s['ari_cohort']:.6f} against rule cohorts and {s['ari_cohort_tier']:.6f} against cohort-by-tier groups. ARI compares partitions after accounting for chance and is label-permutation invariant; it does not establish causal or predictive validity. [scikit-learn reference](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.adjusted_rand_score.html)

Cluster names are neutral and ordered by mean rounds, independent of arbitrary fit label IDs. PCA is a visualization of the same features, not independent validation. Profiles remain partly true by construction because they report outcomes used for clustering.

## Retrospective A/B analysis plan

Declared before executing the corrected analysis: primary two-sided pooled two-proportion z tests, alpha {p['alpha']}, and Holm correction across {', '.join(p['family'])}. This is not an original preregistration. The reported effect is always gate_40 minus gate_30; relative lift divides by the gate_30 rate. Odds ratios use gate_40 over gate_30.

For successes x and denominators n, estimate each arm rate x/n. The pooled null standard error uses pooled rate times its complement, multiplied by the sum of reciprocal arm sizes. The z statistic is the test-minus-control difference divided by that error. Two-sided p uses both normal tails. The exploratory one-sided alternative is gate_40 lower than gate_30, fixed independently of the observed sign.

Pearson contingency tests use no continuity correction. For these binary outcomes their statistic equals the squared pooled z statistic. Pearson chi-square itself is nondirectional; a directional tail is calculated from its signed square root and clearly labeled. These cross-checks are the same tests, not additional family members. [SciPy reference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html)

Holm sorts the two primary p-values, multiplies each by the remaining family size, takes a cumulative maximum and caps at unity. Decisions use adjusted p-values. Neither metric is declared significant merely because an exploratory directional p-value is small.

## Intervals and bootstrap

Difference intervals are {p['ci_level']:.0%} Newcombe independent Wilson-score intervals without continuity correction. Form Wilson bounds in each arm; combine the appropriate squared distances from the arm estimates to their bounds to obtain the difference bounds. This avoids zero-width Wald intervals at all-zero or all-one rates. [Method reference](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.confint_proportions_2indep.html)

Odds-ratio intervals are log-Wald, using the square root of the sum of reciprocal contingency cells. If any cell is zero, add a half to every cell and record that correction. All reported intervals are marginal, not simultaneous family-adjusted intervals.

The independent empirical bootstrap uses {p['resamples']:,} resamples and seed {p['seed']} for D1, advancing the seed for D7. Resampling binary empirical observations is exactly equivalent to drawing retained counts from a binomial with the observed arm probability and original arm size. This avoids allocating a large replicate-by-player matrix. Percentile bounds form the bootstrap CI. The share of replicates where gate_30 D7 exceeds gate_40 is a sampling-distribution summary, not a probability that a hypothesis is true.

## Separate association test and allocation diagnostic

Engagement tier versus D7 has Pearson chi-square {a['chi_square']:.6f}, degrees of freedom {a['df']}, Cramer's V {a['cramers_v']:.6f}, and minimum expected cell {a['min_expected']:.6f}. The computed p-value underflows floating-point precision; it is not exactly zero. Cramer's V divides chi-square by sample size and the smaller contingency dimension minus unity, then takes the square root. Pearson residuals are observed minus expected, divided by the square root of expected.

These are concurrent variables over an overlapping window. Association cannot identify an intervention threshold or establish that activity causes return. None of these association numbers are evidence for gate assignment.

SRM compares observed version counts with assumed equal assignment: p = {m['srm']['p_value']:.6f}. The original allocation protocol is missing. A nonsignificant diagnostic cannot establish randomness or representativeness of the truncated prefix.

## SQL, Excel and BI validation

Every SQL question is executed from the SQL file, not duplicated SQL strings. Independent pandas calculations match all {m['sql_validation']['query_count']} queries. Deciles rank rounds descending with userid ascending as deterministic tie-breaker, allocating the remainder to the earliest groups. Cumulative share runs from highest to lowest activity.

Excel summaries are live formulas over a native Data table. Preview caches come from the same aggregate metrics and are checked independently against formulas and data. Derived cohort/tier/decile classifications are fixed at generation time; refresh the pipeline after underlying data changes. There are native charts and instructions for manually adding a PivotTable, but no prebuilt PivotTables. Native recalculation status: {m['excel']['native_recalculation']}. Native Excel rendering has not been verified.

BI files have explicit grains, keys, hashes and reconciliation totals. The native PBIP report contains a TMDL import model with embedded, portable snapshots. Full-sample inference tables are disconnected from interactive subgroup filters; the experiment page disables cross-visual filtering. The local Power BI engine validation record is stored in metrics.powerbi.engine_validation and [the native validation report](../outputs/powerbi/validation.md). Archived evidence is reused only when model hashes match, and every DAX result is compared again against current pandas expectations. JSON schemas validate the report definitions. Visual rendering has not been reviewed because the computer-use runtime could not initialize; schema and engine checks do not establish visual quality.

## Decision limits

The evidence supports description, uncertainty assessment and follow-up questions. It does not establish revenue impact, fatigue, exact churn timing, lifetime value, causal subgroup effects or intervention ROI. No timestamps support a longitudinal performance dashboard or before/after study. The brief recommends validating the complete experiment and defining the next decision threshold.

See [full statistical results](../outputs/statistical_results.md), [generated comparison](../outputs/metric_comparison.md), and [audit notes](audit_notes.md).
"""

def render_audit_verified(m):
    a=m['audit']; r=m['ab']['D7']; association=m['association']
    return f"""<!-- VERIFIED_AUDIT:START -->
## Verified numerical appendix

Generated from metrics.json after the corrected implementation:

- Local raw records: {a['raw_rows']:,}; accepted complete records: {a['complete_rows']:,}; source records: {a['source_rows']:,}.
- Exact byte prefix: {a['exact_byte_prefix']}; local/source byte sizes: {a['local_bytes']:,} / {a['source_bytes']:,}. Local/source maximum rounds: {a['local_max_rounds']:,} / {a['source_max_rounds']:,}. No valid outliers were excluded.
- Engagement-tier versus D7 association: chi-square {association['chi_square']:.6f}, Cramer's V {association['cramers_v']:.6f}; the numerical p-value underflows. This is not the gate-assignment test.
- D7 gate-assignment test: two-sided p {r['p_two_sided']:.8f}; exploratory one-sided p {r['p_one_sided_gate40_lower']:.8f}; Holm p {r['p_holm']:.8f}. Conclusion: {r['conclusion']}.
- The association table's minimum expected cell is {association['min_expected']:.6f}, correcting the original reported value of {a['legacy_selected_claims']['association_expected_min']:.6f}.

The complete original-versus-corrected numerical tables are in [metric_comparison.md](../outputs/metric_comparison.md).
<!-- VERIFIED_AUDIT:END -->
"""

def main():
    m=metrics()
    m=update_metrics(comparison=comparison(m))
    (OUT/'metric_comparison.md').write_text(render_comparison(m),encoding='utf-8')
    (ROOT/'docs/methodology.md').write_text(render_methodology(m),encoding='utf-8')
    path=ROOT/'docs/audit_notes.md'
    original=path.read_text(encoding='utf-8-sig').split('<!-- VERIFIED_AUDIT:START -->')[0].rstrip()
    path.write_text(original+'\n\n'+render_audit_verified(m),encoding='utf-8')

if __name__=='__main__':
    main()

