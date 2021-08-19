import pandas as pd
import numpy as np
import glob
from sklearn.preprocessing import MinMaxScaler


def getUmps():
    umps = pd.read_csv("E:/Documents/Pitcher List/statcast_data/umpires_ids_game_pk.csv")
    umps['game_date'] = umps['game_date'].str.split('-').str[0]
    umps = umps[(umps['position'] == 'HP') & (umps['id'].isin(umps[umps['game_date'] == '2021']['id']))]
    ump_count = umps.groupby('id')['game_pk'].count()
    df = pd.concat([pd.read_csv(f, engine='python') for f in glob.glob('E:/Documents/Pitcher List/statcast_data/savant_20*.csv')])
    df = pd.merge(df[['description', 'plate_x', 'plate_z', 'sz_bot', 'sz_top', 'game_pk']], umps[['id', 'name', 'game_date', 'game_pk']], on='game_pk')
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
    df_balls = df[df['description'] == 'ball'].groupby('id').agg(wrong_ball=('strike', 'mean'))
    df_strikes = df[df['description'] == 'called_strike'].groupby('id').agg(wrong_strike=('ball', 'mean'))
    df = pd.merge(df_balls, df_strikes, on="id")
    df = pd.merge(df, ump_count, on="id")
    df['ratio'] = df['wrong_strike'] / df['wrong_ball']
    scaler = MinMaxScaler(feature_range=(-0.5, 0.5))
    df['runs'] = scaler.fit_transform(df['ratio'].to_numpy().reshape(-1,1))
    return df.to_csv('umps.csv')

    
def getBets():
    d = {"total": [],
         "bet": []
         }
    for x in range(1, 201, 1):
        d['total'].append(x/100)
    scaler = MinMaxScaler(feature_range=(210, 610))
    scaled = scaler.fit_transform(pd.Series(d['total']).to_numpy().reshape(-1, 1))
    for i, n in enumerate(d['total']):
        # d['x'].append(scaled[i][0])
        d['bet'].append(5 * round(scaled[i][0] / 5))
    df = pd.DataFrame(d, columns=d.keys())
    return df.to_csv('bets.csv', index=False)


def getFielding():
    outs = pd.read_csv("outs_above_average.csv")
    d = {"player": [],
         "outs": []
         }
    outs['rank'] = outs['outs_above_average'].rank(ascending=False)
    scaler = MinMaxScaler(feature_range=(-0.03, 0.03))
    scaled = scaler.fit_transform(outs['rank'].to_numpy().reshape(-1, 1))
    d['player'] = outs['player_id']
    d['outs'] = [i[0] for i in scaled]
    df = pd.DataFrame(d, columns=d.keys())
    return df.to_csv('fielding.csv', index=False)
  
  
def getBullpens():
    df = pd.concat([pd.read_csv(f, engine='python') for f in glob.glob('E:/Documents/Pitcher List/statcast_data/savant_20*.csv')])
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
    scaler = MinMaxScaler(feature_range=(-0.3125, 0.2475))
    df['runs'] = scaler.fit_transform(df['whip'].to_numpy().reshape(-1,1))
    return df.to_csv('bullpens.csv')


def getPitching():
    df = pd.read_csv('D:/Documents/Pitcher List/statcast_data/savant_2021.csv')
    
    out_1 = ['strikeout', 'field_out', 'caught_stealing_2b', 'force_out', 'sac_bunt', 'sac_fly', 'fielders_choice', 'fielders_choice_out', 'caught_stealing_3b', 'other_out']
    out_2 = ['grounded_into_double_play', 'strikeout_double_play', 'double_play', 'sac_fly_double_play']
    out_3 = ['triple_play']
    walks_hits = ['single', 'home_run', 'double', 'walk', 'hit_by_pitch', 'triple']
    df['outs'] = np.where(df['events'].isin(out_1), 1, 0)
    df['outs'] = np.where(df['events'].isin(out_2), 2, df['outs'])
    df['outs'] = np.where(df['events'].isin(out_3), 3, df['outs'])
    df['walks_hits'] = np.where(df['events'].isin(walks_hits), 1, 0)
    dfi = df.groupby(['pitcher', 'game_pk']).agg({'outs': 'sum'})
    dfi['innings'] = dfi['outs'] / 3
    # dfi['ip'] = round(dfi['walks_hits'] / dfi['innings'], 2)
    dfi = dfi.groupby('pitcher').agg(ips = ('innings', 'mean'),
                                     ip = ('innings', 'sum')
                                     )
    df_wh = df.groupby('pitcher').agg({'walks_hits': 'sum'})
    df_whip = pd.merge(dfi, df_wh, on='pitcher')
    df_whip['whip'] = round(df_whip['walks_hits'] / df_whip['ip'], 2)
    dft = df.groupby("pitcher")['p_throws'].unique().str[0]
    df1 = df[df['stand'] == "L"].groupby("pitcher").agg(woba_L = ('woba_value', 'sum'),
                                                        pa_L = ('woba_value', 'count'))
    df2 = df[df['stand'] == "R"].groupby("pitcher").agg(woba_R = ('woba_value', 'sum'),
                                                        pa_R = ('woba_value', 'count'))
    dfc = pd.merge(df1, df2, on="pitcher")
    dfx = pd.merge(dft, dfc, on='pitcher')
    df = pd.merge(dfx, df_whip, on='pitcher')
    pa_L = df['pa_L'].mean()
    pa_R = df['pa_R'].mean()
    woba_L = df['woba_L'].mean()
    woba_R = df['woba_R'].mean()
    df['woba_R'] = (df['woba_R'] + woba_R) / (df['pa_R'] + pa_R)
    df['woba_L'] = (df['woba_L'] + woba_L) / (df['pa_L'] + pa_L)
    return df.drop(columns=['ip', 'walks_hits']).to_csv("pitchers.csv")


def getHitters():
    df = pd.read_csv('D:/Documents/Pitcher List/statcast_data/savant_2021.csv')
    
    dfs1 = df[df['stand'] == "L"].groupby("batter")['stand'].unique().str[0]
    dfs2 = df[df['stand'] == "R"].groupby("batter")['stand'].unique().str[0]
    df1 = df[(df['p_throws'] == "L") & (df['stand'] == 'L')].groupby("batter").agg(woba_L = ("woba_value", 'sum'),
                                                                                   pa_L = ('woba_value', 'count'))
    df2 = df[(df['p_throws'] == "R") & (df['stand'] == 'L')].groupby('batter').agg(woba_R = ('woba_value', 'sum'),
                                                                                   pa_R = ('woba_value', 'count'))
    df3 = df[(df['p_throws'] == "L") & (df['stand'] == 'R')].groupby("batter").agg(woba_L = ("woba_value", 'sum'),
                                                                                   pa_L = ('woba_value', 'count'))
    df4 = df[(df['p_throws'] == "R") & (df['stand'] == 'R')].groupby('batter').agg(woba_R = ('woba_value', 'sum'),
                                                                                   pa_R = ('woba_value', 'count'))
    dfc1 = pd.merge(df1, df2, on='batter')
    dfc2 = pd.merge(df3, df4, on='batter')
    
    dfl = pd.merge(dfs1, dfc1, on='batter')
    woba_L = dfl['woba_L'].mean()
    woba_R = dfl['woba_R'].mean()
    pa_L = dfl['pa_L'].mean()
    pa_R = dfl['pa_R'].mean()
    dfl['woba_R'] = (dfl['woba_R'] + woba_R) / (dfl['pa_R'] + pa_R)
    dfl['woba_L'] = (dfl['woba_L'] + woba_L) / (dfl['pa_L'] + pa_L)
    
    dfr = pd.merge(dfs2, dfc2, on='batter')
    woba_L = dfr['woba_L'].mean()
    woba_R = dfr['woba_R'].mean()
    pa_L = dfr['pa_L'].mean()
    pa_R = dfr['pa_R'].mean()
    dfr['woba_R'] = (dfr['woba_R'] + woba_R) / (dfr['pa_R'] + pa_R)
    dfr['woba_L'] = (dfr['woba_L'] + woba_L) / (dfr['pa_L'] + pa_L)
    df = pd.concat([dfl, dfr])
    return df.to_csv('hitters.csv')

def getMatchups():
    p = pd.read_csv("pitchers.csv", index_col="pitcher")
    h = pd.read_csv("hitters.csv", index_col="batter")
    
    pLL = p[p['p_throws'] == 'L']['woba_L']
    pLR = p[p['p_throws'] == 'L']['woba_R']
    pRL = p[p['p_throws'] == 'R']['woba_L']
    pRR = p[p['p_throws'] == 'R']['woba_R']
    
    hLL = h[h['stand'] == 'L']['woba_L']
    hLR = h[h['stand'] == 'L']['woba_R']
    hRL = h[h['stand'] == 'R']['woba_L']
    hRR = h[h['stand'] == 'R']['woba_R']
    
    LL = pd.concat([pLL, hLL])
    LR = pd.concat([pLR, hRL])
    RL = pd.concat([pRL, hLR])
    RR = pd.concat([pRR, hRR])
    
    matchups = {'matchup': ['LL', 'LR', 'RL', 'RR'],
                'odds': []
                }
    matchups['odds'].append(LL.mean() / (1 - LL.mean()))
    matchups['odds'].append(LR.mean() / (1 - LR.mean()))
    matchups['odds'].append(RL.mean() / (1 - RL.mean()))
    matchups['odds'].append(RR.mean() / (1 - RR.mean()))
    df = pd.DataFrame(matchups, columns=matchups.keys())
    return df.to_csv('matchups.csv', index=False)

def getParks():
    df = pd.read_csv('parks.csv', index_col='park')
    al_over = MinMaxScaler(feature_range=(0.73, 1.23))
    al_under = MinMaxScaler(feature_range=(1.16, 1.75))
    nl_over = MinMaxScaler(feature_range=(0.91, 1.55))
    nl_under = MinMaxScaler(feature_range=(1.10, 1.62))
    al = df[df['lg'] == 'al']
    nl = df[df['lg'] == 'nl']
    al['over_threshold'] = al_over.fit_transform(al['runs'].to_numpy().reshape(-1,1))
    al['under_threshold'] = 1 - ((al['runs'] - al['runs'].min())/ (al['runs'].max() - al['runs'].min()))
    al['under_threshold'] = al_under.fit_transform(al['under_threshold'].to_numpy().reshape(-1,1))
    nl['over_threshold'] = nl_over.fit_transform(nl['runs'].to_numpy().reshape(-1,1))
    nl['under_threshold'] = 1 - ((nl['runs'] - nl['runs'].min())/ (nl['runs'].max() - nl['runs'].min()))
    nl['under_threshold'] = nl_under.fit_transform(nl['under_threshold'].to_numpy().reshape(-1,1))
    df = pd.concat([al, nl])
    
    handicaps = MinMaxScaler(feature_range=(0.0, 0.21))
    df['handicap'] = handicaps.fit_transform(df['runs'].to_numpy().reshape(-1,1)).round(2)
    return df.to_csv('parks.csv')


# getUmps()
# getBets()
# getFielding()
# getBullpens()
# getPitching()
# getHitters()
# getMatchups()
getParks()
