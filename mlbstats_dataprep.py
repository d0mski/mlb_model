import mlbstatsapi
import pandas as pd
from bet_dataprep import full_slate
import re

mlb = mlbstatsapi.Mlb()

team_info = pd.read_csv('cfg_team_info.csv')

home_info = full_slate['home_team'].unique()
away_info = full_slate['away_team'].unique()

# double headers are listed with a _2 to the last team, ie SF@CHW_2. 
# only affects home_team, remove any items that end with underscore followed by number
# turn both to lists while here
home_info = [team for team in home_info if not re.search(r'_\d$', team)]
away_info = [team for team in away_info]