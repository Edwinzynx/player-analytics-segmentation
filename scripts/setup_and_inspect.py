import os
import urllib.request
import pandas as pd
import numpy as np

# 1. Directory Structure Setup
directories = [
    'data',
    'notebooks',
    'sql',
    'outputs/figures',
    'scripts'
]

for d in directories:
    os.makedirs(d, exist_ok=True)
    print(f"[OK] Directory ready: {d}/")

# 2. Download Cookie Cats Dataset if not present
data_path = 'data/cookie_cats.csv'
if not os.path.exists(data_path):
    print("\nFetching Cookie Cats dataset...")
    url = 'https://raw.githubusercontent.com/ryanschaub/Mobile-Games-A-B-Testing-with-Cookie-Cats/master/cookie_cats.csv'
    urllib.request.urlretrieve(url, data_path)
    print(f"[OK] Downloaded dataset to {data_path} ({os.path.getsize(data_path):,} bytes)")
else:
    print(f"\n[OK] Dataset already present at {data_path} ({os.path.getsize(data_path):,} bytes)")

# 3. Load and Inspect Dataset
print("\n" + "="*60)
print("PHASE 1: DATASET INSPECTION & QUALITY AUDIT")
print("="*60)

df = pd.read_csv(data_path)

print(f"\n1. Dataset Dimensions:")
print(f"   - Total Rows (Records): {df.shape[0]:,}")
print(f"   - Total Columns (Fields): {df.shape[1]}")

print(f"\n2. Columns & Data Types:")
for col, dtype in df.dtypes.items():
    print(f"   - {col:18s}: {str(dtype)}")

print(f"\n3. Missing Value Audit:")
missing = df.isnull().sum()
for col, count in missing.items():
    print(f"   - {col:18s}: {count} missing ({count / len(df) * 100:.2f}%)")

print(f"\n4. Uniqueness & Primary Key Check:")
total_rows = len(df)
unique_users = df['userid'].nunique()
duplicate_users = total_rows - unique_users
print(f"   - Total records: {total_rows:,}")
print(f"   - Unique userid count: {unique_users:,}")
print(f"   - Duplicate userid count: {duplicate_users:,}")

print(f"\n5. Categorical Breakdown (A/B Test Version):")
version_counts = df['version'].value_counts()
for val, count in version_counts.items():
    print(f"   - {val:10s}: {count:,} ({count / len(df) * 100:.2f}%)")

print(f"\n6. Retention Rates (Raw Boolean Summary):")
print(f"   - Day 1 Retention (retention_1): {df['retention_1'].mean() * 100:.2f}% ({df['retention_1'].sum():,} players)")
print(f"   - Day 7 Retention (retention_7): {df['retention_7'].mean() * 100:.2f}% ({df['retention_7'].sum():,} players)")

print(f"\n7. Numerical Distribution: sum_gamerounds (Player Engagement):")
stats = df['sum_gamerounds'].describe(percentiles=[0.25, 0.50, 0.75, 0.90, 0.95, 0.99, 0.999])
for k, v in stats.items():
    if k == 'count':
        print(f"   - {k:10s}: {int(v):,}")
    else:
        print(f"   - {k:10s}: {v:,.2f}")

zero_rounds = (df['sum_gamerounds'] == 0).sum()
print(f"\n   - Players with 0 game rounds: {zero_rounds:,} ({zero_rounds / len(df) * 100:.2f}%)")
print(f"   - Extreme Max check: {df['sum_gamerounds'].max():,} (Potential extreme outlier)")

print("\n" + "="*60)
print("AUDIT COMPLETE")
print("="*60)
