import requests
import pandas as pd
from datetime import datetime
from apikey import key

url = "https://tank01-mlb-live-in-game-real-time-statistics.p.rapidapi.com/getMLBBettingOdds"

house_list = ['fanduel']
today = datetime.today()
yyyymmdd = today.strftime("%Y%m%d")

querystring = {"gameDate":str(yyyymmdd),"playerProps":"false"}

# create user input for key and use it to generate apikey.py if it does not already exist
headers = {
	"X-RapidAPI-Key": key,
	"X-RapidAPI-Host": "tank01-mlb-live-in-game-real-time-statistics.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)
# Insert a check here to see if this day's betting data already exists to not waste a pull
# Add a check y/N if we want data pulled - so we have option to get refreshed data

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

# Append to a "master" csv 

# Make csv on a shared location. In meantime set it to a fixed local location.

# Run model over data