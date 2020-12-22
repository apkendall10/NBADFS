import datetime as dt
import pandas as pd
import os

type_map = {
    'line': ('Lineups', 'lineup'),
    'proj': ('Projection', 'Projections'),
    'stat': ('Stats', 'stats')
}

def format_fpath(type, target_date = dt.date.today()):
    fname_base, folder = type_map[type]
    fname = '{}_{}.csv'.format(fname_base, target_date)
    return os.path.join('..', folder, fname)

def team_map():
    return pd.read_csv('team_map.csv').set_index('City').code.to_dict()