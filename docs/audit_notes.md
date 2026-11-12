# Audit before implementation

The baseline is identified in `outputs/metrics.json` under `audit.baseline_commit`. All original scripts, SQL, README and master report were reviewed before analysis edits. Original claims remain inspectable in Git; their numeric tokens and locations are captured programmatically in `audit.legacy_numeric_claims`. The audit script also captures the original segment profiles directly from the baseline dataset.

## Provenance

The setup script names a public GitHub CSV and downloads only if the local file does not exist. Comparing the bytes shows the checked-in raw file is an **exact prefix** of that source, ending inside the version field of its final row. This establishes truncation, not a documented random sample. The acquisition date and cause of truncation cannot be recovered from the repository. The source and local row counts, byte lengths, hashes and maxima are recorded under `audit` in metrics.json. The old cleaning script excludes invalid versions and null measurements, but does not trim, cap or remove valid high-round records. The smaller maximum is a property of the truncated prefix, not evidence of an outlier-removal policy. The raw file will remain unchanged. Generalization to the full experiment is limited.

## Statistical errors and unsupported inference

- The large chi-square and Cramer's V used in the original headline refer to **engagement tier versus D7**, not version versus D7. The promotional bullet incorrectly attaches this association test to the A/B experiment.
- The headline A/B p-value is one-sided. The script actually calculates a two-sided z-test; the master report records both. The script's hardcoded positive interval and significance statement contradict its computed interval, and it switches the significance threshold after seeing results. Corrected exact values will be generated in the statistical analysis section of metrics.json.
- D1 and D7 were tested without multiplicity adjustment. Neither a planned directional hypothesis nor an original experiment protocol is provided. SRM, odds-ratio intervals and bootstrap D1 intervals were missing.
- Bootstrap replicates are a sampling distribution, not a Bayesian posterior. Their positive share is not a probability that a hypothesis is true. The previous resample count and fixed annotations cannot support certainty or practical/business value.
- Engagement overlaps the retention observation window. Association does not show that more rounds cause retention, that thresholds create habits, or that tiers predict future retention.
- Comparing version counts inside outcome-defined segments does not demonstrate players lost due to treatment. Conditioning on post-assignment rounds or retention can introduce selection bias.
- D7 users need not have returned on D1. The ratio of marginal retention rates is not survival or conditional persistence. A proper descriptive nested funnel counts D1 AND D7; the D7-only group must also be disclosed.
- A nonsignificant D1 test is not proof of zero effect. Rounded equality is not exact equality. No level timestamps establish when gates were reached.
- No session data support day-zero binge, single-session fatigue, permanent churn, tutorial friction, content exhaustion, precise churn day, or intervention timing. Total rounds span the observation window.
- No monetization, cost or experimental intervention outcomes establish revenue, lifetime value, ROI, prevented losses, or operational impact. Industry benchmark claims are uncited.
- Independence and randomization are assumptions, not verified facts. Equal allocation is assumed for SRM, pending the missing protocol.

## Segmentation and descriptive inconsistencies

- Retention flags and a deterministic weighted sum of them enter K-means. Reported segment retention is therefore partly true by construction; the composite further weights retention. Standardization does not remove redundancy or confer unbiased geometry.
- The chosen cluster count is hardcoded; the report's own selection table has a higher silhouette at a different count. Claims of optimality and a peak at the chosen count are unsupported. Final fit settings differ from candidate-evaluation settings.
- Cluster IDs are assigned fixed persona labels without deriving names from their current profiles. IDs can permute with implementation/version changes.
- The selected clusters do not correspond to the four retention patterns: one unretained pattern is split, while D7-only and both are combined. Some D7 users also appear in the low-round cluster.
- The master report contains conflicting segment counts, validation indices, and expected-cell minima. The purported zero-retention group has nonzero D7 in its own table. Audit comparisons will retain baseline profiles and report corrected values rather than preserve prose claims.
- Handwritten segment total-rounds values also differ from the saved original segmented data, even when player counts agree. The numerical comparison distinguishes old reported tables from recomputed baseline profiles, including version splits.
- Concentration is descriptive; neither a power-law distribution nor an exact Pareto rule was fitted or tested. A log transform reduces skewness but does not establish normality.
- Zero rounds do not establish tutorial abandonment: some zero-round records have retention flags. Keep and flag this as a soft inconsistency.
- The top tier label overlaps its predecessor at the boundary; use an unambiguous strictly-greater label.

## Reproducibility and output defects

- The SQL runner duplicates SQL strings instead of executing the SQL file and prints validation success without parity tests. The summary question promises a median absent from the query.
- Quantile ranking has no deterministic tie-breaker. The displayed Pareto rows descend while their cumulative sum ascends, obscuring top-down concentration.
- Data checks omit duplicate enforcement, strict Boolean parsing, exact schema and integer validation. Generic Boolean casting can turn nonempty false strings into true. Broad silent row dropping could hide future corruption.
- There is no complete orchestration, metrics registry, output lineage, test suite, CI, workbook, or BI contract. Dependency lower bounds do not reproduce versions; an advertised statistics package is neither required nor used.
- Several figure annotations and dashboard values are handcoded. Existing scripts would regenerate obsolete conclusions after documentation edits alone.
- The README's license badge targets a missing file. The master report has stale status, duplicated and broken sections, and machine-local links. Role-specific marketing and interview material obscure the analytical evidence.

## Resolution policy

Use the checked-in prefix, explicitly quarantine only its evidenced incomplete trailing record, fail on unexpected hard-rule violations, retain valid outliers, and disclose provenance. Use two-sided tests with a declared family correction; keep association separate. Make descriptive rule cohorts primary and label all post-treatment segment comparisons noncausal. Generate all results and reporting from metrics.json. Numerical comparison tables are generated after the corrected run.

<!-- VERIFIED_AUDIT:START -->
## Verified numerical appendix

Generated from metrics.json after the corrected implementation:

- Local raw records: 31,332; accepted complete records: 31,331; source records: 90,189.
- Exact byte prefix: True; local/source byte sizes: 933,888 / 2,707,297. Local/source maximum rounds: 2,961 / 49,854. No valid outliers were excluded.
- Engagement-tier versus D7 association: chi-square 11393.734024, Cramer's V 0.603040; the numerical p-value underflows. This is not the gate-assignment test.
- D7 gate-assignment test: two-sided p 0.09944584; exploratory one-sided p 0.04972292; Holm p 0.19889168. Conclusion: directionally negative, not conclusive at 5%.
- The association table's minimum expected cell is 56.153490, correcting the original reported value of 256.200000.

The complete original-versus-corrected numerical tables are in [metric_comparison.md](../outputs/metric_comparison.md).
<!-- VERIFIED_AUDIT:END -->
