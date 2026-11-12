# Methodology

## Scope, evidence and data lineage

This is retrospective product analytics on Cookie Cats. The input has one record per player. The source is the [CSV named by the original setup script](https://raw.githubusercontent.com/ryanschaub/Mobile-Games-A-B-Testing-with-Cookie-Cats/master/cookie_cats.csv). Its retrieved byte hash is 5ab54d761fbddcd50de7b88e4eaf7837cba4569474f50c043a4d17ee342c46bd; the checked-in raw hash is f6a85f5f022c7dd2bcf06e16abe7767fa8cb54287089058526f45092ef1d3c52. The local file contains 31,332 records versus 90,189 source records and is an exact byte prefix. The final row is incomplete. Acquisition date and interruption mechanism are unknown.

The original cleaner did not trim high-round observations. The accepted prefix has maximum 2,961 rounds; the reference source maximum is 49,854. Neither maximum should be silently substituted for the other. A future complete-data analysis would be a different population and must be labeled separately.

The stated observation window is 14 days. The file lacks timestamps to independently verify it, exact day boundaries, or experiment duration. Supplied retention flags represent return on the named milestone, not activity throughout an interval. Independent players and original random assignment are assumptions.

## Quality and business definitions

See [business rules](business_rules.md). Only the exact evidenced trailing row is quarantined under a raw-hash guard. Schema, missing data, normalized duplicate keys, integer domains, valid version values and binary flags are hard checks. Valid outliers are retained. The upper IQR fence is 120.00 rounds, flagging 3,491 records; 44 zero-round records have a return flag. These are soft warnings, not exclusions.

Raw staging and accepted SQL tables are distinct. CSV schemas, counts, totals and hashes are reconciled across outputs. No type cast is allowed to silently turn an arbitrary nonempty string into a true retention flag.

## Primary descriptive segmentation

Primary cohorts are none, D1 only, D7 only and both, optionally crossed with explicit engagement tiers. These patterns exhaust the accepted population. Their retention rates are true by definition. They describe completed outcomes and cannot support pre-outcome targeting.

Profiles report count, size share, rounds share, mean, median, distribution summaries, marginal D1/D7, version counts/shares, and test-minus-control differences with marginal intervals. Cohorts and tiers are post-assignment variables. Their within-group contrasts are descriptive and vulnerable to selection bias; intervals do not restore randomization. Outcome-fixed rates remain non-predictive even where the score interval has nonzero width. Missing arms produce unavailable effects.

The nested descriptive funnel is all players, D1, then D1 AND D7. D7-only players are reported separately. This avoids falsely treating the ratio of marginal D7 and D1 rates as conditional persistence or continuous survival.

## Secondary K-means

Features are log1p(rounds), D1, D7, and their weighted composite. StandardScaler centers and scales each feature. The log transform reduces extreme influence but does not prove normality. The composite repeats retention information and increases its weight; scaling does not remove that redundancy.

Candidate cluster counts run from 2 through 7, using consistent fit settings and seed 42. The retained cluster count is 4 for legacy comparability, not claimed optimal. Diagnostics include inertia, silhouette, Calinski-Harabasz and Davies-Bouldin. Silhouette uses a fixed subsample of 3,000 players for manageable runtime; this differs from the original diagnostic sample.

Adjusted Rand index is 0.675512 against rule cohorts and 0.493455 against cohort-by-tier groups. ARI compares partitions after accounting for chance and is label-permutation invariant; it does not establish causal or predictive validity. [scikit-learn reference](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.adjusted_rand_score.html)

Cluster names are neutral and ordered by mean rounds, independent of arbitrary fit label IDs. PCA is a visualization of the same features, not independent validation. Profiles remain partly true by construction because they report outcomes used for clustering.

## Retrospective A/B analysis plan

Declared before executing the corrected analysis: primary two-sided pooled two-proportion z tests, alpha 0.05, and Holm correction across D1, D7. This is not an original preregistration. The reported effect is always gate_40 minus gate_30; relative lift divides by the gate_30 rate. Odds ratios use gate_40 over gate_30.

For successes x and denominators n, estimate each arm rate x/n. The pooled null standard error uses pooled rate times its complement, multiplied by the sum of reciprocal arm sizes. The z statistic is the test-minus-control difference divided by that error. Two-sided p uses both normal tails. The exploratory one-sided alternative is gate_40 lower than gate_30, fixed independently of the observed sign.

Pearson contingency tests use no continuity correction. For these binary outcomes their statistic equals the squared pooled z statistic. Pearson chi-square itself is nondirectional; a directional tail is calculated from its signed square root and clearly labeled. These cross-checks are the same tests, not additional family members. [SciPy reference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html)

Holm sorts the two primary p-values, multiplies each by the remaining family size, takes a cumulative maximum and caps at unity. Decisions use adjusted p-values. Neither metric is declared significant merely because an exploratory directional p-value is small.

## Intervals and bootstrap

Difference intervals are 95% Newcombe independent Wilson-score intervals without continuity correction. Form Wilson bounds in each arm; combine the appropriate squared distances from the arm estimates to their bounds to obtain the difference bounds. This avoids zero-width Wald intervals at all-zero or all-one rates. [Method reference](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.confint_proportions_2indep.html)

Odds-ratio intervals are log-Wald, using the square root of the sum of reciprocal contingency cells. If any cell is zero, add a half to every cell and record that correction. All reported intervals are marginal, not simultaneous family-adjusted intervals.

The independent empirical bootstrap uses 10,000 resamples and seed 42 for D1, advancing the seed for D7. Resampling binary empirical observations is exactly equivalent to drawing retained counts from a binomial with the observed arm probability and original arm size. This avoids allocating a large replicate-by-player matrix. Percentile bounds form the bootstrap CI. The share of replicates where gate_30 D7 exceeds gate_40 is a sampling-distribution summary, not a probability that a hypothesis is true.

## Separate association test and allocation diagnostic

Engagement tier versus D7 has Pearson chi-square 11393.734024, degrees of freedom 6, Cramer's V 0.603040, and minimum expected cell 56.153490. The computed p-value underflows floating-point precision; it is not exactly zero. Cramer's V divides chi-square by sample size and the smaller contingency dimension minus unity, then takes the square root. Pearson residuals are observed minus expected, divided by the square root of expected.

These are concurrent variables over an overlapping window. Association cannot identify an intervention threshold or establish that activity causes return. None of these association numbers are evidence for gate assignment.

SRM compares observed version counts with assumed equal assignment: p = 0.615099. The original allocation protocol is missing. A nonsignificant diagnostic cannot establish randomness or representativeness of the truncated prefix.

## SQL, Excel and BI validation

Every SQL question is executed from the SQL file, not duplicated SQL strings. Independent pandas calculations match all 10 queries. Deciles rank rounds descending with userid ascending as deterministic tie-breaker, allocating the remainder to the earliest groups. Cumulative share runs from highest to lowest activity.

Excel summaries are live formulas over a native Data table. Preview caches come from the same aggregate metrics and are checked independently against formulas and data. Derived cohort/tier/decile classifications are fixed at generation time; refresh the pipeline after underlying data changes. There are native charts and instructions for manually adding a PivotTable, but no prebuilt PivotTables. Native recalculation status: skipped: LibreOffice unavailable. Native Excel rendering has not been verified.

BI files have explicit grains, keys, hashes and reconciliation totals. Full-sample inference tables are disconnected from interactive subgroup filters. DAX is provided as authored measures, not as an executed or validated Power BI model.

## Decision limits

The evidence supports description, uncertainty assessment and follow-up questions. It does not establish revenue impact, fatigue, exact churn timing, lifetime value, causal subgroup effects or intervention ROI. No timestamps support a longitudinal performance dashboard or before/after study. The brief recommends validating the complete experiment and defining the next decision threshold.

See [full statistical results](../outputs/statistical_results.md), [generated comparison](../outputs/metric_comparison.md), and [audit notes](audit_notes.md).
