import pandas as pd
import numpy as np
import glob
from sklearn.preprocessing import MinMaxScaler


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
    return df.to_csv('umps.csv', index=False)

    
def getBets():
    d = {"total": [],
         "x": [],
         "bet": []
         }
    for x in range(50, 451, 1):
        d['total'].append(x/100)
    scaler = MinMaxScaler(feature_range=(0.625, 1.375))
    scaled = scaler.fit_transform(pd.Series(d['total']).to_numpy().reshape(-1, 1))
    for i, n in enumerate(d['total']):
        d['x'].append(scaled[i][0])
        d['bet'].append(round(n * scaled[i][0] * 26, 1))  
    df = pd.DataFrame(d, columns=d.keys())
    return df.to_csv('bets.csv', index=False)

def getFielding():
    outs = pd.read_csv("outs_above_average.csv")
    d = {"player": [],
         "outs": []
         }
    outs['rank'] = outs['outs_above_average'].rank(ascending=False)
    scaler = MinMaxScaler(feature_range=(-0.05, 0.05))
    scaled = scaler.fit_transform(outs['rank'].to_numpy().reshape(-1, 1))
    d['player'] = outs['player_id']
    d['outs'] = [i[0] for i in scaled]
    df = pd.DataFrame(d, columns=d.keys())
    return df.to_csv('fielding.csv', index=False)
  
  
def getBullpens():
    df = pd.concat([pd.read_csv(f, engine='python') for f in glob.glob('C:/users/jefni/Documents/Pitcher List/statcast_data/savant_20*.csv')])
    df = df[(df['game_year'].isin([2018, 2019, 2020, 2021])) & (df['pitcher'].isin(df[df['game_year'] == 2021]['pitcher'].to_list()))]
    walks = df[df['events'] == 'walk'].groupby('pitcher').agg(walks=('events', 'count'))
    hits = df[df['events'].isin(['single', 
                                 'home_run', 
                                 'hit_by_pitch',
                                 'double',
                                 'triple'])
              ].groupby('pitcher').agg(hits=('events', 'count'))
    df['outs'] = np.where(df['events'].isin(['field_out',
                                              'strikeout',
                                              'fielders_choice_out',
                                              'fielders_choice',
                                              'force_out',
                                              'sac_fly',
                                              'caught_stealing_2b',
                                              'sac_bunt',
                                              'caught_stealing_3b',
                                              'pickoff_caught_stealing_2b',
                                              'other_out',
                                              'caught_stealing_home',
                                              'pickoff_caught_stealing_3b']),
                          1, 0)
    df['outs'] = np.where(df['events'].isin(['grounded_into_double_play',
                                              'double_play',
                                              'strikeout_double_play',
                                              'sac_fly_double_play']),
                          2, df['outs'])
    df['outs'] = np.where(df['events'] == 'triple_play', 3, df['outs'])
    innings = df.groupby('pitcher').agg({'outs': 'sum'})
    innings['innings'] = innings['outs'] / 3
    whip = pd.merge(walks, hits, on='pitcher')
    whip['runners'] = whip['walks'] + whip['hits']
    df = pd.merge(innings, whip, on='pitcher')
    avg_runners = df['runners'].mean()
    avg_innings = df['innings'].mean()
    df['whip'] = (df['runners'] + avg_runners) / (df['innings'] + avg_innings)
    df['rank'] = df['whip'].rank(ascending=True)
    scaler = MinMaxScaler(feature_range=(-0.06, 0.06))
    df['runs'] = scaler.fit_transform(df['rank'].to_numpy().reshape(-1,1))
    return df.to_csv('bullpens.csv')

def getPitching():
    df = pd.concat([pd.read_csv(f, engine='python') for f in glob.glob('C:/Users/jefni/Documents/Pitcher List/statcast_data/savant_20*.csv')])
    df = df[df['pitcher'].isin(df[df['game_year'] == 2021]['pitcher'])]
    dft = df.groupby("pitcher")['p_throws'].unique()
    df1 = df[df['stand'] == "L"].groupby("pitcher").agg(woba_L = ('woba_value', 'mean'),
                                                        pa_L = ('woba_value', 'count'))
    df2 = df[df['stand'] == "R"].groupby("pitcher").agg(woba_R = ('woba_value', 'mean'),
                                                        pa_R = ('woba_value', 'count'))
    dfc = pd.merge(df1, df2, on="pitcher")
    df = pd.merge(dft, dfc, on='pitcher')
    pa_L = df['pa_L'].mean()
    pa_R = df['pa_R'].mean()
    woba_L = df['woba_L'].mean()
    woba_R = df['woba_R'].mean()
    df['woba_R'] = (df['woba_R'] + woba_R) / (df['pa_R'] + pa_R)
    df['woba_L'] = (df['woba_L'] + woba_L) / (df['pa_L'] + pa_L)
    return df.to_csv("pitchers.csv")

def getHitters():
    df = pd.concat([pd.read_csv(f, engine='python') for f in glob.glob('C:/Users/jefni/Documents/Pitcher List/statcast_data/savant_20*.csv')])
    df = df[df['batter'].isin(df[df['game_year'] == 2021]['batter'])]
    dfs1 = df[df['stand'] == "L"].groupby("batter")['stand'].unique()
    dfs2 = df[df['stand'] == "R"].groupby("batter")['stand'].unique()
    df1 = df[(df['p_throws'] == "L") & (df['stand'] == 'L')].groupby("batter").agg(woba_L = ("woba_value", 'mean'),
                                                                                   pa_L = ('woba_value', 'count'))
    df2 = df[(df['p_throws'] == "R") & (df['stand'] == 'L')].groupby('batter').agg(woba_R = ('woba_value', 'mean'),
                                                                                   pa_R = ('woba_value', 'count'))
    df3 = df[(df['p_throws'] == "L") & (df['stand'] == 'R')].groupby("batter").agg(woba_L = ("woba_value", 'mean'),
                                                                                   pa_L = ('woba_value', 'count'))
    df4 = df[(df['p_throws'] == "R") & (df['stand'] == 'R')].groupby('batter').agg(woba_R = ('woba_value', 'mean'),
                                                                                   pa_R = ('woba_value', 'count'))
    dfc1 = pd.merge(df1, df2, on='batter')
    dfc2 = pd.merge(df3, df4, on='batter')
    dfl = pd.merge(dfs1, dfc1, on='batter')
    dfl['woba_R'] = (dfl['woba_R'] + woba_R) / (dfl['pa_R'] + pa_R)
    dfl['woba_L'] = (dfl['woba_L'] + woba_L) / (dfl['pa_L'] + pa_L)
    dfr = pd.merge(dfs2, dfc2, on='batter')
    dfr['woba_R'] = (dfr['woba_R'] + woba_R) / (dfr['pa_R'] + pa_R)
    dfr['woba_L'] = (dfr['woba_L'] + woba_L) / (dfr['pa_L'] + pa_L)
    df = pd.concat([dfl, dfr])
    return df.to_csv('hitters.csv')

# getUmps()
# getBets()
# getFielding()
# getBullpens()
# getPitching()
getHitters()

# pitchers = pd.read_csv('pitchers.csv', index_col='pitcher')
# hitters = pd.read_csv('hitters.csv', index_col='batter')
# scaler = MinMaxScaler(feature_range=(-0.2, 0.2))

# p = pitchers['p_throws'].to_list()
# ph = []
# for i in p:
#     ph.append(i[2])
# pitchers['p_throws'] = ph

# b = hitters['stand'].to_list()
# bh = []
# for i in b:
#     bh.append(i[2])
# hitters['stand'] = bh

# pitchers['runs_L'] = scaler.fit_transform(pitchers['woba_L'].to_numpy().reshape(-1,1))
# pitchers['runs_R'] = scaler.fit_transform(pitchers['woba_R'].to_numpy().reshape(-1,1))
# hitters['runs_L'] = scaler.fit_transform(hitters['woba_L'].to_numpy().reshape(-1,1))
# hitters['runs_R'] = scaler.fit_transform(hitters['woba_R'].to_numpy().reshape(-1,1))

# pitchers.to_csv('pitchers_test.csv')
# hitters.to_csv('hitters_test.csv')
