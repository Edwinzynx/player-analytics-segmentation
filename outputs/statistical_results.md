# Statistical results

Primary: two-sided pooled z tests; Holm correction across D1 and D7. The plan is retrospective, declared before this corrected run, not an original preregistration.
Alpha: 0.05. Effects and all intervals: gate_40 minus gate_30. Difference CI: Newcombe independent Wilson score. Odds ratio: gate_40 / gate_30; log-Wald CI. Intervals are marginal, not simultaneous family-adjusted intervals.

| Metric | Gate 30 | Gate 40 | Difference (pp), CI | Relative lift | OR, CI | z | Two-sided p | One-sided p | Holm p |
|---|---:|---:|---|---:|---|---:|---:|---:|---:|
| D1 | 44.6706% | 44.6722% | 0.0015 [-1.0993, 1.1024] | 0.0035% | 1.00006 [0.95649, 1.04562] | 0.00276 | 0.997802 | 0.501099 | 0.997802 |
| D7 | 19.0193% | 18.2941% | -0.7252 [-1.5879, 0.1375] | -3.8129% | 0.95333 [0.90064, 1.00911] | -1.64755 | 0.099446 | 0.049723 | 0.198892 |

## Pearson cross-check and empirical bootstrap

Pearson chi-square has no intrinsic direction. The exploratory directional p-value uses its signed square root, with gate_40 < gate_30 fixed as the alternative.
Independent empirical bootstrap: 10,000 replicates, seed 42 (D7 uses the next seed). Binomial draws exactly reproduce resampling binary outcomes within each arm.

- D1: Pearson chi-square 0.000008; two-sided p 0.997802; signed-root directional p 0.501099; minimum expected cell 6978.121. Bootstrap CI (pp) [-1.0955, 1.1232]; share of resamples where gate_30 exceeds gate_40 50.14%. Conclusion: directionally positive, not conclusive at 5%.
- D7: Pearson chi-square 2.714408; two-sided p 0.099446; signed-root directional p 0.049723; minimum expected cell 2914.198. Bootstrap CI (pp) [-1.5846, 0.1551]; share of resamples where gate_30 exceeds gate_40 94.76%. Conclusion: directionally negative, not conclusive at 5%.

## Engagement-tier association with D7 (not the A/B test)

Pearson chi-square 11393.734024, df 6, Cramer's V 0.603040; minimum expected cell 56.153.
The computed p-value underflows double precision; it is not exactly zero.
This is concurrent association across the observation window, not evidence that raising activity improves retention. Independence is assumed, not verified.

## Sample ratio mismatch

Assuming equal assignment, chi-square 0.252817, p 0.615099. A nonsignificant SRM check cannot establish randomization or eliminate prefix-selection bias.
