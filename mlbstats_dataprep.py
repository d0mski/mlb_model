import mlbstatsapi
import pandas as pd
from bet_dataprep import full_slate
import re
from datetime import datetime

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
roster = []
player_id_list = []
player_position_nm = []
player_position_code = []
parentteam = []

# this works but can take a long time if all teams are playing. change to one team only for testing purposes.
# for id in team_info['team_id']:
#     curr_roster = mlb.get_team_roster(id)
#     roster.append(curr_roster)

roster = mlb.get_team_roster(110)

# grab players from each roster and if they are active
# TODO: this is pretty time-intensive. research a quicker way to complete this. may not be possible due to api call limitation.
# TODO: also am joining based on them all being in the same order, not best practice and should revisit to use .iterrows

# this works but can take a long time if all teams are playing. change to one team only for testing purposes.
# for team in roster:
#     for player in team:
for player in roster:
    if player.primaryposition.name == 'Pitcher':
        player_position_nm.append(player.primaryposition.name)
        player_position_code.append(player.primaryposition.code)
        parentteam.append(player.parentteamid)
        player_nm.append(player.fullname)
        player_status.append(player.status)
        player_id_list.append(mlb.get_people_id(player.fullname))

descriptions = [item['description'] for item in player_status]
status=pd.DataFrame(descriptions,columns=['status'])
player=pd.DataFrame({'player_nm':player_nm})
team_id=pd.DataFrame({'team_id':parentteam})
player_id=pd.DataFrame(player_id_list,columns=['player_id'])
position=pd.DataFrame({'position':player_position_nm})
position_code=pd.DataFrame({'position_code':player_position_code})

# merge player info into single dataframe
play_info = pd.merge(status, player, left_index=True, right_index=True)
play_info = pd.merge(play_info, team_id, left_index=True, right_index=True)
play_info = pd.merge(play_info, player_id, left_index=True, right_index=True)
play_info = pd.merge(play_info, position, left_index=True, right_index=True)
play_info = pd.merge(play_info, position_code, left_index=True, right_index=True)

print(play_info)
play_info.to_csv('today_player_stats.csv')

# does not support L3/L5 games, only by season
# TODO: does support game log, may have to grab last 3 from there and ping each game individually for those stats

curr_seas_yr = datetime.now().year
team_dict = {}
stats_param = ['season']
groups = ['hitting']
params = {'season': curr_seas_yr}
today_teams_stat = pd.DataFrame()

# for each row iterated grab team abbreviation while here so we can match later on
for i, row in team_info.iterrows():
    team_id = row['team_id']
    stats = mlb.get_team_stats(team_id, stats=stats_param, groups=groups, **params)
    season_hitting = stats['hitting']['season']
    for split in season_hitting.splits:
        for k, v in split.stat.__dict__.items():
            v=[v]
            team_dict[k] = v
    team_dict['team_abbr'] = row['team_abbr']
    curr_team_stats = pd.DataFrame(team_dict)
    today_teams_stat = pd.concat([today_teams_stat, curr_team_stats])

today_teams_stat.to_csv('today_team_stats.csv')