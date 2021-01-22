import pandas as pd, numpy as np
from bs4 import BeautifulSoup
import requests
from utils import format_fpath, player_team_map, format_name

def parse_player(player):
    temp = [x.strip() for x in player.split("\n") if len(x.strip()) > 0]
    return temp[1], temp[2], temp[5], temp[3], temp[6]

def get_proj(date):
    df = pd.read_csv(format_fpath('proj',date))
    df.loc[:,'Name'] = df.Name.apply(lambda x: format_name(x))
    mapper = player_team_map()
    listed = df.Name.apply(lambda x: x in mapper.index)
    df['PTeam'] = 'UNK'
    df.loc[listed, 'PTeam'] = df.loc[listed].Name.apply(lambda x: mapper.loc[x]).values
    df['Loc'] = df.apply(lambda x: 'Home' if x.PTeam == x.Team else 'Away', axis = 1)
    df['Name'] = df.index.values
    df.index = range(len(df))
    away = df[df.Loc == 'Away'].index
    temp = df.loc[away,'Team'] 
    df.loc[away,'Team'] = df.loc[away,'Opp'] 
    df.loc[away,'Opp'] = temp
    df.set_index('Name')
    return df

def main():
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

if __name__ == "__main__":
    main()