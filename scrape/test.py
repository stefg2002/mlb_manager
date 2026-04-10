import requests
from bs4 import BeautifulSoup, NavigableString

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
    xxxx