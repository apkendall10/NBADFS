import numpy as np
import pandas as pd
import os
from utils import get_games

def game_count(date):
    return len(get_games(date))

def fanduel_data():
    return pd.read_csv(os.path.join('..','FanDuelData'))