import pandas as pd
import datetime as dt
import numpy as np
import argparse, traceback, sys
from utils import format_fpath, get_games, arg_date

def boxStats(date):
    try:
        games = get_games(date)
        url_base = 'https://www.basketball-reference.com/boxscores/{}0{}.html'
        stats = None

        for home, away in games:
            t = pd.read_html(url_base.format(date.strftime('%Y%m%d'),home))
            for idx in [0, int(len(t)/2)]:
                temp = t[idx]
                temp.columns = temp.columns.droplevel(0)
                temp = temp.set_index('Starters').drop('Reserves').drop('Team Totals').fillna(0)
                if idx == 0:
                    temp['Loc'] = 'Away'
                    temp['Team'] = away
                    temp['Opp'] = home
                else: 
                    temp['Loc'] = 'Home'
                    temp['Team'] = home
                    temp['Opp'] = away
                stats = temp if stats is None else stats.append(temp)

        stats.drop(stats[stats.MP.str[:3] == 'Did'].index, inplace=True)
        stats.drop(stats[stats.MP.str[:3] == 'Not'].index, inplace=True)
        stats['FP'] = stats.PTS.astype('int') + stats.TRB.astype('int') * 1.2 + stats.AST.astype('int') * 1.5 + stats.BLK.astype('int') * 3 + stats.STL.astype('int') * 3 - stats.TOV.astype('int')
        stats.to_csv(format_fpath('stat', date))

    except:
        print('No games for {}'.format(date))
        traceback.print_exc(file = sys.stdout)

def statRange(start_date, end_date):
    stats = None
    for date in pd.date_range(start_date,end_date):
        try:
            temp = pd.read_csv(format_fpath('stat',date.date()))
            temp['Date'] = date
        except:
            continue
        stats = temp if stats is None else stats.append(temp)
    return stats

if __name__ == "__main__":
    date = arg_date()
    print('fetching data for {}'.format(date))
    boxStats(date)