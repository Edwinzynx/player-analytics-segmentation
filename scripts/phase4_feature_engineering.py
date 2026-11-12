"""Derive transparent cohorts and retain legacy features for comparison."""
import pandas as pd
from common import ROOT, features
def main():
    df = features(pd.read_csv(ROOT/'data/cookie_cats_cleaned.csv'))
    df.to_csv(ROOT/'data/player_features.csv',index=False)
if __name__ == '__main__':
    main()

