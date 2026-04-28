import pandas as pd

# Load data
hd = pd.read_csv('hd2024/hd2024.csv')
cost = pd.read_csv('cost1_2024/cost1_2024.csv')

# Prompt for CIP code
cip = input("Enter CIP code (e.g., 11.0101): ").strip()
# Find institutions offering the program
competitors = []

cip_columns = ['CIPCODE1', 'CIPCODE2', 'CIPCODE3', 'CIPCODE4', 'CIPCODE5', 'CIPCODE6']
tuition_columns = ['CIPTUIT1', 'CIPTUIT2', 'CIPTUIT3', 'CIPTUIT4', 'CIPTUIT5', 'CIPTUIT6']

for idx, row in cost.iterrows():
    for i, cip_col in enumerate(cip_columns):
        if pd.notna(row[cip_col]) and str(row[cip_col]).strip() == cip:
            unitid = row['UNITID']
            tuition = row[tuition_columns[i]]
            inst_info = hd[hd['UNITID'] == unitid]
            if not inst_info.empty:
                name = inst_info['INSTNM'].values[0]
                state = inst_info['STABBR'].values[0]
                city = inst_info['CITY'].values[0]
                competitors.append({
                    'Institution': name,
                    'State': state,
                    'City': city,
                    'Tuition': tuition
                })

# Display results
if competitors:
    print(f"\nCompetitors offering CIP {cip}:")
    for comp in competitors:
        print(f"- {comp['Institution']} ({comp['City']}, {comp['State']}): ${comp['Tuition']}")
else:
    print(f"No institutions found with program-level tuition data for CIP {cip}.")
    print("Note: This tool uses only reported program-level tuition data. For complete competitor analysis, Completions data is needed.")