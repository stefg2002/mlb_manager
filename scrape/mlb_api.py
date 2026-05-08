from sqlalchemy import create_engine, inspect, text
import requests
import pandas as pd
import re
from unidecode import unidecode

from config import settings

def get_player_info(res):
    p_data = res.json()['people'][0]

    first_name = p_data['useName']
    last_name = p_data['useLastName']
    age = p_data['currentAge']
    position = p_data['primaryPosition']['abbreviation']
    bats = p_data['batSide']['code']
    throws = p_data['pitchHand']['code']
    mlb_id = p_data['id']

    normalized_name=re.sub(r'[^\w\s]','', unidecode(f'{first_name} {last_name}'.lower()))

    return first_name, last_name, normalized_name, age, position, bats, throws, mlb_id

def get_teams(data):
    teams = []
    with requests.Session() as session:
        for team in data:
            if not 'name' in team['league']:
                continue
            if team['league']['name'] == 'American League' or team['league']['name'] == 'National League':
                teams.append({'Full Name': team['name'],'Franchise Name': team['franchiseName'],'Club Name': team['clubName'],'League': team['league']['name'],'Division': team['division']['name'],'Roster': None,'MLBID': team['id']})
        
        for team in teams:
            s = session.get(f"https://statsapi.mlb.com/api/v1/teams/{team['MLBID']}/roster/40Man")
            r_data = s.json()['roster']
            ids = []
            for player in r_data:
                ids.append(player['person']['id']) 
            team['Roster'] = ids
        print(f'Parsed {team['Club Name']}')
    return teams


# Put all player ids into one
def get_player_links(teams):
    links = []
    for team in teams:
        for player in team['Roster']:
            links.append({'Link': f'/api/v1/people/{player}', 'Team ID': team['MLBID']})
    return links

def scrape():

    engine = create_engine(str(settings.postgres_url))

    r = requests.get('https://statsapi.mlb.com/api/v1/teams/')
    data = r.json()

    teams = get_teams(data['teams'])

    links = get_player_links(teams)
    
    players = []
    with requests.Session() as session:
        i=0
        for player in links:
            s = session.get(f"https://statsapi.mlb.com{player['Link']}")
            first_name, last_name, normalized_name, age, position, bats, throws, mlb_id = get_player_info(s)
            players.append({'first_name': first_name, 'last_name': last_name, 'normalized_name': normalized_name, 'age': age, 'position': position, 'bats': bats, 'throws': throws, 'mlb_id': mlb_id, 'team_id': player['Team ID']})
            print(f"Parsed {normalized_name}")
        
    players_df = pd.DataFrame(players)
    players_df['id'] = range(1, len(players_df) + 1)


    players_df.to_sql('players_mlb', con=engine, if_exists='replace', index=False)
    with engine.connect() as conn:
        conn.execute(text('ALTER TABLE players_mlb ADD PRIMARY KEY (id);'))
        conn.commit()

    return players_df

if __name__ == '__main__':
    scrape()