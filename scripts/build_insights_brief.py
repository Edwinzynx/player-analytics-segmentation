"""Concise stakeholder report, with every empirical value read from metrics.json."""
from common import metrics, OUT

def render(m):
    a=m['ab']['D7']; o=m['overall']; audit=m['audit']
    cohort=next(r for r in m['profiles']['cohort'] if r['cohort']=='D1 only')
    top=m['profiles']['decile'][0]
    return f"""# Product retention and activity: decision brief

**Context.** Evaluate gate placement and describe retention/activity patterns in Cookie Cats. This analysis covers {o['n']:,} accepted players from a truncated prefix of a {audit['source_rows']:,}-row source. It is a reproducible portfolio analysis, with no claim of business intervention impact.

**Gate placement remains uncertain.** D7 retention is {a['rate_gate30']:.2%} under gate_30 and {a['rate_gate40']:.2%} under gate_40. The difference is {100*a['difference']:.3f} percentage points, with a confidence interval of [{100*a['ci95'][0]:.3f}, {100*a['ci95'][1]:.3f}] percentage points. Two-sided p = {a['p_two_sided']:.5f}; Holm-adjusted p = {a['p_holm']:.5f}. **So what:** {a['conclusion']}. **Recommendation:** do not justify a rollout or rollback from this prefix alone; obtain the complete validated experiment and define a practical decision threshold before a confirmatory test.

**Observed return patterns identify a question, not a diagnosis.** The D1-only cohort contains {cohort['n']:,} players ({cohort['size_share']:.2%}). **So what:** returning at the first milestone does not guarantee return at the later milestone; the cohort's rates are fixed by its definition. **Recommendation:** investigate the intervening experience using timestamped events, then test a targeted intervention using features available before the outcome.

**Activity is concentrated.** The highest-round decile contains {top['n']:,} players ({top['size_share']:.2%}) and accounts for {top['rounds_share']:.2%} of rounds. **So what:** average activity can conceal distinct usage patterns. **Recommendation:** track distribution and cohort mix alongside mean activity; do not equate rounds with revenue or customer value.

**Engagement and return are associated.** Engagement tier versus D7 has Cramer's V = {m['association']['cramers_v']:.3f}. **So what:** high activity and retention occur together during the same observation window. This is separate from the A/B test. **Recommendation:** use tiers for descriptive reporting and formulate prospective hypotheses rather than claim causal thresholds.

**Caveats and next steps.** The source is truncated, acquisition history and assignment protocol are unavailable, and the stated {m['data_contract']['observation_days']}-day window cannot be verified from timestamps. No revenue, session or cost data are present. Post-assignment cohorts cannot identify causal subgroup effects. Recover the complete source under a separate approved data change, verify assignment and outcome definitions, and rerun quality checks and reconciliations. The Excel workbook and BI exports provide a repeatable snapshot, not a time-series performance dashboard.

Source: all empirical values are generated from `outputs/metrics.json`; methods and marginal interval level are defined in `outputs/statistical_results.md`.
"""

def main():
    (OUT/'insights_brief.md').write_text(render(metrics()),encoding='utf-8')

if __name__=='__main__':
    main()
