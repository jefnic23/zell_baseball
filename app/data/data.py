import pandas as pd
import numpy as np
import glob
from sklearn.preprocessing import MinMaxScaler

# write functions to get all data

def getUmps():
    umps = pd.read_csv("E:/Documents/Pitcher List/statcast_data/umpires_ids_game_pk.csv")
    umps['game_date'] = umps['game_date'].str.split('-').str[0]
    umps = umps[(umps['position'] == 'HP') & (umps['name'].isin(umps[umps['game_date'] == '2021']['name']))]
    ump_count = umps.groupby('name')['game_pk'].count()
    df = pd.concat([pd.read_csv(f, engine='python') for f in glob.glob('E:/Documents/Pitcher List/statcast_data/savant_20*.csv')])
    df = pd.merge(df[['description', 'plate_x', 'plate_z', 'sz_bot', 'sz_top', 'game_pk']], umps[['name', 'game_date', 'game_pk']], on='game_pk')
    df['ball'] = np.where((df['plate_x'] < -0.8308333) | 
                          (df['plate_x'] > 0.8308333) |
                          (df['plate_z'] < df['sz_bot']) |
                          (df['plate_z'] > df['sz_top']), 
                          1, 0
                          )
    df['strike'] = np.where((df['plate_x'] >= -0.8308333) & 
                            (df['plate_x'] <= 0.8308333) &
                            (df['plate_z'] >= df['sz_bot']) &
                            (df['plate_z'] <= df['sz_top']), 
                            1, 0
                            )
    df_balls = df[df['description'] == 'ball'].groupby('name').agg(wrong_ball=('strike', 'mean'))
    df_strikes = df[df['description'] == 'called_strike'].groupby('name').agg(wrong_strike=('ball', 'mean'))
    df = pd.merge(df_balls, df_strikes, on="name")
    df = pd.merge(df, ump_count, on="name")
    df['ratio'] = df['wrong_strike'] / df['wrong_ball']
    df['rank'] = df['ratio'].rank(ascending=False)
    scaler = MinMaxScaler(feature_range=(-0.75, 0.75))
    df['runs'] = scaler.fit_transform(df['rank'].to_numpy().reshape(-1,1))
    return df.to_csv('umps.csv')
    
# getUmps()


d = {"total": [],
     "x": [],
     "bet": []
     }

for x in range(50, 451, 1):
    d['total'].append(x/100)
    
scaler = MinMaxScaler(feature_range=(0.625, 1.375))
scaled = scaler.fit_transform(pd.Series(d['total']).to_numpy().reshape(-1, 1))

scale = []
for i, n in enumerate(d['total']):
    d['x'].append(scaled[i][0])
    d['bet'].append(round(n * scaled[i][0] * 20, 2))


df = pd.DataFrame(d, columns=d.keys())
df.to_csv('bets.csv', index=False)