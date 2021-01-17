import numpy as np
import pandas as pd
import datetime as dt
import os
from utils import get_games, team_map, format_fpath, format_name, team_translation
from sklearn.preprocessing import OneHotEncoder

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
    df = pd.DataFrame(off_def, columns = ['Offense', 'Score', 'Defense','Date'])
    team_names = team_map()
    df.loc[:,'Offense'] = df.Offense.apply(lambda x: team_names[x])
    df.loc[:,'Defense'] = df.Defense.apply(lambda x: team_names[x])
    return df

def game_data(date, lookback, save = True):
    my_path = '../game_data.csv'
    try:
        df = pd.read_csv(my_path)
    except:
        df = game_history(date, lookback)
    
    range = pd.date_range(start = date - dt.timedelta(days = date), end = date)
    for dat in range:
        if dat in df.Date:
            continue
        df.append(game_history(dat,1))
    
    if save:
        pd.to_csv(my_path, index = False)
    
    return df.set_index('Date').loc[range]

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
        mapper.drtg = (mapper['new-drtg'] + mapper.drtg)/2
        mapper.ortg = (mapper['new-ortg'] + mapper.ortg)/2
        offense = mapper.groupby('Offense').mean().ortg
        defense = mapper.groupby('Defense').mean().drtg

    return offense, defense

def proj_vs_actual(start_date, end_date):
    compare = None
    days = (end_date - start_date).days
    for offset in range(days + 1):
        cur_date = start_date + dt.timedelta(days = offset)
        try:
            stats = pd.read_csv(format_fpath('stat', cur_date))
        except:
            continue
        stats.loc[:,'Starters'] = stats.Starters.apply(lambda x: format_name(x))
        lineups = pd.read_csv(format_fpath('line',cur_date))
        lineups.loc[:,'Name'] = lineups.Name.apply(lambda x: format_name(x))
        combo = lineups.join(stats.set_index('Starters').FP.rename('actual'), on = 'Name').sort_values('Name').set_index('Name')
        combo['date'] = cur_date
        compare = combo if compare is None else compare.append(combo)
        compare.loc[:,'date'] = pd.to_datetime(compare.date)
    return compare

def oneHotTeams(df):
    enc = OneHotEncoder(sparse = False)
    enc.fit(np.reshape(df.index.values,(-1,1)))
    return enc

def feature_columns():
    return ['Blk',
        'Cost',
        'drtg',
        'Games',
        'Stl',
        'l_drtg',
        'Min',
        'l_ortg',
        'TO',
        'Reb',
        'Ast',
        'Value',
        'FP',
        'ortg',
        'Pts']

def build_feature_set(date = dt.date.today()):
    proj = pd.read_csv(format_fpath('proj', date))
    team_translation(proj)
    teams = proj.Team.drop_duplicates()
    hist = game_data(date - dt.timedelta(days = 1), 15)
    offense, defense = calc_ratings(hist)
    def_dict = defense.to_dict()
    off_dict = offense.to_dict()
    off_def = teams.apply(lambda x: off_dict[x]).rename('ortg').to_frame().join(teams.apply(lambda x: def_dict[x]).rename('drtg')).mean()
    lineups = pd.read_csv(format_fpath('line', date))
    team_translation(lineups)
    lineups['ortg'] = off_def.ortg
    lineups['drtg'] = off_def.drtg
    lineups['Games'] = len(teams)/2
    enc = oneHotTeams(defense)
    defense_mat = enc.transform(np.reshape(lineups.Opp.to_numpy(),(-1,1)))
    offense_mat = enc.transform(np.reshape(lineups.Team.to_numpy(),(-1,1)))
    lineups['l_drtg'] = np.reshape(np.matmul(defense_mat,np.reshape(defense.values,(-1,1))),(-1))
    lineups['l_ortg'] = np.reshape(np.matmul(offense_mat,np.reshape(offense.values,(-1,1))),(-1))
    return lineups