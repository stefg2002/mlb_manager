import requests
from config import settings
from sqlalchemy import create_engine, text
from bs4 import BeautifulSoup, NavigableString
from rapidfuzz import fuzz, process
import pandas as pd

engine = create_engine(str(settings.postgres_url))

teams = ['angels','astros','athletics','blue jays', 'braves', 'brewers', 'cardinals', 'cubs', 'diamondbacks', 'dodgers', 
         'giants', 'guardians', 'mariners', 'marlins', 'mets', 'nationals', 'orioles', 'padres', 'phillies', 'pirates',
         'rangers', 'rays', 'reds', 'red sox', 'rockies', 'royals', 'tigers', 'twins', 'white sox', 'yankees']

matches = []
non_matches = []

for team in teams:
    with engine.connect() as conn:
        data = conn.execute(text(f"SELECT * FROM players_mlb pm WHERE pm.team_name='{team}';"))
        players_mlb = data.fetchall()

        data = conn.execute(text(f"SELECT * FROM players_cots pc WHERE pc.team_name='{team}';"))
        players_cots = data.fetchall()

    cots_dict = [p._asdict() for p in players_cots]
    mlb_dict = [p._asdict() for p in players_mlb]

    c_names = [c['normalized_name'] for c in cots_dict]

    for row in mlb_dict:
        m_name = row['normalized_name']

        if m_name=='enrique hernandez':
            m_name = 'kike hernandez'

        if m_name=='jacob latz':
            m_name = 'jake latz'

        match, score, idx = process.extractOne(m_name, c_names, scorer=fuzz.ratio)

        if score >= 78:
            c_row = cots_dict[idx]
            matches.append({
                "mlb_name": row['normalized_name'],
                "cots_name": c_row['normalized_name'],
                "mlb_id": row['id'],
                "cots_id": c_row['id'],
                "score": score
            })
        else:
            non_matches.append({
                "mlb_name": row['normalized_name'],
                "cots_name": c_row['normalized_name'],
                "mlb_id": row['id'],
                "cots_id": c_row['id'],
                "score": score
            })

mat_df = pd.DataFrame(matches)
non_df = pd.DataFrame(non_matches)

mat_df.to_sql('mlb_match', con=engine, if_exists='replace', index=False)

print(non_df)