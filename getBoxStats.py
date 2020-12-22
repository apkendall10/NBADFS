import pandas as pd
import datetime as dt
import numpy as np
from utils import format_fpath


date = dt.date(2020,1,10)
url = 'https://www.basketball-reference.com/boxscores/?month={}&day={}&year={}'.format(date.month, date.day, date.year)
tables = pd.read_html(url)
team_map = pd.read_csv('team_map.csv').set_index('City').code.to_dict()
games = [team_map[tables[x].iloc[1,0]] for x in range(0,len(tables)-3,3)]

url_base = 'https://www.basketball-reference.com/boxscores/{}0{}.html'
home_full_index = 0
away_full_index = 8
stats = None
for g in games:
  t = pd.read_html(url_base.format(date.strftime('%Y%m%d'),g))
  for idx in [home_full_index, away_full_index]:
    temp = t[idx]
    temp.columns = temp.columns.droplevel(0)
    temp = temp.set_index('Starters').drop('Reserves').drop('Team Totals')
    stats = temp if stats is None else stats.append(temp)

stats.drop(stats[stats.MP.str[:3] == 'Did'].index, inplace=True)
stats['FP'] = stats.PTS.astype('int') + stats.TRB.astype('int') * 1.2 + stats.AST.astype('int') * 1.5 + stats.BLK.astype('int') * 3 + stats.STL.astype('int') * 3 - stats.TOV.astype('int')
stats.to_csv(format_fpath('stat', date))