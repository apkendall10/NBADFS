import datetime as dt
import os

def format_fpath(type):
    fname_base = 'projection' if type == 'proj' else 'lineup'
    folder = 'Projections' if type == 'proj' else 'Lineups'
    fname = '{}_{}.csv'.format(fname_base, dt.date.today())
    return os.path.join('..', folder, fname)