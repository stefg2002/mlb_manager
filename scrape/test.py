import psycopg2
import requests
import pandas as pd
from scrape_cots import TeamScraper

def get_player_info(res):
    p_data = res.json()['people'][0]

    first_name = p_data['useName']
    last_name = p_data['useLastName']
    age = p_data['currentAge']
    position = p_data['primaryPosition']['abbreviation']
    bats = p_data['batSide']['code']
    throws = p_data['pitchHand']['code']
    mlb_id = p_data['id']
    return first_name, last_name, age, position, bats, throws, mlb_id

def get_teams(data):
    teams = []
    with requests.Session() as session:
        for team in data:
            if not 'name' in team['league']:
                continue
            if team['league']['name'] == 'American League' or team['league']['name'] == 'National League':
                teams.append({'Full Name': team['name'],'Franchise Name': team['franchiseName'],'Club Name': team['clubName'],'League': team['league']['name'],'Division': team['division']['name'],'Roster': None,'MLBID': team['id']})
        
        for team in teams:
            s = session.get(f"https://statsapi.mlb.com/api/v1/teams/{team['MLBID']}/roster")
            r_data = s.json()['roster']
            ids = []
            for player in r_data:
                ids.append(player['person']['id']) 
            team['Roster'] = ids
        print(f'Parsed {team['Club Name']}')
    return teams

# def get_rosters(teams):
#     pass

# Put all player ids into one
def get_player_links(teams):
    links = []
    for team in teams:
        for player in team['Roster']:
            links.append({'Link': f'/api/v1/people/{player}', 'Team ID': team['MLBID']})
    return links

DB_NAME = "mlb_database"
DB_USERNAME = "postgres"
DB_PASSWORD = "syncopate"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"

r = requests.get('https://statsapi.mlb.com/api/v1/teams/')
data = r.json()

teams = get_teams(data['teams'])
team_df = pd.DataFrame(teams)
# with requests.Session() as session:
#     for id in team_ids:
#         s = session.get(f"https://statsapi.mlb.com/api/v1/teams/{id}/roster")
#         r_data = s.json()['roster']
#         rosters.append(r_data)
#         print(f'Parsed {id}')

links = get_player_links(teams)
# for roster in rosters:
#     for player in roster:
#         links.append(player['person']['link'])

players = []
with requests.Session() as session:
    for player in links:
        s = session.get(f"https://statsapi.mlb.com{player['Link']}")
        first_name, last_name, age, position, bats, throws, mlb_id = get_player_info(s)
        players.append({'First Name': first_name, 'Last Name': last_name, 'Age': age, 'Position': position, 'Bats': bats, 'Throws': throws, 'MLBID': mlb_id, 'Team ID': player['Team ID']})
        print(f"Parsed {first_name} {last_name}")
    

main_roster = pd.DataFrame(players)
print(main_roster)

# scraper = TeamScraper('tor')

# cbt = scraper.get_main_roster()
# for index,row in main_roster.iterrows():
#     comb = f"{row['First Name']} {row['Last Name']}"
#     if cbt['Name'].str.contains(comb).any():
#         print(f"{comb}")
    

try:
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USERNAME, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    cur = conn.cursor()

    insert_teams = """
    INSERT INTO teams (full_name,franchise_name,club_name,league,division,roster,team_id) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    for index,row in team_df.iterrows():
        cur.execute(insert_teams, (row['Full Name'],row['Franchise Name'],row['Club Name'],row['League'],row['Division'],row['Roster'],row['MLBID']))
        print(f"Adding {row['Club Name']}")

    insert_players  = """
    INSERT INTO players (first_name,last_name,age,position,bats,throws,player_id,team_id) VALUES (%s, %s, %s, %s, %s, %s, %s,%s)
    """
    for index,row in main_roster.iterrows():
        cur.execute(insert_players, (row['First Name'],row['Last Name'],row['Age'],row['Position'],row['Bats'],row['Throws'],row['MLBID'],row['Team ID']))
        print(f"Adding {row['First Name']} {row['Last Name']}")

    conn.commit()
except psycopg2.Error as e:
    print(f"Database Error: {e}")
finally:
    if cur:
        cur.close()
    if conn:
        conn.close()