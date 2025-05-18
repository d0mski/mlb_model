# starting_pitcher
# 11/2/2024 - BJA - Script creation
# 5/18/2025 - DJD - item clean up and table creation

def grab_pitching_list():
    from bs4 import BeautifulSoup
    import requests
    from datetime import datetime
    import requests
    import pandas as pd

    today = datetime.today()
    yyyymmdd = today.strftime("%Y%m%d")

    url = 'https://www.cbssports.com/fantasy/baseball/probable-pitchers/' + yyyymmdd

    website = requests.get(url)
    scrape =BeautifulSoup(website.text, "html.parser")

    pitcher = scrape.find_all("span", attrs={"class":"CellPlayerName--long"})

    starter_p = []

    for player in pitcher:
        starter_p.append(player.text)

    starter_list = []

    for item in starter_p:
        name = item.split('\n')[0].strip()
        if name and name.upper() != "TBD":
            starter_list.append(name)
                
    pitch_df = pd.DataFrame(starter_list, columns=['player_nm'])
    return pitch_df
    pitch_df.to_csv('today_starting_pitchers.csv')