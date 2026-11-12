import sqlite3
from common import load_players
from run_sql_analysis import build_database,compare,queries

def test_every_sql_query_matches_pandas():
    df=load_players()
    with build_database(df) as conn:
        assert set(compare(conn,df))==set(queries())

