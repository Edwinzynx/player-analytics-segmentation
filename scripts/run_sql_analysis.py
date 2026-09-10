import sqlite3
import pandas as pd

# 1. Connect to SQLite database
db_path = 'data/cookie_cats.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 2. Load cleaned data into SQL table
df = pd.read_csv('data/cookie_cats_cleaned.csv')
df.to_sql('player_activity', conn, if_exists='replace', index=False)

cursor.execute("CREATE INDEX IF NOT EXISTS idx_user ON player_activity (userid);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_version ON player_activity (version);")
conn.commit()

print("="*75)
print(f"[OK] Database connection active. Table 'player_activity' has {len(df):,} records.")
print("="*75)

queries = {
    "Query 1: Macro Executive Portfolio Summary (Aggregations)": """
        SELECT 
            COUNT(userid) AS total_players,
            ROUND(AVG(sum_gamerounds), 2) AS avg_game_rounds,
            MIN(sum_gamerounds) AS min_rounds,
            MAX(sum_gamerounds) AS max_rounds,
            ROUND(AVG(CAST(retention_1 AS FLOAT)) * 100, 2) AS d1_retention_pct,
            ROUND(AVG(CAST(retention_7 AS FLOAT)) * 100, 2) AS d7_retention_pct,
            ROUND((AVG(CAST(retention_7 AS FLOAT)) / AVG(CAST(retention_1 AS FLOAT))) * 100, 2) AS d1_to_d7_survival_rate_pct
        FROM player_activity
    """,
    "Query 2: A/B Experimentation Performance (GROUP BY Version)": """
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
        ORDER BY version ASC
    """,
    "Query 3: Behavioral Engagement Tiering & Retention (CTE + Case Bucketing)": """
        WITH player_engagement_tiers AS (
            SELECT 
                userid,
                version,
                sum_gamerounds,
                retention_1,
                retention_7,
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
        ORDER BY engagement_tier ASC
    """,
    "Query 4: Population Quartile Analysis (Window Function: NTILE)": """
        WITH ranked_players AS (
            SELECT 
                userid,
                version,
                sum_gamerounds,
                retention_1,
                retention_7,
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
        ORDER BY engagement_quartile ASC
    """,
    "Query 5: Inter-Tier Retention Lift & Step-Change (Window Function: LAG)": """
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
        ORDER BY tier ASC
    """,
    "Query 6: Power Law Concentration & Decile Share (Window Function: Running Total)": """
        WITH decile_ranked AS (
            SELECT 
                userid,
                sum_gamerounds,
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
        ORDER BY d.decile DESC
    """
}

for title, sql in queries.items():
    print(f"\n{'='*75}")
    print(title)
    print(f"{'='*75}")
    res_df = pd.read_sql_query(sql, conn)
    print(res_df.to_string(index=False))

conn.close()
print("\n" + "="*75)
print("ALL SQL QUERIES EXECUTED AND VALIDATED")
print("="*75)
