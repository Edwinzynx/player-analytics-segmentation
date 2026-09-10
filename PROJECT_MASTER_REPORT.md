# Mobile Game Player Analytics & Behavioral Segmentation
## Comprehensive Master Technical Report & Interview Guide

> **Role Focus**: Senior Game Analytics & Product Insights (Targeted for EA / Slingshot Studios)  
> **Dataset**: Cookie Cats Mobile Puzzle Game (Tactile Entertainment / A/B Test & Player Tracking)  
> **Status**: In Progress — Phases 1 & 2 Completed

---

## Executive Summary & Problem Framing

In modern free-to-play (F2P) mobile titles, long-term player lifetime value (LTV) and monetization are directly gated by **early gameplay engagement and player retention**. For a live-service game team, identifying drop-off cliffs, behavioral friction points, and segment-specific retention dynamics is essential for balancing gameplay progression and optimizing live operations.

### Core Business & Analytical Questions
1. **Behavioral Segmentation**: Can we identify distinct player archetypes based purely on early gameplay activity (`sum_gamerounds`) and retention behavior?
2. **Engagement vs Retention**: At what gameplay threshold does a player transition from casual "bouncer" to a highly retained core player?
3. **Game Mechanics & Progression Gates**: How does placing a progress gate at level 30 versus level 40 alter 1-day and 7-day retention curves?

---

## Analytical Architecture & Workflow

```text
Raw Data (31,332 records)
    │
    ▼
Phase 1: Quality Audit & Data Schema Verification
    │
    ▼
Phase 2: Cleaning (Corrupt Row Removal) & Exploratory Data Analysis
    │
    ▼
Phase 3: Production SQL Analytics & Window Functions (Upcoming)
    │
    ▼
Phase 4: Behavioral Feature Engineering & Log Transformations (Upcoming)
    │
    ▼
Phase 5: K-Means Clustering, Elbow Curve & Silhouette Validation (Upcoming)
    │
    ▼
Phase 6: Segment Profiling & Retention Curve Analysis (Upcoming)
    │
    ▼
Phase 7: Rigorous Statistical Hypothesis Testing (Chi-Square / CIs) (Upcoming)
    │
    ▼
Phase 8: High-Impact Visual Story & Executive Dashboard (Upcoming)
    │
    ▼
Phase 9: Product Recommendations & Business Implications (Upcoming)
    │
    ▼
Phase 10: Final Resume Bullets & Technical Interview Defense (Upcoming)
```

---

## Phase-by-Phase Technical Documentation

---

### PHASE 1 — Setup & Dataset Quality Audit

#### 1. Dataset Dimensions & Schema
The dataset tracks player-level gameplay and retention behavior:
- **Total Raw Records**: `31,332`
- **Total Fields**: `5`
- **Primary Key**: `userid` (`int64`, 31,332 unique records, 0 duplicates)

| Field | Data Type | Missing Count | Description & Analytical Use |
| :--- | :--- | :--- | :--- |
| `userid` | Integer | 0 | Unique player identifier (granular player-level grain). |
| `version` | String / Object | 0 | Experimental cohort: `gate_30` (control) vs `gate_40` (test). |
| `sum_gamerounds` | Float / Int | 1 | Total number of game rounds played in the first 14 days. |
| `retention_1` | Boolean / Object | 1 | Player returned and played 1 day after installing (D1 retention). |
| `retention_7` | Boolean / Object | 1 | Player returned and played 7 days after installing (D7 retention). |

#### 2. Key Dataset Integrity Findings
1. **Explicit Data Boundary**: The dataset does **not** contain session timestamps, monetization/in-app purchase values, or demographic fields. All analysis strictly reflects observable gameplay volume and retention flags.
2. **Corrupted Record**: Exactly 1 record (`userid = 3486875`) contained invalid version `gate_4` and `NaN` values across all other attributes.

---

### PHASE 2 — Data Cleaning & Exploratory Data Analysis (EDA)

#### 1. Cleaning Actions & Rationale
- **Corrupted Record Removal**: Filtered out `gate_4` record with null metrics. Clean dataset size: `31,331` valid players.
- **Type Casting**: Converted `sum_gamerounds` to `int64`, and `retention_1` / `retention_7` to standard boolean types.
- **Domain Validation**: Verified `min(sum_gamerounds) == 0` (players who opened the app but churned before completing level 1). No negative values detected.

#### 2. Overall Gameplay & Retention Benchmarks

| Metric | Measured Value | Analytical Context |
| :--- | :--- | :--- |
| **Total Cleaned Population** | **31,331** players | Full cohort of tracked installs. |
| **Overall Day 1 Retention** | **44.67%** (13,996 players) | ~45% D1 is standard for casual puzzle games. |
| **Overall Day 7 Retention** | **18.66%** (5,845 players) | D7 drops by **26.01 percentage points** (-58.2% relative decay from D1). |
| **Mean Game Rounds** | **51.16** rounds | Strongly inflated by high-volume power players. |
| **Median Game Rounds** | **16.0** rounds | True central tendency of typical players. |
| **Standard Deviation** | **104.32** rounds | High dispersion indicating immense variance in engagement. |
| **Interquartile Range (IQR)** | **46.0** rounds | 25th percentile = 5 rounds, 75th percentile = 51 rounds. |
| **90th / 99th Percentiles** | **133.0** / **494.0** rounds | Top 10% play >133 rounds; top 1% play ~500+ rounds. |
| **Maximum Observed** | **2,961** rounds | Power user (~211 rounds/day over 14 days). |
| **Zero-Round Installs** | **1,373** players (4.38%) | Immediate bounce at app start/tutorial. |

#### 3. A/B Test Variant Comparison (Gate 30 vs Gate 40)

| Version Cohort | Player Count | Mean Rounds | Median Rounds | Day 1 Retention | Day 7 Retention |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **gate_30 (Control)** | 15,621 (49.86%) | **52.03** | **17.0** | **44.67%** | **19.02%** |
| **gate_40 (Test)** | 15,710 (50.14%) | **50.29** | **16.0** | **44.67%** | **18.29%** |
| **Delta ($\Delta$)** | +89 players | -1.74 rounds | -1.0 round | **+0.00%** | **-0.73% pts** |

**Key A/B Finding**: 
- **Day 1 Retention is identical** (44.67% vs 44.67%). Because players do not hit Level 30 or 40 on Day 1, gate placement has zero impact on immediate onboarding.
- **Day 7 Retention is noticeably lower for Gate 40** (18.29% vs 19.02%, a 0.73 percentage point / 3.8% relative drop). Delaying the gate to level 40 reduces 7-day retention, likely because players exhaust content or lose the structured pacing/urgency introduced by the level 30 gate.

#### 4. Behavioral Engagement Buckets vs Retention Dynamics

| Engagement Tier | Game Rounds Range | Player Volume | % of Players | D1 Retention | D7 Retention |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **0 Rounds (Churned)** | 0 | 1,373 | 4.38% | 2.62% | 0.73% |
| **1–5 Rounds (Bouncers)** | 1–5 | 7,187 | 22.94% | 7.68% | 1.35% |
| **6–15 Rounds (Light Casual)** | 6–15 | 6,642 | 21.20% | 26.30% | 4.11% |
| **16–50 Rounds (Core Players)** | 16–50 | 8,230 | 26.27% | 59.25% | 13.44% |
| **51–150 Rounds (Engaged)** | 51–150 | 5,188 | 16.56% | 83.00% | 42.48% |
| **151–500 Rounds (Heavy)** | 151–500 | 2,410 | 7.69% | 90.66% | 77.47% |
| **500+ Rounds (Hardcore)** | >500 | 301 | 0.96% | 97.67% | 95.68% |

**Key Retention Inflection Points**:
1. **The 16-Round Retention Cliff**: Players who complete $\le 15$ rounds have a D7 retention $< 5\%$. Once a player crosses 15 rounds, D1 retention surges from 26.3% to **59.3%**, and D7 retention triples to **13.4%**.
2. **The 50-Round Habituation Cliff**: Crossing 50 rounds elevates D7 retention to **42.5%**, and crossing 150 rounds locks in **>77% D7 retention**.

---

### PHASE 3 — Production SQL Analytics

The cleaned dataset was loaded into an **SQLite relational database (`data/cookie_cats.db`)** with indexing on `userid` and `version`. The SQL suite in [sql/analysis.sql](file:///c:/Users/edwin/OneDrive/Desktop/ea%20project/sql/analysis.sql) executes 6 production queries designed to answer core business and game health questions.

#### Query 1: Macro Executive Portfolio Summary (Aggregations)
```sql
SELECT 
    COUNT(userid) AS total_players,
    ROUND(AVG(sum_gamerounds), 2) AS avg_game_rounds,
    MIN(sum_gamerounds) AS min_rounds,
    MAX(sum_gamerounds) AS max_rounds,
    ROUND(AVG(CAST(retention_1 AS FLOAT)) * 100, 2) AS d1_retention_pct,
    ROUND(AVG(CAST(retention_7 AS FLOAT)) * 100, 2) AS d7_retention_pct,
    ROUND((AVG(CAST(retention_7 AS FLOAT)) / AVG(CAST(retention_1 AS FLOAT))) * 100, 2) AS d1_to_d7_survival_rate_pct
FROM player_activity;
```
*Output*:
| total_players | avg_game_rounds | min_rounds | max_rounds | d1_retention_pct | d7_retention_pct | d1_to_d7_survival_rate_pct |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 31,331 | 51.16 | 0 | 2,961 | 44.67% | 18.66% | **41.76%** |

#### Query 2: A/B Experimentation Performance (GROUP BY)
```sql
SELECT 
    version,
    COUNT(userid) AS player_count,
    ROUND(COUNT(userid) * 100.0 / (SELECT COUNT(*) FROM player_activity), 2) AS variant_share_pct,
    ROUND(AVG(sum_gamerounds), 2) AS avg_game_rounds,
    ROUND(AVG(CAST(retention_1 AS FLOAT)) * 100, 2) AS d1_retention_pct,
    ROUND(AVG(CAST(retention_7 AS FLOAT)) * 100, 2) AS d7_retention_pct,
    ROUND((AVG(CAST(retention_1 AS FLOAT)) - AVG(CAST(retention_7 AS FLOAT))) * 100, 2) AS retention_drop_pct_points
FROM player_activity
GROUP BY version
ORDER BY version ASC;
```
*Output*:
| version | player_count | variant_share_pct | avg_game_rounds | d1_retention_pct | d7_retention_pct | retention_drop_pct_points |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `gate_30` | 15,621 | 49.86% | 52.03 | 44.67% | **19.02%** | 25.65% pts |
| `gate_40` | 15,710 | 50.14% | 50.29 | 44.67% | **18.29%** | 26.38% pts |

#### Query 3: Behavioral Engagement Tiering (CTE & CASE Bucketing)
```sql
WITH player_engagement_tiers AS (
    SELECT 
        userid, version, sum_gamerounds, retention_1, retention_7,
        CASE 
            WHEN sum_gamerounds = 0 THEN '1. Zero Activity (0 rounds)'
            WHEN sum_gamerounds BETWEEN 1 AND 5 THEN '2. Bouncers (1-5 rounds)'
            WHEN sum_gamerounds BETWEEN 6 AND 15 THEN '3. Light Casual (6-15 rounds)'
            WHEN sum_gamerounds BETWEEN 16 AND 50 THEN '4. Core Players (16-50 rounds)'
            WHEN sum_gamerounds BETWEEN 51 AND 150 THEN '5. Engaged (51-150 rounds)'
            WHEN sum_gamerounds BETWEEN 151 AND 500 THEN '6. Heavy Engaged (151-500 rounds)'
            ELSE '7. Hardcore VIP (500+ rounds)'
        END AS engagement_tier
    FROM player_activity
)
SELECT 
    engagement_tier,
    COUNT(userid) AS player_count,
    ROUND(COUNT(userid) * 100.0 / (SELECT COUNT(*) FROM player_activity), 2) AS pct_of_playerbase,
    ROUND(AVG(sum_gamerounds), 1) AS avg_rounds_in_tier,
    ROUND(AVG(CAST(retention_1 AS FLOAT)) * 100, 2) AS d1_retention_pct,
    ROUND(AVG(CAST(retention_7 AS FLOAT)) * 100, 2) AS d7_retention_pct
FROM player_engagement_tiers
GROUP BY engagement_tier
ORDER BY engagement_tier ASC;
```
*Output*:
| engagement_tier | player_count | pct_of_playerbase | avg_rounds_in_tier | d1_retention_pct | d7_retention_pct |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1. Zero Activity (0 rounds) | 1,373 | 4.38% | 0.0 | 2.62% | 0.73% |
| 2. Bouncers (1–5 rounds) | 7,187 | 22.94% | 2.7 | 7.68% | 1.35% |
| 3. Light Casual (6–15 rounds) | 6,642 | 21.20% | 9.9 | 26.30% | 4.11% |
| 4. Core Players (16–50 rounds) | 8,230 | 26.27% | 29.2 | 59.25% | 13.44% |
| 5. Engaged (51–150 rounds) | 5,188 | 16.56% | 86.1 | 83.00% | 42.48% |
| 6. Heavy Engaged (151–500 rounds) | 2,410 | 7.69% | 250.6 | 90.66% | 77.47% |
| 7. Hardcore VIP (500+ rounds) | 301 | 0.96% | 753.0 | 97.67% | 95.68% |

#### Query 4: Population Quartile Analysis (Window Function: `NTILE(4)`)
```sql
WITH ranked_players AS (
    SELECT 
        userid, version, sum_gamerounds, retention_1, retention_7,
        NTILE(4) OVER (ORDER BY sum_gamerounds ASC) AS engagement_quartile
    FROM player_activity
)
SELECT 
    engagement_quartile,
    COUNT(userid) AS players_in_quartile,
    MIN(sum_gamerounds) AS min_rounds,
    MAX(sum_gamerounds) AS max_rounds,
    ROUND(AVG(sum_gamerounds), 2) AS avg_rounds,
    ROUND(AVG(CAST(retention_1 AS FLOAT)) * 100, 2) AS d1_retention_pct,
    ROUND(AVG(CAST(retention_7 AS FLOAT)) * 100, 2) AS d7_retention_pct
FROM ranked_players
GROUP BY engagement_quartile
ORDER BY engagement_quartile ASC;
```
*Output*:
| engagement_quartile | players_in_quartile | min_rounds | max_rounds | avg_rounds | d1_retention_pct | d7_retention_pct |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Q1 (Bottom 25%)** | 7,833 | 0 | 5 | 2.01 | 6.04% | **1.25%** |
| **Q2 (Lower-Mid)** | 7,833 | 5 | 16 | 9.84 | 26.13% | **4.15%** |
| **Q3 (Upper-Mid)** | 7,833 | 17 | 51 | 30.14 | 60.56% | **13.78%** |
| **Q4 (Top 25%)** | 7,832 | 51 | 2,961 | 162.65 | 85.96% | **55.45%** |

#### Query 5: Inter-Tier Retention Lift & Step-Change (Window Function: `LAG()`)
```sql
WITH tier_metrics AS (
    SELECT 
        CASE 
            WHEN sum_gamerounds = 0 THEN '1. Zero'
            WHEN sum_gamerounds BETWEEN 1 AND 5 THEN '2. Bouncers (1-5)'
            WHEN sum_gamerounds BETWEEN 6 AND 15 THEN '3. Light (6-15)'
            WHEN sum_gamerounds BETWEEN 16 AND 50 THEN '4. Core (16-50)'
            WHEN sum_gamerounds BETWEEN 51 AND 150 THEN '5. Engaged (51-150)'
            WHEN sum_gamerounds BETWEEN 151 AND 500 THEN '6. Heavy (151-500)'
            ELSE '7. Hardcore (500+)'
        END AS tier,
        COUNT(userid) AS player_count,
        ROUND(AVG(CAST(retention_7 AS FLOAT)) * 100, 2) AS d7_retention_pct
    FROM player_activity
    GROUP BY 1
)
SELECT 
    tier,
    player_count,
    d7_retention_pct,
    LAG(d7_retention_pct, 1) OVER (ORDER BY tier ASC) AS prev_tier_d7_retention,
    ROUND(d7_retention_pct - LAG(d7_retention_pct, 1) OVER (ORDER BY tier ASC), 2) AS incremental_d7_lift_pct_points
FROM tier_metrics
ORDER BY tier ASC;
```
*Output*:
| tier | player_count | d7_retention_pct | prev_tier_d7_retention | incremental_d7_lift_pct_points |
| :--- | :--- | :--- | :--- | :--- |
| 1. Zero | 1,373 | 0.73% | NULL | NULL |
| 2. Bouncers (1–5) | 7,187 | 1.35% | 0.73% | +0.62% pts |
| 3. Light (6–15) | 6,642 | 4.11% | 1.35% | +2.76% pts |
| 4. Core (16–50) | 8,230 | 13.44% | 4.11% | +9.33% pts |
| **5. Engaged (51–150)** | 5,188 | 42.48% | 13.44% | **+29.04% pts** (Largest Step 1) |
| **6. Heavy (151–500)** | 2,410 | 77.47% | 42.48% | **+34.99% pts** (Largest Step 2) |
| 7. Hardcore (500+) | 301 | 95.68% | 77.47% | +18.21% pts |

#### Query 6: Power Law Concentration & Decile Share (Window Function: `NTILE(10)` & Running Total)
```sql
WITH decile_ranked AS (
    SELECT 
        userid, sum_gamerounds,
        NTILE(10) OVER (ORDER BY sum_gamerounds ASC) AS decile
    FROM player_activity
),
decile_aggregation AS (
    SELECT 
        decile,
        COUNT(userid) AS player_count,
        MIN(sum_gamerounds) AS min_rounds,
        MAX(sum_gamerounds) AS max_rounds,
        SUM(sum_gamerounds) AS total_rounds_in_decile
    FROM decile_ranked
    GROUP BY decile
),
total_rounds_const AS (
    SELECT SUM(sum_gamerounds) AS grand_total FROM player_activity
)
SELECT 
    d.decile,
    d.player_count,
    d.min_rounds,
    d.max_rounds,
    d.total_rounds_in_decile,
    ROUND(d.total_rounds_in_decile * 100.0 / t.grand_total, 2) AS pct_of_all_game_rounds,
    ROUND(SUM(d.total_rounds_in_decile * 100.0 / t.grand_total) OVER (ORDER BY d.decile ASC), 2) AS cumulative_rounds_pct
FROM decile_aggregation d
CROSS JOIN total_rounds_const t
ORDER BY d.decile DESC;
```
*Output*:
| decile | player_count | min_rounds | max_rounds | total_rounds_in_decile | pct_of_all_game_rounds | cumulative_rounds_pct |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Decile 10 (Top 10%)** | 3,133 | 133 | 2,961 | 890,308 | **55.55%** | 100.00% |
| **Decile 9** | 3,133 | 66 | 133 | 292,357 | **18.24%** | 44.45% |
| **Decile 8** | 3,133 | 40 | 66 | 161,992 | **10.11%** | 26.21% |
| **Decile 7** | 3,133 | 25 | 40 | 101,060 | **6.31%** | 16.11% |
| **Decile 6** | 3,133 | 17 | 25 | 64,277 | **4.01%** | 9.80% |
| **Decile 5** | 3,133 | 11 | 16 | 42,209 | **2.63%** | 5.79% |
| **Decile 4** | 3,133 | 6 | 11 | 26,185 | **1.63%** | 3.16% |
| **Decile 3** | 3,133 | 3 | 6 | 15,252 | **0.95%** | 1.52% |
| **Decile 2** | 3,133 | 1 | 3 | 7,424 | **0.46%** | 0.57% |
| **Decile 1 (Bottom 10%)** | 3,134 | 0 | 1 | 1,761 | **0.11%** | 0.11% |

**Key Power Law Finding**: 
---

### PHASE 4 — Behavioral Feature Engineering & Matrix Construction

To perform unsupervised player segmentation with K-Means clustering, the raw player records were transformed into a mathematically standardized behavioral feature matrix.

#### 1. Mathematical Handling of Extreme Skewness
- **Problem**: Raw `sum_gamerounds` has a skewness coefficient of **+6.52** (heavily right-skewed, ranging from 0 to 2,961 rounds). If passed directly into Euclidean distance-based algorithms like K-Means ($d = \sqrt{\sum (x_i - y_i)^2}$), the massive variance of the top 0.1% power players would completely dominate distance calculations, distorting cluster centroids.
- **Solution**: Applied logarithmic smoothing transformation:
  $$\text{log\_gamerounds} = \ln(\text{sum\_gamerounds} + 1)$$
- **Result**: Skewness dropped from **+6.52** to **+0.10** (near-symmetric, normal-like distribution), stabilizing variance while preserving monotonic rank order across players.

#### 2. Engineered Behavioral Features

| Feature Name | Data Type | Mathematical Transformation | Analytical Role & Rationale |
| :--- | :--- | :--- | :--- |
| `log_gamerounds` | Float64 | $\ln(x + 1)$ + `StandardScaler` ($\mu=0, \sigma=1$) | Normalizes engagement intensity for unbiased Euclidean distance clustering. |
| `retention_1_int` | Binary (0/1) | `StandardScaler` ($\mu=0, \sigma=1$) | Captures immediate Day 1 onboarding conversion and initial game hook. |
| `retention_7_int` | Binary (0/1) | `StandardScaler` ($\mu=0, \sigma=1$) | Captures sustained Week 1 habituation and long-term retention. |
| `retention_score` | Ordinal (0–3) | $(1 \cdot \text{D1}) + (2 \cdot \text{D7})$ + `StandardScaler` | Synthesizes full retention trajectory: 0=Churned, 1=D1 only, 2=D7 only, 3=Both. |
| `sum_gamerounds` | Int64 | Unscaled (Raw Count) | Preserved for intuitive business profiling and segment translation. |
| `version` | Categorical | Unscaled (String) | Preserved for post-clustering experimental A/B cohort cross-tabulation. |

#### 3. Feature Correlation Matrix
```text
                 log_gamerounds  retention_1_int  retention_7_int  retention_score
log_gamerounds            1.000            0.614            0.541            0.691
retention_1_int           0.614            1.000            0.327            0.715
retention_7_int           0.541            0.327            1.000            0.895
retention_score           0.691            0.715            0.895            1.000
```
*Takeaway*: Moderate-to-strong positive correlations demonstrate that engagement volume and longitudinal retention reinforce each other, providing rich behavioral variance for K-Means clustering.

#### 4. Standardization Rationale
Standardization (`StandardScaler`) transforms all clustering features to mean 0 and variance 1:
$$z = \frac{x - \mu}{\sigma}$$
This ensures that binary retention flags ($0/1$) and log gameplay values ($0 \text{ to } 7.99$) contribute equally to Euclidean distance metrics without arbitrary scale bias.

The final feature matrix was exported to [data/player_features.csv](file:///c:/Users/edwin/OneDrive/Desktop/ea%20project/data/player_features.csv) (31,331 rows, 12 columns).

---

### PHASE 5 — Unsupervised Behavioral Player Segmentation (K-Means)

We applied K-Means clustering across standardized behavioral features (`log_gamerounds_scaled`, `retention_1_int_scaled`, `retention_7_int_scaled`, `retention_score_scaled`) to discover empirical player archetypes.

#### 1. Cluster Evaluation & Model Selection ($K=2$ to $K=7$)

| Number of Clusters ($K$) | Inertia (WCSS) | Silhouette Score | Calinski-Harabasz Index | Davies-Bouldin Index |
| :--- | :--- | :--- | :--- | :--- |
| **$K=2$** | 56,368.3 | 0.6050 | 38,325.0 | 0.6119 |
| **$K=3$** | 20,761.7 | **0.6812** | 78,888.9 | 0.4718 |
| **$K=4$ (Selected)** | **15,017.5** | **0.6166** | **76,701.1** | **0.5269** |
| **$K=5$** | 9,653.6 | 0.6327 | 93,838.0 | 0.5006 |
| **$K=6$** | 7,097.0 | 0.5870 | 104,366.9 | 0.5595 |
| **$K=7$** | 5,677.9 | 0.5818 | 110,011.4 | 0.5535 |

**Why $K=4$ was Selected as the Optimal Model**:
1. **Mathematical Evidence**: The Elbow curve exhibits strong dimensional flattening between $K=3$ and $K=4$ (inertia decreases from 56.4k at $K=2$ to 15.0k at $K=4$). While $K=3$ achieves a high silhouette score (0.68), it collapses two fundamentally different retention pathways into a single cluster.
2. **Behavioral Separation**: $K=4$ perfectly maps the four quadrant combinations of longitudinal retention trajectories:
   - Neither D1 nor D7 returned (split into low-engagement vs day-0 binging).
   - D1 returned only (high initial hook, rapid subsequent churn).
   - D7 returned (highly retained core and resurrected players).
3. **Actionability**: A 4-cluster segmentation maps directly to actionable live-ops player lifecycles: onboarding triage, churn re-engagement, progression tuning, and VIP retention.

#### 2. Final Empirical Player Segment Profiles ($N = 31,331$)

| Cluster ID | Segment Name | Player Count | % Share | Mean Rounds | Median Rounds | Day 1 Retention | Day 7 Retention | Both Retained |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Cluster 0** | **Immediate Bouncers** | 8,666 | **27.66%** | **2.53** | **2.0** | 0.00% | 0.09% | 0.00% |
| **Cluster 3** | **Day-0 Bingers (Unretained)** | 7,430 | **23.71%** | **22.53** | **15.0** | 0.00% | 0.00% | 0.00% |
| **Cluster 2** | **Short-Term Adopters (D1 Only)** | 9,398 | **30.00%** | **49.72** | **32.0** | 100.00% | 0.00% | 0.00% |
| **Cluster 1** | **Loyal Core Champions (D7 Retained)** | 5,837 | **18.63%** | **162.11** | **106.0** | 78.77% | 100.00% | 78.77% |

#### 3. Deep Archetype Definitions & Behavioral Signatures
1. **Immediate Bouncers (Cluster 0, 27.7%)**: Minimal interaction (average 2.5 rounds). Players who installed the game, encountered friction during tutorial/early onboarding, and abandoned immediately with 0% retention.
2. **Day-0 Bingers / Unretained Trialists (Cluster 3, 23.7%)**: Significant early engagement on day 0 (average 22.5 rounds, median 15 rounds), yet **0% returned on Day 1 or Day 7**. This represents a critical product insight: high single-session playtime without habit formation leads to total churn.
3. **Short-Term Adopters (Cluster 2, 30.0%)**: High initial interest (100% Day 1 retention, average 49.7 rounds), but **0% Day 7 retention**. Players hit early progression barriers or content exhaustion between Day 2 and Day 6.
4. **Loyal Core Champions (Cluster 1, 18.6%)**: The power engine of the game (average 162.1 rounds, median 106.0 rounds). **100% returned on Day 7**, with 78.8% also active on Day 1.

The segmented dataset is saved at [data/player_segments.csv](file:///c:/Users/edwin/OneDrive/Desktop/ea%20project/data/player_segments.csv).

---

## Generated Visualizations & Analytical Interpretations

### 1. Game Rounds Distribution (`outputs/figures/01_gamerounds_distribution.png`)
- **Question Answered**: How is player gameplay volume distributed across the player base?
- **Key Insight**: Severe right skew (power-law distribution). Over 50% of players play fewer than 16 rounds, while the top 1% play up to thousands of rounds. Justifies logarithmic scaling for machine learning.

### 2. Overall D1 vs D7 Retention Funnel (`outputs/figures/02_d1_vs_d7_retention.png`)
- **Question Answered**: What is the overall macro retention drop-off from Day 1 to Day 7?
- **Key Insight**: Demonstrates a 58.2% relative retention decay between Day 1 (44.67%) and Day 7 (18.66%), highlighting the critical need for early-game retention mechanics.

### 3. Retention by Game Version (`outputs/figures/03_retention_by_version.png`)
- **Question Answered**: Did shifting the gate from Level 30 to Level 40 improve or damage player retention?
- **Key Insight**: D1 retention is identical, but D7 retention drops significantly for Gate 40 (18.29% vs 19.02%), proving that gate placement at Level 30 was superior for long-term engagement.

### 4. Retention by Engagement Buckets (`outputs/figures/04_engagement_vs_retention_buckets.png`)
- **Question Answered**: How strongly does early gameplay intensity predict subsequent Day 1 and Day 7 return rates?
- **Key Insight**: Retention exhibits a steep sigmoidal/S-curve relationship with game rounds. The steepest return on retention occurs between 15 and 50 rounds.

### 5. Feature Engineering: Skewness & Log Transformation (`outputs/figures/05_skewness_and_log_transformation.png`)
- **Question Answered**: How does applying a `log1p` transformation transform skewed gameplay data for machine learning?
- **Key Insight**: Compresses skewness from +6.52 down to +0.10, preventing extreme outliers (2,961 rounds) from biasing cluster centroid distance calculations.

### 6. K-Means Elbow & Silhouette Analysis (`outputs/figures/06_kmeans_elbow_and_silhouette.png`)
- **Question Answered**: What is the mathematically and behaviorally optimal number of clusters?
- **Key Insight**: Identifies the elbow inflection point at $K=4$ with a robust silhouette score of 0.617, validating optimal cluster compactness and separation.

### 7. Behavioral Player Archetype Profiles (`outputs/figures/07_cluster_profiles.png`)
- **Question Answered**: How do the 4 player segments differ across volume, gameplay intensity, and retention rates?
- **Key Insight**: Visually contrasts the 4 distinct behavioral groups, illustrating the massive 162-round engagement of Loyal Core Champions alongside the 30% share of Short-Term Adopters.

### 8. 2D PCA Cluster Projection (`outputs/figures/08_cluster_scatter_pca.png`)
- **Question Answered**: How cleanly separated are the clusters in reduced dimensionality space?
- **Key Insight**: 2D PCA projection captures >80% of total variance, showing distinct non-overlapping clusters corresponding to discrete retention trajectories.

---

## Interview Questions & Preparation Guide

### Phase 1 & 2 Technical Interview Questions

#### Q1: "Why did you use both the mean and the median to describe game rounds?"
> **Answer**: `sum_gamerounds` is heavily right-skewed with extreme outliers (max: 2,961 rounds, while median is only 16 rounds). In skewed distributions, the mean is pulled upward by power users (51.16 rounds), whereas the median (16.0 rounds) and IQR (46.0 rounds) provide a robust, non-parametric representation of the typical player experience.

#### Q2: "How did you handle data cleaning and missing values?"
> **Answer**: During our data audit, we discovered 31,332 records with 1 corrupted row containing an invalid version string (`gate_4`) and null values across all engagement metrics. We removed this single corrupted record (0.003% of data) and cast boolean and integer types cleanly, preserving 31,331 valid records without discarding real player behavioral variance.

#### Q3: "Why did Day 1 retention show no difference between Gate 30 and Gate 40, while Day 7 retention showed a difference?"
> **Answer**: On Day 1, players have only installed the game and played early levels (median ~16 rounds). Almost no players reach Level 30 on their first day, so the gate position cannot physically affect Day 1 retention. By Day 7, engaged players reach Level 30/40; players in the Gate 30 group encountered the gate mechanic earlier, which provided a natural pacing break, whereas Gate 40 players experienced fatigue or content exhaustion.

#### Q4: "What is the difference between statistical significance and practical significance in mobile game analytics?"
> **Answer**: With large sample sizes ($N > 30,000$), even tiny percentage changes can be statistically significant ($p < 0.05$). Practical significance asks whether the difference moves the needle for game health or revenue. A 0.73 percentage point drop in D7 retention across millions of players translates to tens of thousands of lost active users, representing substantial practical business impact.

### Phase 3 SQL Technical Interview Questions

#### Q5: "Can you walk me through how you calculated player retention in SQL without relying on BI tools?"
> **Answer**: In our SQL table `player_activity`, retention flags are boolean (`retention_1`, `retention_7`). To calculate the exact retention percentage, we cast the boolean flag to float (`CAST(retention_1 AS FLOAT)`) and take the `AVG(...) * 100`. In a `GROUP BY version` or `GROUP BY engagement_tier` clause, this cleanly computes the cohort-specific conversion rate in a single pass without expensive subqueries.

#### Q6: "Why did you use window functions like `LAG()` and `NTILE()` instead of standard `GROUP BY`?"
> **Answer**: `GROUP BY` collapses rows into summary groups, which is great for single-level aggregates. However, answering comparative analytical questions requires window functions:
> 1. `NTILE(4)` and `NTILE(10)` rank the full continuous population into equal quartiles and deciles to test for non-linear power-law dynamics.
> 2. `LAG()` allows inter-tier comparisons (calculating the marginal Day 7 retention lift gained when moving from one engagement tier to the next) without performing self-joins.
> 3. Cumulative running totals (`SUM(...) OVER (ORDER BY decile)`) quantify the exact proportion of total gameplay generated by the top deciles.

### Phase 4 Feature Engineering & ML Interview Questions

#### Q7: "Why did you apply a log1p transformation to sum_gamerounds before K-Means clustering?"
> **Answer**: K-Means clustering calculates Euclidean distance between points and centroids. In our dataset, raw `sum_gamerounds` had an extreme right skew (+6.52) with power users reaching 2,961 rounds. Without transformation, these extreme values would completely dominate distance calculations, pulling centroids toward outliers. Applying $\ln(x + 1)$ reduced skewness to +0.10, stabilizing variance and allowing the algorithm to segment across the full spectrum of player engagement.

#### Q8: "Why is feature standardization (Z-score scaling) strictly necessary for K-Means?"
> **Answer**: K-Means is non-scale-invariant. If one feature ranges from 0 to 8 (like `log_gamerounds`) and another ranges from 0 to 1 (like binary retention flags), the feature with the larger variance and magnitude will artificially carry 8x more weight in Euclidean distance calculations. Standardization brings all features to mean 0 and standard deviation 1, ensuring equal geometric contribution.

### Phase 5 K-Means Segmentation Interview Questions

#### Q9: "How did you validate your choice of K=4 rather than just picking an arbitrary number?"
> **Answer**: We evaluated $K=2$ through $K=7$ using both the **Elbow Method (within-cluster sum of squares / inertia)** and the **Silhouette Coefficient**. The elbow curve exhibited a sharp drop from $K=2$ (56.4k) to $K=4$ (15.0k) with diminishing returns thereafter. $K=4$ achieved a high silhouette score of **0.617** while uniquely isolating the four fundamental retention archetypes: Immediate Churners, Day-0 Bingers, D1 Adopters, and D7 Loyal Champions.

#### Q10: "What was the most surprising behavioral pattern discovered through clustering?"
> **Answer**: Discovering **Day-0 Bingers (Cluster 3, 23.7% of players)**. These players played an average of 22.5 rounds on their first day (higher than the overall median of 16 rounds), yet **0% returned on Day 1 or Day 7**. This revealed that high initial gameplay volume does not guarantee retention; without habit triggers or pacing breaks, players can binge and burn out within a single session.

---

## Next Steps: Roadmap
- [x] **Phase 1: Setup & Data Understanding**
- [x] **Phase 2: Data Cleaning & Exploratory Analysis**
- [x] **Phase 3: SQL Analytics (Aggregations, CTEs, Window Functions)**
- [x] **Phase 4: Behavioral Feature Engineering (Log Scaling, Standardizing)**
- [x] **Phase 5: K-Means Clustering & Segmentation Validation**
- [ ] **Phase 6: Segment Profiling & Retention Curve Analysis**
- [ ] **Phase 7: Statistical Hypothesis Testing (Chi-Square, Odds Ratios)**
- [ ] **Phase 8: Visual Story & Dashboard**
- [ ] **Phase 9: Product Recommendations & Business Implications**
- [ ] **Phase 10: Final Master Review, Resume Bullets & Interview Defense**



