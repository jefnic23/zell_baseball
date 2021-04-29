import pandas as pd
import numpy as np
import glob
from sklearn.preprocessing import MinMaxScaler

# make two ump dfs, one of 2021 and one of 2015-2020
# if any umps are in both, use those umps in savant merge

savant = pd.concat([pd.read_csv(f, engine='python') for f in glob.glob('C:/Users/jefni/Documents/Pitcher List/statcast_data/savant_20*.csv')])
umps = pd.read_csv("C:/Users/jefni/Documents/Pitcher List/statcast_data/umpires_ids_game_pk.csv")
umps.rename(columns = {'name': 'ump'}, inplace=True)
umps = umps[umps['position'] == 'HP']
df = pd.merge(savant[['description', 'plate_x', 'plate_z', 'game_pk']], umps[['ump', 'game_year', 'game_pk']], on='game_pk')
df['active'] = np.where()

def q5(x):
    return x.quantile(0.05)
def q95(x):
    return x.quantile(0.95)
        
df = df[df['description'] == "called_strike"].groupby("ump").agg(plate_x_5 = ('plate_x', q5),
        plate_x_95 = ('plate_x', q95),
        plate_z_5 = ('plate_z', q5),
        plate_z_95 = ('plate_z', q95)
        )
df['plate_x'] = df['plate_x_95'] - df['plate_x_5']
df['plate_z'] = df['plate_z_95'] - df['plate_z_5']
df['total'] = df['plate_x'] + df['plate_z']
df['zscore'] = (df['total'].mean() - df['total']) / df['total'].std()
scaler = MinMaxScaler(feature_range=(-0.5, 0.5))
df['runs'] = scaler.fit_transform(df['zscore'].to_numpy().reshape(-1,1))
df.to_csv('umps.csv')    