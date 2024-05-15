import mlbstatsapi
import pandas as pd
from bet_dataprep import full_slate
import re
from datetime import datetime
import csv

mlb = mlbstatsapi.Mlb()

team_info = pd.read_csv('cfg_team_info.csv')

# filter by today's games 
full_slate = full_slate[full_slate['date'] == datetime.today().strftime("%Y%m%d")]
home_info = full_slate['home_team'].unique()
away_info = full_slate['away_team'].unique()

# double headers are listed with a _2 to the last team, ie SF@CHW_2. 
# only affects home_team, remove any items that end with underscore followed by number
home_info = [team for team in home_info if not re.search(r'_\d$', team)]
away_info = [team for team in away_info]
full_info = home_info + away_info

# whittle down full slate to only today's playing teams
team_info = team_info[team_info['team_abbr'].isin(full_info)]
team_rosters = pd.DataFrame()
df = pd.DataFrame()
player_nm = []
player_status = []
parent_team_id = []
roster = []

for id in team_info['team_id']:
    curr_roster = mlb.get_team_roster(id)
    roster.append(curr_roster)

# grab players from each roster and if they are active
for team in roster:
    for player in team:
        player_nm.append(player.fullname)
        player_status.append(player.status)
        parent_team_id.append(player.parentteamid)

descriptions = [item['description'] for item in player_status]
status=pd.DataFrame(descriptions,columns=['status'])
player=pd.DataFrame({'player_nm':player_nm})
team_id=pd.DataFrame({'team_id':parent_team_id})

play_info = pd.merge(status, player, left_index=True, right_index=True)
play_info = pd.merge(play_info, team_id, left_index=True, right_index=True)

print(play_info)