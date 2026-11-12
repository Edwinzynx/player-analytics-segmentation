-- name: summary
-- Business question: What are the baseline activity and retention levels?
-- Logic: Aggregate at unique-player grain without rounding.
-- Assumptions: Validated accepted rows; D1 and D7 are marginal outcomes, not survival.
SELECT COUNT(*) AS n, SUM(sum_gamerounds) AS rounds, AVG(sum_gamerounds) AS mean_rounds,
 MIN(sum_gamerounds) AS min_rounds, MAX(sum_gamerounds) AS max_rounds,
 AVG(retention_1) AS d1, AVG(retention_7) AS d7 FROM player_activity;

-- name: version
-- Business question: How do assigned versions compare?
-- Logic: Aggregate counts, activity and retention by assignment.
-- Assumptions: Descriptive differences; inferential conclusions come from the full-sample tests.
SELECT version, COUNT(*) AS n, SUM(sum_gamerounds) AS rounds, AVG(sum_gamerounds) AS mean_rounds,
 AVG(retention_1) AS d1, AVG(retention_7) AS d7
FROM player_activity GROUP BY version ORDER BY version;

-- name: tier
-- Business question: How does observed retention vary with activity?
-- Logic: Derive explicit integer tier keys with CASE, then aggregate.
-- Assumptions: Concurrent activity and retention are associated, not causally ordered.
WITH tiers AS (
 SELECT *, CASE WHEN sum_gamerounds=0 THEN 0 WHEN sum_gamerounds<=5 THEN 1
 WHEN sum_gamerounds<=15 THEN 2 WHEN sum_gamerounds<=50 THEN 3
 WHEN sum_gamerounds<=150 THEN 4 WHEN sum_gamerounds<=500 THEN 5 ELSE 6 END AS rule_tier
 FROM player_activity)
SELECT rule_tier AS tier_id,COUNT(*) AS n,SUM(sum_gamerounds) AS rounds,
 AVG(sum_gamerounds) AS mean_rounds, AVG(retention_1) AS d1,AVG(retention_7) AS d7
FROM tiers GROUP BY rule_tier ORDER BY rule_tier;

-- name: quartile
-- Business question: How do retention levels compare across activity quartiles?
-- Logic: NTILE descending rounds, breaking ties by userid; larger groups first.
-- Assumptions: Quartile one is highest activity; groups may differ by one player.
WITH ranked AS (SELECT *,NTILE(4) OVER(ORDER BY sum_gamerounds DESC,userid ASC) AS quartile
 FROM player_activity)
SELECT quartile,COUNT(*) AS n,SUM(sum_gamerounds) AS rounds,
 AVG(sum_gamerounds) AS mean_rounds,AVG(retention_1) AS d1,AVG(retention_7) AS d7
FROM ranked GROUP BY quartile ORDER BY quartile;

-- name: tier_lag
-- Business question: Where are adjacent tiers most different in observed D7?
-- Logic: Aggregate by ordered tier then subtract LAG of the unrounded rate.
-- Assumptions: This difference is not the effect of moving a player between tiers.
WITH t AS (SELECT tier_id,COUNT(*) AS n,AVG(retention_7) AS d7
 FROM player_activity GROUP BY tier_id)
SELECT *,LAG(d7) OVER(ORDER BY tier_id) AS prior_d7,
 d7-LAG(d7) OVER(ORDER BY tier_id) AS d7_step FROM t ORDER BY tier_id;

-- name: decile
-- Business question: How concentrated is activity in the highest-round players?
-- Logic: Deterministic descending NTILE and cumulative rounds from top to bottom.
-- Assumptions: Rounds measure activity, not monetary value; no power-law fit is claimed.
WITH ranked AS (SELECT *,NTILE(10) OVER(ORDER BY sum_gamerounds DESC,userid ASC) AS rank_decile
 FROM player_activity), d AS (SELECT rank_decile AS decile,COUNT(*) AS n,
 SUM(sum_gamerounds) AS rounds FROM ranked GROUP BY rank_decile)
SELECT *,rounds*1.0/SUM(rounds) OVER() AS rounds_share,
 SUM(rounds) OVER(ORDER BY decile ROWS UNBOUNDED PRECEDING)*1.0/SUM(rounds) OVER()
 AS cumulative_rounds_share FROM d ORDER BY decile;

-- name: quality
-- Business question: Does the accepted SQL table satisfy essential domains?
-- Logic: Count duplicate identifiers, nulls and out-of-domain values.
-- Assumptions: pandas performs strict dtype/schema checks before materialization.
SELECT COUNT(*) AS n,COUNT(*)-COUNT(DISTINCT userid) AS duplicate_userids,
 SUM(CASE WHEN userid IS NULL OR version IS NULL OR sum_gamerounds IS NULL
 OR retention_1 IS NULL OR retention_7 IS NULL THEN 1 ELSE 0 END) AS rows_with_null,
 SUM(CASE WHEN version NOT IN ('gate_30','gate_40') THEN 1 ELSE 0 END) AS invalid_version,
 SUM(CASE WHEN sum_gamerounds<0 THEN 1 ELSE 0 END) AS negative_rounds,
 SUM(CASE WHEN retention_1 NOT IN (0,1) OR retention_7 NOT IN (0,1) THEN 1 ELSE 0 END) AS invalid_flags
FROM player_activity;

-- name: raw_quality
-- Business question: What defects exist before quarantine?
-- Logic: Query the untouched raw staging table separately.
-- Assumptions: Null trailing fields are preserved, not coerced to valid observations.
SELECT COUNT(*) AS n,COUNT(*)-COUNT(DISTINCT userid) AS duplicate_userids,
 SUM(CASE WHEN userid IS NULL OR version IS NULL OR sum_gamerounds IS NULL
 OR retention_1 IS NULL OR retention_7 IS NULL THEN 1 ELSE 0 END) AS rows_with_null,
 SUM(CASE WHEN version NOT IN ('gate_30','gate_40') THEN 1 ELSE 0 END) AS invalid_version
FROM raw_player_activity;

-- name: funnel
-- Business question: How many players returned at both observed milestones?
-- Logic: Nested all/D1/both counts plus a separate nonnested D7-only branch.
-- Assumptions: No intervening-day events or continuous survival are observed.
SELECT COUNT(*) AS all_players,SUM(retention_1) AS d1,
 SUM(CASE WHEN retention_1=1 AND retention_7=1 THEN 1 ELSE 0 END) AS both,
 SUM(CASE WHEN retention_1=0 AND retention_7=1 THEN 1 ELSE 0 END) AS d7_only,
 SUM(CASE WHEN retention_1=1 AND retention_7=1 THEN 1 ELSE 0 END)*1.0/SUM(retention_1)
 AS d7_given_d1 FROM player_activity;

-- name: segment_version
-- Business question: How are descriptive cohort/tier cells distributed by assignment?
-- Logic: Cross-tabulate rule cohort, tier and version.
-- Assumptions: Outcome-defined segments induce selection; contrasts are not causal subgroup effects.
SELECT cohort,tier_id,version,COUNT(*) AS n,SUM(sum_gamerounds) AS rounds,
 AVG(retention_1) AS d1,AVG(retention_7) AS d7
FROM player_activity GROUP BY cohort,tier_id,version ORDER BY cohort,tier_id,version;

