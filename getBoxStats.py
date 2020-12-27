import pandas as pd
import datetime as dt
import numpy as np
import argparse, traceback, sys
from utils import format_fpath

def boxStats(date):
    try:
        url = 'https://www.basketball-reference.com/boxscores/?month={}&day={}&year={}'.format(date.month, date.day, date.year)
        tables = pd.read_html(url)

        team_map = pd.read_csv('team_map.csv').set_index('City').code.to_dict()
        games = [team_map[tables[x].iloc[1,0]] for x in range(0,len(tables)-3,3)]
        url_base = 'https://www.basketball-reference.com/boxscores/{}0{}.html'

        stats = None
        for g in games:
            t = pd.read_html(url_base.format(date.strftime('%Y%m%d'),g))
            for idx in [0, int(len(t)/2)]:
                temp = t[idx]
                temp.columns = temp.columns.droplevel(0)
                temp = temp.set_index('Starters').drop('Reserves').drop('Team Totals').fillna(0)
                stats = temp if stats is None else stats.append(temp)

        stats.drop(stats[stats.MP.str[:3] == 'Did'].index, inplace=True)
        stats.drop(stats[stats.MP.str[:3] == 'Not'].index, inplace=True)
        stats['FP'] = stats.PTS.astype('int') + stats.TRB.astype('int') * 1.2 + stats.AST.astype('int') * 1.5 + stats.BLK.astype('int') * 3 + stats.STL.astype('int') * 3 - stats.TOV.astype('int')
        stats.to_csv(format_fpath('stat', date))

    except:
        print('No games for {}'.format(date))
        traceback.print_exc(file = sys.stdout)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest = 'date', default = str(dt.date.today() - dt.timedelta(days = 1)))
    args = parser.parse_args()
    year, month, day = [int(x) for x in args.date.split('-')]
    date = dt.date(year, month, day)
    print('fetching data for {}'.format(date))
    boxStats(date)