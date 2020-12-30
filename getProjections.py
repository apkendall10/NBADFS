import pandas as pd, numpy as np
from bs4 import BeautifulSoup
import requests
from utils import format_fpath

def parse_player(player):
    temp = [x.strip() for x in player.split("\n") if len(x.strip()) > 0]
    return temp[1], temp[2], temp[5], temp[3], temp[6]

url = "https://www.numberfire.com/nba/daily-fantasy/daily-basketball-projections"
soup = BeautifulSoup(requests.get(url).text, features="lxml")
table = soup.find_all("table")
row_marker = 0
data = []
for row in table[3].find_all("tr"):
    columns = row.find_all("td")
    data.append([x.get_text().strip() for x in columns])

cols = "Player,FP,Cost,Value,Min,Pts,Reb,Ast,Stl,Blk,TO".split(",")
df = pd.DataFrame(data, columns=cols).dropna()

player_data = df.Player.apply(parse_player)
df = df.join(
    pd.DataFrame(
        player_data.to_list(),
        index=player_data.index,
        columns=["Name", "Pos", "Team", "Opp", "Game"],
    )
).drop("Player", axis=1)

for pos in df.Pos.unique():
    col = 'is{}'.format(pos)
    df[col] = (df.Pos == pos).astype('int').to_numpy()

df.loc[:,'Cost'] = df.Cost.apply(lambda x: int(''.join(x[1:].split(','))))

df.to_csv(format_fpath('proj'), index=False)