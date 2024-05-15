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

# TODO: remove these and have the loop join directly to dataframe.
player_nm = []
player_status = []
parent_team_id = []
roster = []
player_id_list = []

# this works but can take a long time if all teams are playing. change to one team only for testing purposes.
# for id in team_info['team_id']:
#     curr_roster = mlb.get_team_roster(id)
#     roster.append(curr_roster)

roster = mlb.get_team_roster(110)

# grab players from each roster and if they are active
# TODO: this is pretty time-intensive. research a quicker way to complete this. may not be possible due to api call limitation.
# TODO: also am joining based on them all being in the same order, not best practice and should revisit.

# this works but can take a long time if all teams are playing. change to one team only for testing purposes.
# for team in roster:
#     for player in team:
for player in roster:
    player_nm.append(player.fullname)
    player_status.append(player.status)
    parent_team_id.append(player.parentteamid)
    player_id_list.append(mlb.get_people_id(player.fullname))

descriptions = [item['description'] for item in player_status]
status=pd.DataFrame(descriptions,columns=['status'])
player=pd.DataFrame({'player_nm':player_nm})
team_id=pd.DataFrame({'team_id':parent_team_id})
player_id=pd.DataFrame(player_id_list,columns=['player_id'])

play_info = pd.merge(status, player, left_index=True, right_index=True)
play_info = pd.merge(play_info, team_id, left_index=True, right_index=True)
play_info = pd.merge(play_info, player_id, left_index=True, right_index=True)

# does not support L3/L5 games, only by season,
# does support game log, may have to grab last 3 from there and ping each game individually for those stats
stats = ['season', 'career']
groups = ['hitting', 'pitching']
params = {'season': 2024}
data = []
split_dict = {}
stat_dict = mlb.get_player_stats(668939, stats=stats, groups=groups, **params)
season_hitting_stat = stat_dict['hitting']['season']
for split in season_hitting_stat.splits:
    for k, v in split.stat.__dict__.items():
         v=[v]
         split_dict[k] = v
    data.append(split_dict)
     
df = pd.DataFrame(split_dict)
print(df)
