# Old and corrected numerical results

Generated from metrics.json, including the frozen audit evidence. Old values are parsed from the original documents or computed from the original segmented table, never retyped. This report includes unchanged secondary profiles to make the segmentation transition reviewable. Null old entries mean the old method did not supply a directly comparable statistic. Every original numerical claim also has a source line in audit.legacy_numeric_claims; numerical table snapshots are retained in audit.legacy_table_numbers.

The full accepted population and its unrounded marginal retention/activity totals are unchanged. The major changes are inferential interpretation, interval reporting, bootstrap method/count, primary segmentation, diagnostic subsampling and decile ordering. The complete primary and crossed-cohort profiles, version shares, and descriptive CIs are available in outputs/tables.

| Metric | Old | New | Explanation |
|---|---:|---:|---|
| Headline D7 p-value | 0.049 | 0.099446 | Old one-sided headline; new primary two-sided test |
| D7 exploratory one-sided p-value | 0.049 | 0.049723 | Same directional hypothesis; old rounded headline |
| D7 Holm p-value | not previously reported / not comparable | 0.198892 | Not previously reported; adjusted across D1 and D7 |
| D1 Holm p-value | not previously reported / not comparable | 0.997802 | Not previously reported |
| D7 odds ratio | 1.049 | 0.953334 | Old control/test; new test/control. Direction changed explicitly |
| D7 bootstrap positive-share (%) | 95.1 | 94.76 | Share where control exceeds test; not a hypothesis probability |
| Bootstrap resamples | 1,000 | 10,000 | Fixed-seed binary empirical bootstrap |
| D7 script CI low (pp), control minus test | 0.013 | -0.137543 | Old hardcoded positive interval was incorrect; new Newcombe CI |
| D7 script CI high (pp), control minus test | 1.437 | 1.587925 | Same direction for comparison |
| D7 bootstrap mean (pp), control minus test | 0.725 | 0.722339 | New replicates and random generator |
| D7 bootstrap CI low (pp), control minus test | -0.136 | -0.155052 | Same direction for comparison |
| D7 bootstrap CI high (pp), control minus test | 1.613 | 1.584612 | Same direction for comparison |
| Association minimum expected cell | 256.2 | 56.15349 | Corrected expected-cell audit |
| Headline secondary silhouette | 0.617 | 0.614298 | New fixed diagnostic subsample size is disclosed |
| Conflicting validation CH claim | 138,512 | 76,701.087753 | Original narrative contradicted its own model table |
| Conflicting validation DB claim | 0.548 | 0.526892 | Original narrative contradicted its own model table |
| ARI: rule cohorts vs secondary clusters | not previously reported / not comparable | 0.675512 | New agreement diagnostic; no predictive validation |
| ARI: cohort/tier vs secondary clusters | not previously reported / not comparable | 0.493455 | Different granularity, explicitly reported |
| SRM p-value | not previously reported / not comparable | 0.615099 | New diagnostic; equal allocation assumed |
| D1 complete result: difference | -0.000015 | 0.000015 | Old computed test reconstructed with pinned runtime; old effects are control minus test, new test minus control; old odds control/test |
| D7 complete result: difference | 0.007252 | -0.007252 | Old computed test reconstructed with pinned runtime; old effects are control minus test, new test minus control; old odds control/test |
| D1 complete result: relative_lift | not previously reported / not comparable | 0.000035 | Newly reported diagnostic; old source locations preserved in audit evidence |
| D7 complete result: relative_lift | not previously reported / not comparable | -0.038129 | Newly reported diagnostic; old source locations preserved in audit evidence |
| D1 complete result: z | -0.002755 | 0.002755 | Old computed test reconstructed with pinned runtime; old effects are control minus test, new test minus control; old odds control/test |
| D7 complete result: z | 1.647546 | -1.647546 | Old computed test reconstructed with pinned runtime; old effects are control minus test, new test minus control; old odds control/test |
| D1 complete result: p_two_sided | 0.997802 | 0.997802 | Old computed test reconstructed with pinned runtime; old effects are control minus test, new test minus control; old odds control/test |
| D7 complete result: p_two_sided | 0.099446 | 0.099446 | Old computed test reconstructed with pinned runtime; old effects are control minus test, new test minus control; old odds control/test |
| D1 complete result: chi_square | not previously reported / not comparable | 0.000008 | Newly reported diagnostic; old source locations preserved in audit evidence |
| D7 complete result: chi_square | not previously reported / not comparable | 2.714408 | Newly reported diagnostic; old source locations preserved in audit evidence |
| D1 complete result: chi_p_two_sided | not previously reported / not comparable | 0.997802 | Newly reported diagnostic; old source locations preserved in audit evidence |
| D7 complete result: chi_p_two_sided | not previously reported / not comparable | 0.099446 | Newly reported diagnostic; old source locations preserved in audit evidence |
| D1 complete result: chi_directional_p_gate40_lower | not previously reported / not comparable | 0.501099 | Newly reported diagnostic; old source locations preserved in audit evidence |
| D7 complete result: chi_directional_p_gate40_lower | not previously reported / not comparable | 0.049723 | Newly reported diagnostic; old source locations preserved in audit evidence |
| D1 complete result: odds_ratio | not previously reported / not comparable | 1.000063 | Newly reported diagnostic; old source locations preserved in audit evidence |
| D7 complete result: odds_ratio | 1.048951 | 0.953334 | Old computed test reconstructed with pinned runtime; old effects are control minus test, new test minus control; old odds control/test |
| D1 complete result: min_expected | not previously reported / not comparable | 6,978.121222 | Newly reported diagnostic; old source locations preserved in audit evidence |
| D7 complete result: min_expected | not previously reported / not comparable | 2,914.198238 | Newly reported diagnostic; old source locations preserved in audit evidence |
| D1 calculated difference CI low (pp), control minus test | -1.102533 | -1.102395 | Original computed unpooled Wald vs corrected Newcombe; common orientation for comparison |
| D1 calculated difference CI high (pp), control minus test | 1.099437 | 1.099316 | Original computed unpooled Wald vs corrected Newcombe; common orientation for comparison |
| D7 calculated difference CI low (pp), control minus test | -0.137512 | -0.137543 | Original computed unpooled Wald vs corrected Newcombe; common orientation for comparison |
| D7 calculated difference CI high (pp), control minus test | 1.58789 | 1.587925 | Original computed unpooled Wald vs corrected Newcombe; common orientation for comparison |
| Secondary K=2 inertia | 56,368.3 | 56,368.260618 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=2 silhouette | 0.605 | 0.602761 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=2 calinski_harabasz | 38,325 | 38,325.013677 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=2 davies_bouldin | 0.6119 | 0.611864 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=3 inertia | 20,761.7 | 20,761.660226 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=3 silhouette | 0.6812 | 0.681299 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=3 calinski_harabasz | 78,888.9 | 78,888.897728 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=3 davies_bouldin | 0.4718 | 0.471773 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=4 inertia | 15,017.5 | 15,017.484583 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=4 silhouette | 0.6166 | 0.614298 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=4 calinski_harabasz | 76,701.1 | 76,701.087753 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=4 davies_bouldin | 0.5269 | 0.526892 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=5 inertia | 9,653.6 | 9,653.587061 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=5 silhouette | 0.6327 | 0.634401 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=5 calinski_harabasz | 93,838 | 93,837.951965 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=5 davies_bouldin | 0.5006 | 0.500567 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=6 inertia | 7,097 | 7,097.000719 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=6 silhouette | 0.587 | 0.594515 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=6 calinski_harabasz | 104,366.9 | 104,366.926222 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=6 davies_bouldin | 0.5595 | 0.559524 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=7 inertia | 5,677.9 | 5,673.055975 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=7 silhouette | 0.5818 | 0.588939 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=7 calinski_harabasz | 110,011.4 | 110,109.559611 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Secondary K=7 davies_bouldin | 0.5535 | 0.55353 | Consistent fit settings; diagnostic subsample differs from legacy; small differences may be rounding |
| Activity group: old decile 10 / new 1: n | 3,133 | 3,134 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 10 / new 1: min_rounds | 133 | 133 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 10 / new 1: max_rounds | 2,961 | 2,961 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 10 / new 1: rounds | 890,308 | 890,441 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 10 / new 1: rounds_share | 0.5555 | 0.555545 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 10 / new 1: cumulative_rounds_share | 1 | 0.555545 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 9 / new 2: n | 3,133 | 3,133 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 9 / new 2: min_rounds | 66 | 66 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 9 / new 2: max_rounds | 133 | 133 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 9 / new 2: rounds | 292,357 | 292,290 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 9 / new 2: rounds_share | 0.1824 | 0.182359 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 9 / new 2: cumulative_rounds_share | 0.4445 | 0.737904 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 8 / new 3: n | 3,133 | 3,133 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 8 / new 3: min_rounds | 40 | 40 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 8 / new 3: max_rounds | 66 | 66 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 8 / new 3: rounds | 161,992 | 161,966 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 8 / new 3: rounds_share | 0.1011 | 0.10105 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 8 / new 3: cumulative_rounds_share | 0.2621 | 0.838954 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 7 / new 4: n | 3,133 | 3,133 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 7 / new 4: min_rounds | 25 | 25 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 7 / new 4: max_rounds | 40 | 40 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 7 / new 4: rounds | 101,060 | 101,045 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 7 / new 4: rounds_share | 0.0631 | 0.063042 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 7 / new 4: cumulative_rounds_share | 0.1611 | 0.901996 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 6 / new 5: n | 3,133 | 3,133 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 6 / new 5: min_rounds | 17 | 16 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 6 / new 5: max_rounds | 25 | 25 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 6 / new 5: rounds | 64,277 | 64,268 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 6 / new 5: rounds_share | 0.0401 | 0.040097 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 6 / new 5: cumulative_rounds_share | 0.098 | 0.942093 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 5 / new 6: n | 3,133 | 3,133 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 5 / new 6: min_rounds | 11 | 11 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 5 / new 6: max_rounds | 16 | 16 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 5 / new 6: rounds | 42,209 | 42,204 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 5 / new 6: rounds_share | 0.0263 | 0.026331 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 5 / new 6: cumulative_rounds_share | 0.0579 | 0.968424 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 4 / new 7: n | 3,133 | 3,133 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 4 / new 7: min_rounds | 6 | 6 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 4 / new 7: max_rounds | 11 | 11 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 4 / new 7: rounds | 26,185 | 26,180 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 4 / new 7: rounds_share | 0.0163 | 0.016334 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 4 / new 7: cumulative_rounds_share | 0.0316 | 0.984758 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 3 / new 8: n | 3,133 | 3,133 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 3 / new 8: min_rounds | 3 | 3 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 3 / new 8: max_rounds | 6 | 6 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 3 / new 8: rounds | 15,252 | 15,249 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 3 / new 8: rounds_share | 0.0095 | 0.009514 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 3 / new 8: cumulative_rounds_share | 0.0152 | 0.994271 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 2 / new 9: n | 3,133 | 3,133 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 2 / new 9: min_rounds | 1 | 1 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 2 / new 9: max_rounds | 3 | 3 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 2 / new 9: rounds | 7,424 | 7,422 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 2 / new 9: rounds_share | 0.0046 | 0.004631 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 2 / new 9: cumulative_rounds_share | 0.0057 | 0.998902 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 1 / new 10: n | 3,134 | 3,133 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 1 / new 10: min_rounds | 0 | 0 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 1 / new 10: max_rounds | 1 | 1 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 1 / new 10: rounds | 1,761 | 1,760 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 1 / new 10: rounds_share | 0.0011 | 0.001098 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Activity group: old decile 1 / new 10: cumulative_rounds_share | 0.0011 | 1 | Descending NTILE allocates remainder to highest group; cumulative direction changed to top-down |
| Legacy cluster 0 / secondary K1: n | 8,666 | 8,666 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 0 / secondary K1: size_share | 0.276595 | 0.276595 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 0 / secondary K1: rounds_share | 0.013681 | 0.013681 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 0 / secondary K1: mean_rounds | 2.530464 | 2.530464 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 0 / secondary K1: median_rounds | 2 | 2 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 0 / secondary K1: d1 | 0 | 0 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 0 / secondary K1: d7 | 0.000923 | 0.000923 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 3 / secondary K2: n | 7,430 | 7,430 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 3 / secondary K2: size_share | 0.237145 | 0.237145 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 3 / secondary K2: rounds_share | 0.104434 | 0.104434 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 3 / secondary K2: mean_rounds | 22.528802 | 22.528802 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 3 / secondary K2: median_rounds | 15 | 15 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 3 / secondary K2: d1 | 0 | 0 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 3 / secondary K2: d7 | 0 | 0 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 2 / secondary K3: n | 9,398 | 9,398 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 2 / secondary K3: size_share | 0.299959 | 0.299959 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 2 / secondary K3: rounds_share | 0.291548 | 0.291548 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 2 / secondary K3: mean_rounds | 49.723345 | 49.723345 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 2 / secondary K3: median_rounds | 32 | 32 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 2 / secondary K3: d1 | 1 | 1 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 2 / secondary K3: d7 | 0 | 0 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 1 / secondary K4: n | 5,837 | 5,837 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 1 / secondary K4: size_share | 0.186301 | 0.186301 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 1 / secondary K4: rounds_share | 0.590337 | 0.590337 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 1 / secondary K4: mean_rounds | 162.10502 | 162.10502 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 1 / secondary K4: median_rounds | 106 | 106 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 1 / secondary K4: d1 | 0.787733 | 0.787733 | Like-for-like secondary profiles, including unchanged values |
| Legacy cluster 1 / secondary K4: d7 | 1 | 1 | Like-for-like secondary profiles, including unchanged values |
| Original report / K1: n | 8,666 | 8,666 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K1: size_share | 0.2766 | 0.276595 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K1: rounds | 21,920 | 21,929 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K1: rounds_share | 0.0137 | 0.013681 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K1: mean_rounds | 2.53 | 2.530464 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K1: median_rounds | 2 | 2 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K1: d1 | 0 | 0 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K1: d7 | 0.0009 | 0.000923 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K2: n | 7,430 | 7,430 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K2: size_share | 0.2371 | 0.237145 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K2: rounds | 167,400 | 167,389 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K2: rounds_share | 0.1044 | 0.104434 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K2: mean_rounds | 22.53 | 22.528802 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K2: median_rounds | 15 | 15 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K2: d1 | 0 | 0 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K2: d7 | 0 | 0 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K3: n | 9,398 | 9,398 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K3: size_share | 0.3 | 0.299959 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K3: rounds | 467,269 | 467,300 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K3: rounds_share | 0.2915 | 0.291548 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K3: mean_rounds | 49.72 | 49.723345 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K3: median_rounds | 32 | 32 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K3: d1 | 1 | 1 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K3: d7 | 0 | 0 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K4: n | 5,837 | 5,837 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K4: size_share | 0.1863 | 0.186301 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K4: rounds | 946,236 | 946,207 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K4: rounds_share | 0.5903 | 0.590337 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K4: mean_rounds | 162.11 | 162.10502 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K4: median_rounds | 106 | 106 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K4: d1 | 0.7877 | 0.787733 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original report / K4: d7 | 1 | 1 | Reported table vs recomputed secondary model; some original totals contradicted saved data |
| Original version table / K1: gate30_n | 4,299 | 4,299 | Assignment counts and mean activity; no players-lost causal interpretation |
| Original version table / K1: gate40_n | 4,367 | 4,367 | Assignment counts and mean activity; no players-lost causal interpretation |
| Original version table / K1: gate30_mean_rounds | 2.52 | 2.517562 | Assignment counts and mean activity; no players-lost causal interpretation |
| Original version table / K1: gate40_mean_rounds | 2.54 | 2.543165 | Assignment counts and mean activity; no players-lost causal interpretation |
| Original version table / K2: gate30_n | 3,715 | 3,715 | Assignment counts and mean activity; no players-lost causal interpretation |
| Original version table / K2: gate40_n | 3,715 | 3,715 | Assignment counts and mean activity; no players-lost causal interpretation |
| Original version table / K2: gate30_mean_rounds | 22.36 | 22.359892 | Assignment counts and mean activity; no players-lost causal interpretation |
| Original version table / K2: gate40_mean_rounds | 22.7 | 22.697712 | Assignment counts and mean activity; no players-lost causal interpretation |
| Original version table / K3: gate30_n | 4,641 | 4,641 | Assignment counts and mean activity; no players-lost causal interpretation |
| Original version table / K3: gate40_n | 4,757 | 4,757 | Assignment counts and mean activity; no players-lost causal interpretation |
| Original version table / K3: gate30_mean_rounds | 50.27 | 50.267399 | Assignment counts and mean activity; no players-lost causal interpretation |
| Original version table / K3: gate40_mean_rounds | 49.19 | 49.192558 | Assignment counts and mean activity; no players-lost causal interpretation |
| Original version table / K4: gate30_n | 2,966 | 2,966 | Assignment counts and mean activity; no players-lost causal interpretation |
| Original version table / K4: gate40_n | 2,871 | 2,871 | Assignment counts and mean activity; no players-lost causal interpretation |
| Original version table / K4: gate30_mean_rounds | 163.73 | 163.731962 | Assignment counts and mean activity; no players-lost causal interpretation |
| Original version table / K4: gate40_mean_rounds | 160.42 | 160.424242 | Assignment counts and mean activity; no players-lost causal interpretation |
| Primary cohort D1 only: n | not previously reported / not comparable | 9,398 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort D1 only: size_share | not previously reported / not comparable | 0.299959 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort D1 only: rounds_share | not previously reported / not comparable | 0.291548 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort D1 only: mean_rounds | not previously reported / not comparable | 49.723345 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort D1 only: median_rounds | not previously reported / not comparable | 32 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort D1 only: d1 | not previously reported / not comparable | 1 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort D1 only: d7 | not previously reported / not comparable | 0 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort D7 only: n | not previously reported / not comparable | 1,247 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort D7 only: size_share | not previously reported / not comparable | 0.039801 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort D7 only: rounds_share | not previously reported / not comparable | 0.058915 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort D7 only: mean_rounds | not previously reported / not comparable | 75.725742 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort D7 only: median_rounds | not previously reported / not comparable | 44 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort D7 only: d1 | not previously reported / not comparable | 0 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort D7 only: d7 | not previously reported / not comparable | 1 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort both: n | not previously reported / not comparable | 4,598 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort both: size_share | not previously reported / not comparable | 0.146756 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort both: rounds_share | not previously reported / not comparable | 0.531422 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort both: mean_rounds | not previously reported / not comparable | 185.249456 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort both: median_rounds | not previously reported / not comparable | 127 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort both: d1 | not previously reported / not comparable | 1 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort both: d7 | not previously reported / not comparable | 1 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort none: n | not previously reported / not comparable | 16,088 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort none: size_share | not previously reported / not comparable | 0.513485 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort none: rounds_share | not previously reported / not comparable | 0.118115 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort none: mean_rounds | not previously reported / not comparable | 11.767653 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort none: median_rounds | not previously reported / not comparable | 6 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort none: d1 | not previously reported / not comparable | 0 | New rule definition; not directly comparable with a legacy cluster |
| Primary cohort none: d7 | not previously reported / not comparable | 0 | New rule definition; not directly comparable with a legacy cluster |
