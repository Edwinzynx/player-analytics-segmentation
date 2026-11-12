# Product retention and activity: decision brief

**Context.** Evaluate gate placement and describe retention/activity patterns in Cookie Cats. This analysis covers 31,331 accepted players from a truncated prefix of a 90,189-row source. It is a reproducible portfolio analysis, with no claim of business intervention impact.

**Gate placement remains uncertain.** D7 retention is 19.02% under gate_30 and 18.29% under gate_40. The difference is -0.725 percentage points, with a confidence interval of [-1.588, 0.138] percentage points. Two-sided p = 0.09945; Holm-adjusted p = 0.19889. **So what:** directionally negative, not conclusive at 5%. **Recommendation:** do not justify a rollout or rollback from this prefix alone; obtain the complete validated experiment and define a practical decision threshold before a confirmatory test.

**Observed return patterns identify a question, not a diagnosis.** The D1-only cohort contains 9,398 players (30.00%). **So what:** returning at the first milestone does not guarantee return at the later milestone; the cohort's rates are fixed by its definition. **Recommendation:** investigate the intervening experience using timestamped events, then test a targeted intervention using features available before the outcome.

**Activity is concentrated.** The highest-round decile contains 3,134 players (10.00%) and accounts for 55.55% of rounds. **So what:** average activity can conceal distinct usage patterns. **Recommendation:** track distribution and cohort mix alongside mean activity; do not equate rounds with revenue or customer value.

**Engagement and return are associated.** Engagement tier versus D7 has Cramer's V = 0.603. **So what:** high activity and retention occur together during the same observation window. This is separate from the A/B test. **Recommendation:** use tiers for descriptive reporting and formulate prospective hypotheses rather than claim causal thresholds.

**Caveats and next steps.** The source is truncated, acquisition history and assignment protocol are unavailable, and the stated 14-day window cannot be verified from timestamps. No revenue, session or cost data are present. Post-assignment cohorts cannot identify causal subgroup effects. Recover the complete source under a separate approved data change, verify assignment and outcome definitions, and rerun quality checks and reconciliations. The Excel workbook and BI exports provide a repeatable snapshot, not a time-series performance dashboard.

Source: all empirical values are generated from `outputs/metrics.json`; methods and marginal interval level are defined in `outputs/statistical_results.md`.
