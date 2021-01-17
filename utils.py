import datetime as dt
import pandas as pd
import os
import unicodedata
import argparse

type_map = {
    'line': ('Lineups', 'lineup'),
    'proj': ('Projections', 'projection'),
    'stat': ('Stats', 'stats')
}

def format_fpath(type, target_date = dt.date.today()):
    folder, fname_base = type_map[type]
    fname = '{}_{}.csv'.format(fname_base, target_date)
    return os.path.join('..', folder, fname)

def team_map():
    return pd.read_csv('team_map.csv').set_index('City').code.to_dict()

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def format_name(name):
  name = strip_accents(name)
  parts = name.split(' ')
  parts[0] = parts[0].replace('.','')
  return parts[0] + ' ' + parts[1]

def get_games(date):
    url = 'https://www.basketball-reference.com/boxscores/?month={}&day={}&year={}'.format(date.month, date.day, date.year)
    tables = pd.read_html(url)
    team_map = pd.read_csv('team_map.csv').set_index('City').code.to_dict()
    games = [(team_map[tables[x].iloc[1,0]], team_map[tables[x].iloc[0,0]]) for x in range(0,len(tables)-3,3)]
    return games

def team_translater():
    return {
        'BKN': 'BRK',
        'UTAH': 'UTA', 
        'SA': 'SAS',
        'GS': 'GSW',
        'NY': 'NYK',
        'WSH': 'WAS',
        'PHX': 'PHO',
        'NO': 'NOP',
        'CHA': 'CHO'
    }

def team_translation(df):
    translator = team_translater()
    if 'Team' in df.columns:
        df.loc[:,'Team'] = df.Team.apply(lambda x: translator[x] if x in translator else x)
    if 'Opp' in df.columns:
        df.loc[:,'Opp'] = df.Opp.apply(lambda x: translator[x] if x in translator else x)

def arg_date(default = str(dt.date.today() - dt.timedelta(days = 1))):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest = 'date', default = default)
    args = parser.parse_args()
    year, month, day = [int(x) for x in args.date.split('-')]
    date = dt.date(year, month, day)
    return date