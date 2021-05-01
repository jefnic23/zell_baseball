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
    scaler = MinMaxScaler(feature_range=(-1, 1))
    df['runs'] = scaler.fit_transform(df['rank'].to_numpy().reshape(-1,1))
    return df.to_csv('umps.csv')
    
getUmps()


### old code, gets strike zone size by plate_x/z quantile ###

# def q5(x):
#     return x.quantile(0.05)
# def q95(x):
#     return x.quantile(0.95)
        
# df = df[df['description'] == "called_strike"].groupby("name").agg(plate_x_5 = ('plate_x', q5),
#         plate_x_95 = ('plate_x', q95),
#         plate_z_5 = ('plate_z', q5),
#         plate_z_95 = ('plate_z', q95)
#         )
# df['plate_x'] = df['plate_x_95'] - df['plate_x_5']
# df['plate_z'] = df['plate_z_95'] - df['plate_z_5']
# df['total'] = df['plate_x'] + df['plate_z']
# df['zscore'] = (df['total'].mean() - df['total']) / df['total'].std()
# scaler = MinMaxScaler(feature_range=(-0.9, 1))
# df['runs'] = scaler.fit_transform(df['zscore'].to_numpy().reshape(-1,1))