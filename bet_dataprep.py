import requests
import pandas as pd
from datetime import datetime
from apikey import key

url = "https://tank01-mlb-live-in-game-real-time-statistics.p.rapidapi.com/getMLBBettingOdds"

house_list = ['fanduel']
today = datetime.today()
yyyymmdd = today.strftime("%Y%m%d")

querystring = {"gameDate":str(20240924),"playerProps":"false"}

# TODO: check if apikey.py exists, if not then create user input for manual key enter 
#       and use it to generate the file if it does not already exist
#       will also have to include functionality to change it if ever needed.

headers = {
	"X-RapidAPI-Key": key,
	"X-RapidAPI-Host": "tank01-mlb-live-in-game-real-time-statistics.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)
# TODO: Insert a check here to see if this day's betting data already exists to not waste a pull
# TODO: Add a check y/N if we want data pulled - so we have option to get refreshed data

json_data = response.json()

df_norm = pd.json_normalize(json_data, max_level=1)
dfs = {}
gameIDs = []
full_slate = pd.DataFrame()

for col in df_norm.columns:
    # Convert each dictionary into a DataFrame
    dfs[col] = pd.DataFrame(df_norm[col].tolist())

# grab list of games for today and append in list
for column in dfs:
    if "@" in column:
        gameIDs.append(column)
# loop through each betting house to get different odds
# TODO: make this house list more dynamic. some houses aren't available for every game so we are excluding some, like draft kings, espnbet, bet rivers
        for item in house_list:
            odds_df = dfs[column][item].apply(pd.Series)
            odds_df['house'] = item
            odds_df['game'] = column.split("_",1)[1]
            full_slate = pd.concat([full_slate,odds_df])

full_slate['date'] = yyyymmdd
full_slate['home_team'] = full_slate['game'].str.split("@").str[1]
full_slate['away_team'] = full_slate['game'].str.split("@").str[0]

full_slate.to_csv('today_game_slate.csv')

# TODO: Append to a "master" csv 

# TODO: Make csv on a shared location. In meantime set it to a fixed local location.

# TODO: Run model over data