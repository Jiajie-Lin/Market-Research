import pandas as pd
import json
import os

def fmt_cip(v):
    try:
        return f"{float(v):07.4f}"
    except (ValueError, TypeError):
        return str(v)

def safe_int(v):
    try:
        f = float(v)
        return int(f) if f >= 0 else None
    except (ValueError, TypeError):
        return None

print("Loading c2024_a.csv...")
comp_df = pd.read_csv(
    'c2024_a/c2024_a.csv',
    usecols=['UNITID', 'CIPCODE', 'AWLEVEL', 'MAJORNUM', 'CTOTALT']
)
for col in ['UNITID', 'AWLEVEL', 'MAJORNUM', 'CTOTALT']:
    comp_df[col] = pd.to_numeric(comp_df[col], errors='coerce')
comp_df['CIPCODE'] = comp_df['CIPCODE'].apply(fmt_cip)

comp_df = comp_df[
    (comp_df['MAJORNUM'] == 1) &
    (comp_df['CTOTALT'] > 0) &
    (~comp_df['CIPCODE'].str.startswith('99'))
].dropna(subset=['UNITID', 'AWLEVEL', 'CTOTALT'])
print(f"  {len(comp_df):,} qualifying records")

print("Loading hd2024.csv...")
hd_df = pd.read_csv(
    'hd2024/hd2024.csv',
    usecols=['UNITID', 'INSTNM', 'CITY', 'STABBR', 'CONTROL']
)
hd_df['UNITID'] = pd.to_numeric(hd_df['UNITID'], errors='coerce')
hd_df['CONTROL'] = pd.to_numeric(hd_df['CONTROL'], errors='coerce')

print("Loading cost1_2024.csv...")
cost_df = pd.read_csv(
    'cost1_2024/cost1_2024.csv',
    usecols=['UNITID', 'TUITION1', 'TUITION2', 'TUITION5', 'TUITION6']
)
cost_df['UNITID'] = pd.to_numeric(cost_df['UNITID'], errors='coerce')
for col in ['TUITION1', 'TUITION2', 'TUITION5', 'TUITION6']:
    cost_df[col] = pd.to_numeric(cost_df[col], errors='coerce')
    cost_df.loc[cost_df[col] < 0, col] = float('nan')

print("Merging institution + tuition...")
inst_df = hd_df.merge(cost_df, on='UNITID', how='left')

institutions = {}
for _, row in inst_df.iterrows():
    if pd.isna(row['UNITID']):
        continue
    uid = str(int(row['UNITID']))
    institutions[uid] = [
        str(row.get('INSTNM', '')),
        str(row.get('CITY', '')),
        str(row.get('STABBR', '')),
        safe_int(row.get('CONTROL')),
        safe_int(row.get('TUITION1')),
        safe_int(row.get('TUITION2')),
        safe_int(row.get('TUITION5')),
        safe_int(row.get('TUITION6'))
    ]
print(f"  {len(institutions):,} institutions")

print("Building completions index...")
completions = {}
for _, row in comp_df.iterrows():
    cip = str(row['CIPCODE'])
    entry = [int(row['UNITID']), int(row['AWLEVEL']), int(row['CTOTALT'])]
    completions.setdefault(cip, []).append(entry)

cips = sorted(completions.keys())
total_records = sum(len(v) for v in completions.values())
print(f"  {len(cips):,} unique CIP codes")
print(f"  {total_records:,} completion records")

os.makedirs('data', exist_ok=True)
output = {'inst': institutions, 'comp': completions, 'cips': cips}

print("Writing data/ipeds_data.json...")
with open('data/ipeds_data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, separators=(',', ':'), ensure_ascii=False)

size_mb = os.path.getsize('data/ipeds_data.json') / (1024 * 1024)
print(f"Done! data/ipeds_data.json — {size_mb:.1f} MB")
