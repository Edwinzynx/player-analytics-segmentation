"""Offline inspection; never download over or modify raw data."""
from data_quality_checks import load_and_check
if __name__=='__main__':
    _,report=load_and_check()
    print(report)

