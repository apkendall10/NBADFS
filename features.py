import numpy as np
import pandas as pd
import datetime as dt
import os
from utils import get_games, team_map

def game_count(date):
    return len(get_games(date))

def game_history(date, lookback):
    off_def = []
    url_template = 'https://www.basketball-reference.com/boxscores/?month={}&day={}&year={}'
    for offset in range(lookback):
        current_date = date - dt.timedelta(days = offset)
        url = url_template.format(current_date.month, current_date.day, current_date.year)
        try:
            tables = pd.read_html(url)
        except:
            continue
        for game in range(0,len(tables)-3,3):
            box = tables[game]
            off_def.append([box.iloc[1,0], box.iloc[1,1], box.iloc[0,0],current_date])
            off_def.append([box.iloc[0,0], box.iloc[0,1], box.iloc[1,0],current_date])
    return pd.DataFrame(off_def, columns = ['Offense', 'Score', 'Defense','Date'])

def calc_ratings(df, iterations = 50):
    offense = df.groupby('Offense').mean().Score.rename('ortg')
    defense = df.groupby('Defense').mean().Score.rename('drtg')
    for _ in range(iterations):
        mapper = df.join(offense, on = 'Offense').join(defense, on = 'Defense')
        mapper['new-ortg'] = mapper.Score * 2 - mapper['drtg']
        mapper['new-drtg'] = mapper.Score * 2 - mapper['ortg']
        if((mapper['new-ortg'] - mapper.ortg).abs().sum() + (mapper['new-drtg'] - mapper.drtg).abs().sum() < 1):
            print('Stopping early')
            break
        mapper.drtg = mapper['new-drtg']
        mapper.ortg = mapper['new-ortg']
        offense = mapper.groupby('Offense').mean().ortg
        defense = mapper.groupby('Defense').mean().drtg

    team_names = team_map()
    defense.index = defense.index.to_series().apply(lambda x: team_names[x]).values
    offense.index = offense.index.to_series().apply(lambda x: team_names[x]).values
    return offense, defense