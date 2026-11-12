# Product analytics dashboard build specification

## Purpose and decision

Show observed retention, version comparisons and activity concentration. The dataset remains Cookie Cats. Use the dashboard to identify questions for further investigation, not to claim commercial or clinical outcomes. This is a snapshot; there is no time axis for trends.

## Import and model

In Power BI Desktop use Get Data > Text/CSV for fact_players, dim_tier, dim_cohort and dim_decile. Set userid, rounds, retention flags, tier_id and decile to Whole Number; version and cohort to Text. Do not let automatic type detection change the tier labels. Fact grain is one accepted player.

Create single-direction one-to-many relationships from dim_tier[tier_id], dim_cohort[cohort], and dim_decile[decile] to matching fact columns. Mark dimensions' keys unique. Sort dim_tier[tier] by tier_id and dim_cohort[cohort] by cohort_order. Use dimension fields in visuals and slicers, not duplicate fact labels. Hide duplicate fact dimension labels.

Import ab_statistics and any desired aggregate tables as disconnected validation/reference tables. Never join aggregate tables back to fact_players or sum their rates. All interactive metrics use the fact table. Add the DAX measures individually from powerbi_measures.dax. They are written for these exact table and column names; execution in a Tabular engine has not been verified here.

## Page: Overview

Use a wide canvas. Place title and a visible truncated-source caveat at the top. Below, align KPI cards for Players, D1 Retention, D7 Retention and Mean Rounds. Use percentages for rates and integers for population.

Place a clustered column chart of dim_tier[tier] against D1 Retention and D7 Retention on the left. Place a cohort table on the right with Players, Share of Players, Total Rounds, Share of Rounds, Mean Rounds, Median Rounds and both retention rates. Add version and cohort slicers down the right edge. Disable misleading cross-highlighting; use filter interactions consistently.

Add a nested funnel using all players, D1 retained, and Both Retained; show D7-only as a separate card calculated by filtering its cohort. Label the funnel as observed milestones, not continuous survival. Caption: cohort retention is defined by its flags.

## Page: Experiment

Use a version comparison chart for the marginal D1 and D7 rates, then a table of disconnected ab_statistics fields: metric, difference, ci_low, ci_high, p_two_sided, p_one_sided_gate40_lower, p_holm, odds_ratio, relative_lift, conclusion. Show the full-population statistical conclusion verbatim.

Disable all slicer and visual-filter interactions with the fixed inference table. Label it as full accepted sample; estimates and confidence intervals do not recalculate for filtered cohorts. A separate descriptive matrix can use tier/cohort slicers and D7 Difference, but must be titled post-assignment comparison and must not be paired with the fixed p-values.

Add notes: primary two-sided testing, Holm family correction, marginal confidence intervals, uncertain sample representativeness, and SRM assumption. Source values for the SRM card from metrics.json via a Power Query JSON import or the statistical report; do not retype values.

## Page: Activity concentration and data quality

Build a combination chart with dim_decile[decile] ascending on the axis, Share of Rounds as columns and Cumulative Share as a line. Set percentage axes consistently. Tooltip fields: Players, Total Rounds, Mean Rounds. Decile membership stays fixed under filtering, so add that explanation.

Show a cohort-by-version count matrix below. Add the data-quality report as a linked evidence source and a small table of accepted/quarantined counts imported from metrics.json. Explain that outliers are retained and rounds are not revenue. Do not manufacture a refresh date from nonexistent event timestamps.

## Tableau equivalent

Connect the same fact and dimension CSVs using logical relationships. Use COUNTD(userid), SUM(rounds), AVG(retention flags), and SUM(rounds) / TOTAL(SUM(rounds)) for partition-aware shares. On the concentration chart use RUNNING_SUM(SUM(rounds)) / TOTAL(SUM(rounds)), compute using decile ascending and restart per selected partition. Use fixed baseline deciles. Import the inference CSV as a separate source and do not apply the descriptive worksheets' filters to its sheet.

## Validation and refresh

Compare unfiltered KPI totals, every version/tier/cohort row and decile cumulative share to aggregate CSVs and metrics.json. Counts and rounds must match exactly; rates should match before display rounding. Check a selected version, a cohort, and their intersection. Reset slicers to verify the original totals. Check that the final cumulative share reaches the complete selected population's rounds.

Run the Python pipeline, then refresh CSV and JSON sources. Record any source hash change. A before/after study or trend page requires dated observations and a valid comparison design; it is future work. No PBIX is supplied.

## Suggested build order

Import and type the tables, create relationships and sort keys, add measures, build Overview, build Experiment with disabled inference interactions, then build concentration and reconcile. This intentionally limited design is suitable for an approximately hour-long manual dashboard build.

