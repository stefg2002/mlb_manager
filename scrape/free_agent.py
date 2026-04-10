import requests
import pandas as pd


res = requests.get('https://statsapi.mlb.com/api/v1/people/freeAgents?season=2025')

data = res.json()['freeAgents']

fa = []
for player in data:
    if player['newTeam']['link'] == "/api/v1/teams/null":
        fa.append({'Name': player['player']['fullName']})

df = pd.DataFrame(fa)
df.to_csv('fa.csv')
print(df)
