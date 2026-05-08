from sqlalchemy import create_engine, text
import pandas as pd
import math
import re

import requests
from bs4 import BeautifulSoup
from unidecode import unidecode

from config import settings

def get_additional_cbt(player,extra_cbt):
    for i,value in extra_cbt.iterrows():
        if player[0] == value[0]:
            if isinstance(value[18],float): #ignore blank NaN values in the CBT column
                if math.isnan(value[18]):
                    continue
            return value[18].replace("$","").replace(",","").replace("(","-").replace(")","") if isinstance(value[18],str) else "0"
    return "0"

# def get_tax_level(total_sum):
    #     diff = total_sum-244000000
    #     if (diff<=20000000 and total_sum>244000000):
    #         return 1
    #     elif(diff>20000000 and diff<=40000000):
    #         return 2
    #     elif(diff>40000000 and diff<=60000000):
    #         return 3
    #     elif(diff>60000000):
    #         return 4
    #     else:
    #         return 0

    # def get_tax_bill(total_sum,years):
    #     rate1 = [0.2,0.32,0.625,0.8] #First time payor
    #     rate2 = [0.3,0.42,0.75,0.9] #Second time payor
    #     rate3 = [0.5,0.62,0.95,1.1] #Third time payor

    #     rate = []
    #     match years:
    #         case 1:
    #             rate = rate1
    #         case 2:
    #             rate = rate2
    #         case _:
    #             rate = rate3

    #     match(get_tax_level(total_sum)):
    #         case 0:
    #             return 0
    #         case 1:
    #             return (total_sum-244000000)*rate[0]
    #         case 2:
    #             return (20000000*rate[0])+((total_sum-264000000)*rate[1])
    #         case 3:
    #             return (20000000*rate[0])+(20000000*rate[1])+((total_sum-284000000)*rate[2])
    #         case 4:
    #             return (20000000*rate[0])+(20000000*rate[1])+(20000000*rate[2])+((total_sum-304000000)*rate[3])

    # def get_years(col0):
    #     for text in col0:
    #         if isinstance(text,str):
    #             if "payor in 2026" in text:
    #                 years = text[text.find("(")+1:text.find("-")]
    #                 match years:
    #                     case "first":
    #                         return 1
    #                     case "second":
    #                         return 2
    #                     case _:
    #                         return 3

def scrape():

    engine = create_engine(str(settings.postgres_url))

    response = requests.get('https://legacy.baseballprospectus.com/compensation/cots/')

    soup = BeautifulSoup(response.text,'html.parser')

    tables=soup.find_all('table')

    ls=[]
    for table in tables:
        if table.find('h5', string='PROJECTED 2025 PAYROLLS'):
            break

        ls.append(table.find_all('a', href=lambda x: x and 'https://docs.google.com' in x))

    a = [item for sub in ls for item in sub]

    links = []
    for link in a:
        links.append(link.get('href'))               

    contracts=pd.DataFrame()
    for link in links:
        
        if '/edit' in link:
            spreadsheet_link = link.split('/edit')[0] + '/export?format=csv'
        elif "/pub" in link:
            spreadsheet_link = link.split('/pub')[0] + '/pub?output=csv'

        print(f'Parsing csv from {spreadsheet_link}')
        csv = pd.read_csv(spreadsheet_link,header=None,skiprows=9,dtype=str)

        # grab only the first box
        end = 0
        for i,value in enumerate(csv[0]):
            if pd.isna(value) or str(value).strip() == "":
                end=i
                break

        result = csv.iloc[:end].copy().drop_duplicates()

        #grab main roster
        main_roster = result.dropna(subset=[0,1,2])

        #Grab CBT summary
        last = 0
        for i,value in enumerate(result[0]):
            if str(value).strip() == main_roster.iloc[-1][0]:
                last=i
                break

        summary=result[last+1:]

        extra_cbt = summary[summary[0].str.contains(",",na=False)] #only grab player names
        misc = summary[~summary[0].str.contains(",",na=False)] #Grab other information

        #Players on the 40-man roster including extra CBT calculations (either addition or subtraction)
        ls = []
        for i,player in main_roster.iterrows():
            name_raw = " ".join(player[0].split(", ")[::-1]).replace("*","")
            name = re.sub(r'\s+[A-Z]\.?(?=\s|$)', '', name_raw, count=1)

            normalized_name=re.sub(r'[^\w\s]','', unidecode(name.lower()))

            cbt = player[18].replace("$","").replace(",","") if isinstance(player[18],str) else "0"
            extra = get_additional_cbt(player,extra_cbt)
            ls.append({'name': name, 'normalized_name': normalized_name, 'cbt': int(cbt) + int(extra)})
            print(normalized_name)

        payroll = pd.DataFrame(ls)
        
        
        #Non-roster CBT additions (dead money) - players with guaranteed contracts not on the 40-man roster
        # ls = []
        # for i,player in extra_cbt.iterrows():
        #     if not main_roster[0].isin([player[0]]).any():
        #         name = player[0]
        #         cbt = player[18].replace("$","").replace(",","").replace("(","-").replace(")","") if isinstance(player[18],str) else "0"
        #         ls.append({'Name': name,'CBT': cbt})
        # dead_payroll = pd.DataFrame(ls)

        contracts=pd.concat([contracts,payroll],ignore_index=True)
    
    contracts['id'] = range(1, len(contracts) + 1)
    contracts.to_sql('players_cots', con=engine, if_exists='replace', index=False)
    with engine.connect() as conn:
        conn.execute(text('ALTER TABLE players_cots ADD PRIMARY KEY (id);'))
        conn.commit()

    return contracts    

if __name__ == '__main__':
    scrape()


