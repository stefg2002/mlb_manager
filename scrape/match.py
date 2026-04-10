from cots import scrape as cots_scrape
from mlb_api import scrape as mlb_scrape
from rapidfuzz import fuzz, process
import pandas as pd

contracts = cots_scrape()
print("-----Scraped cots-------")

players = mlb_scrape()
print("----Scraped Players------")

c_names = contracts['Normalized Name'].tolist()
matches = []
non_matches = []

for _,row in players.iterrows():
    m_name = row['Normalized Name']

    match, score, idx = process.extractOne(m_name, c_names, scorer=fuzz.ratio)

    if score >= 78:
        c_row = contracts.iloc[idx]
        matches.append({
            "mlb_name": row['Normalized Name'],
            "cots_name": c_row["Normalized Name"],
            "score": score
        })
    else:
        c_row = contracts.iloc[idx]
        non_matches.append({
            "mlb_name": row['Normalized Name'],
            "cots_name": c_row["Name"],
            "score": score
        })

mat_df=pd.DataFrame(matches)
mat_df.to_csv('out.csv')

non_df = pd.DataFrame(non_matches)
non_df.to_csv('out_non.csv')

print(mat_df)