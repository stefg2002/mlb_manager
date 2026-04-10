import psycopg2
import requests
import pandas as pd
import re
from unidecode import unidecode

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
    r = requests.get('https://statsapi.mlb.com/api/v1/teams/')
    data = r.json()

    teams = get_teams(data['teams'])

    links = get_player_links(teams)
    
    players = []
    with requests.Session() as session:
        for player in links:
            s = session.get(f"https://statsapi.mlb.com{player['Link']}")
            first_name, last_name, normalized_name, age, position, bats, throws, mlb_id = get_player_info(s)
            players.append({'First Name': first_name, 'Last Name': last_name, 'Normalized Name': normalized_name,'Age': age, 'Position': position, 'Bats': bats, 'Throws': throws, 'MLBID': mlb_id, 'Team ID': player['Team ID']})
            print(f"Parsed {normalized_name}")
        

    main_roster = pd.DataFrame(players)
    return main_roster

# if __name__ == '__main__':
#     scrape()