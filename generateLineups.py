import numpy as np
import cvxpy as cp
import cvxopt
import pandas as pd
import datetime as dt
from getProjections import get_proj
from utils import format_fpath, arg_date

def generate(date = dt.date.today(), lineups = 25, to_file = True):

    data = get_proj(date)
    fp_col = 'FP'
    df = data.copy()
    pos_mat = np.transpose(df.loc[:,('isPG','isSG','isSF','isPF','isC')].to_numpy())
    cur_proj = df[fp_col].copy()
    b = np.array([2, 2, 2, 2, 1])
    sal_max = 60000
    x = cp.Variable(len(df), boolean = True)
    salary_columns = 'Cost'
    sal = df[salary_columns].to_numpy()
    selections = None

    for round in range(1,lineups+1):
        c = cur_proj.to_numpy()
        objective = cp.Maximize(x.T @ c)
        constraints = [pos_mat @ x == b, x >= 0, x <= 1, x.T @ sal <= sal_max] #pos_mat @ x >= b_low
        prob = cp.Problem(objective, constraints)
        prob.solve(solver = 'GLPK_MI')
        picks = df.iloc[x.value == 1].copy()
        picks['round'] = round
        selections = picks if selections is None else selections.append(picks)
        cur_proj.loc[picks.index] = cur_proj.loc[picks.index].values * .95

    if to_file:
        selections.to_csv(format_fpath('line', date), index = False)
    else:
        return selections

if __name__ == "__main__":
    date = arg_date()
    generate(dt.date.today())
