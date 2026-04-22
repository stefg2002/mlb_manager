from cots import scrape as cots_scrape
from mlb_api import scrape as mlb_scrape

from rapidfuzz import fuzz, process
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('postgresql://postgres:syncopate@192.168.1.78:5432/scrape_database')

contracts = cots_scrape()
print("-----Scraped cots-------")

players = mlb_scrape()
print("----Scraped Players------")

c_names = contracts['normalized_name'].tolist()
matches = []
non_matches = []

for _,row in players.iterrows():
    m_name = row['normalized_name']

    match, score, idx = process.extractOne(m_name, c_names, scorer=fuzz.ratio)

    if score >= 78:
        c_row = contracts.iloc[idx]
        matches.append({
            "mlb_name": row['normalized_name'],
            "cots_name": c_row["normalized_name"],
            "score": score
        })
    else:
        c_row = contracts.iloc[idx]
        non_matches.append({
            "mlb_name": row['normalized_name'],
            "cots_name": c_row["normalized_name"],
            "score": score
        })

mat_df=pd.DataFrame(matches)
# mat_df.to_csv('out.csv')

non_df = pd.DataFrame(non_matches)
# non_df.to_csv('out_non.csv')

mat_df.to_sql('mlb_match', con=engine, if_exists='append', index=False)