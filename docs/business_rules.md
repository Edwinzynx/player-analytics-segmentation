# Business rules and data contract

The unit is one player identified by a unique integer userid. Version is assigned gate_30 or gate_40. The raw artifact is immutable; its SHA-256 and accepted population are recorded in metrics.json.

D1 and D7 are the supplied flags indicating return one and seven days after installation. Exact calendar versus rolling-hour boundaries are not available. Neither flag measures continuous activity, permanent churn, or persistence through all intervening days. Rounds are cumulative over the stated fourteen-day observation window; the file has no timestamps to independently verify this window.

The four primary cohorts are none (neither flag), D1 only, D7 only, and both. Cohort crossed with tier provides descriptive detail. Retention rates inside these cohorts are fixed by the definition and cannot validate predictive usefulness. The nested descriptive funnel is all players, D1, then both D1 and D7; D7-only is reported separately.

Engagement tier boundaries are stored in metrics.json/data_contract/tier_bounds. Zero is separate; successive intervals are lower-exclusive and upper-inclusive, with the final tier strictly above the last boundary. These inherited thresholds are descriptive business rules, not optimized interventions.

Exclusions: quarantine only the exact incomplete trailing row in the hash-verified audited raw file. Every unexpected missing field, schema change, duplicate userid, invalid version, invalid Boolean, fractional count or negative count fails the run. No imputation, random sampling, high-round trimming or winsorization is performed. Data-quality output records the raw violations and accepted-data checks separately. Outliers above the upper Tukey IQR fence and zero-round players with retention are soft warnings and remain included.

Deciles rank rounds descending, breaking ties with userid ascending. The first groups receive the remainder when the population does not divide evenly. Decile one is the highest-round group. Decile membership is a fixed baseline classification; changing workbook rounds requires rerunning the pipeline to refresh ranks.

Rates use all accepted players in the relevant group as denominator. Share of rounds uses total accepted rounds. Primary treatment effects use test minus control; relative lift divides the difference by the control rate. All per-cohort, tier and cluster treatment contrasts are descriptive post-assignment comparisons. CIs do not make them causal. Missing treatment arms produce unavailable contrasts, not zeros. Small or outcome-fixed cohorts should not drive rollout decisions.

The analysis assumes independent players and valid original random assignment. The original assignment protocol, acquisition history and reason for file truncation are unavailable. Equal allocation is assumed only for the SRM diagnostic. Passing SRM does not establish sample representativeness.

No monetization, exposure timestamps, sessions, event dates, demographics, level progression or costs are available. Activity concentration is not revenue concentration. The retrospective rule cohorts cannot support prospective targeting without pre-outcome features. There is no time series for performance trends or before/after estimation; the dashboard is a reproducible snapshot.

