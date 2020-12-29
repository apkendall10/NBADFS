import datetime as dt
import pandas as pd
import os
import unicodedata

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
    games = [team_map[tables[x].iloc[1,0]] for x in range(0,len(tables)-3,3)]
    return games