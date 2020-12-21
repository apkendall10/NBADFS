import numpy as np
import cvxpy as cp
import cvxopt
import pandas as pd
import datetime as dt

data = pd.read_csv('data.csv')

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

for round in range(1,26):
    c = cur_proj.to_numpy()
    objective = cp.Maximize(x.T @ c)
    constraints = [pos_mat @ x == b, x >= 0, x <= 1, x.T @ sal <= sal_max] #pos_mat @ x >= b_low
    prob = cp.Problem(objective, constraints)
    result = prob.solve(solver = 'GLPK_MI')
    picks = df.iloc[x.value == 1].copy()
    picks['round'] = round
    selections = picks if selections is None else selections.append(picks)
    cur_proj.loc[picks.index] = cur_proj.loc[picks.index].values * .95

selections.to_csv('selections{}.csv'.format(dt.date.today()), index = False)