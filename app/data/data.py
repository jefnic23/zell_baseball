import pandas as pd
import numpy as np
import glob
from sklearn.preprocessing import MinMaxScaler
from collections import Counter


def getUmps():
    umps = pd.read_csv("D:/Documents/Pitcher List/statcast_data/umpires_ids_game_pk.csv")
    umps['game_date'] = umps['game_date'].str.split('-').str[0]
    umps = umps[(umps['position'] == 'HP') & (umps['id'].isin(umps[umps['game_date'] == '2021']['id']))]
    ump_count = umps.groupby('id')['game_pk'].count()
    df = pd.concat([pd.read_csv(f, engine='python') for f in glob.glob('D:/Documents/Pitcher List/statcast_data/savant_20*.csv')])
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
    for x in range(1, 501, 1):
        d['total'].append(x/100)
    scaler = MinMaxScaler(feature_range=(230, 1230))
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
    df = pd.read_csv('D:/Documents/Pitcher List/statcast_data/savant_2021.csv')
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
    df['hev'] = round(df['launch_speed'] * np.cos(np.radians(df['launch_angle']-25)))
    df['hev'] = np.where(df['description'] == 'foul', np.nan, df['hev'])
    df['hev'] = np.where((df['description'] == 'swinging_strike') & (df['events'] == 'strikeout'), 0.0, df['hev'])
    df['outs'] = np.where(df['events'].isin(out_1), 1, 0)
    df['outs'] = np.where(df['events'].isin(out_2), 2, df['outs'])
    df['outs'] = np.where(df['events'].isin(out_3), 3, df['outs'])
    
    d = {'pitcher': [],
         'p_throws': [],
         'tbf': [],
         'hev_R': [],
         'ab_R': [],
         'hev_L': [],
         'ab_L': [],
         'wHEV': []
         }
    
    for player in df['pitcher'].unique():
        try:
            df_new = df[df['pitcher'] == player].dropna(subset=['hev'])
            stand = df_new['p_throws'].unique()
            df_R = df_new[df_new['stand'] == 'R']
            df_L = df_new[df_new['stand'] == 'L']
            hev_R = round(df_R['hev'].mean()/100,3)
            hev_L = round(df_L['hev'].mean()/100,3)
            ab_R = len(df_R.index)
            ab_L = len(df_L.index)
            wHEV = round((hev_R * ab_R + hev_L * ab_L)/(ab_R + ab_L), 3)
            
            group = df[df['pitcher'] == player].groupby(['game_pk']).agg({'at_bat_number': 'unique'})
            tbf = []
            for i in group['at_bat_number']:
                tbf.append(len(i))
            tbf = Counter(tbf)
            d['tbf'].append(round(np.average(list(tbf.keys()), weights=list(tbf.values()))))
            
            d['pitcher'].append(player)
            d['p_throws'].append(stand[0])
            d['hev_R'].append(hev_R)
            d['hev_L'].append(hev_L)
            d['ab_R'].append(ab_R)
            d['ab_L'].append(ab_L)
            d['wHEV'].append(wHEV)
        except:
            pass
    df1 = pd.DataFrame(d, columns=list(d.keys()))
    
    df2 = df.groupby(['pitcher', 'game_pk']).agg({'outs': 'sum'})
    df2['innings'] = round(df2['outs'] / 3, 2)
    df2 = df2.groupby('pitcher').agg({'innings': 'mean'})
    df = pd.merge(df1, df2, on='pitcher')
    return df.to_csv('pitchers.csv', index=False)


def getHitters():
    df = pd.read_csv('D:/Documents/Pitcher List/statcast_data/savant_2021.csv')
    df['hev'] = round(df['launch_speed'] * np.cos(np.radians(df['launch_angle']-25)))
    df['hev'] = np.where(df['description'] == 'foul', np.nan, df['hev'])
    df = df.dropna(subset=['hev'])
    
    d = {'batter': [],
         'stand': [],
         'hev_R': [],
         'ab_R': [],
         'hev_L': [],
         'ab_L': []
         }
    
    for player in df['batter'].unique():
        try:
            df_new = df[df['batter'] == player]
            stand = df_new['stand'].unique()
            df_R = df_new[df_new['p_throws'] == 'R']
            df_L = df_new[df_new['p_throws'] == 'L']
            ab_R = len(df_R.index)
            ab_L = len(df_L.index)
            d['batter'].append(player)
            if len(stand) > 1:
                d['stand'].append('S')
            else:
                d['stand'].append(stand[0])
            d['hev_R'].append(round(df_R['hev'].mean()/100,3))
            d['ab_R'].append(ab_R)
            d['hev_L'].append(round(df_L['hev'].mean()/100,3))
            d['ab_L'].append(ab_L)
        except:
            pass
    
    df = pd.DataFrame(d, columns=list(d.keys()))
    return df.to_csv('batters.csv', index=False)


def getMatchups():
    p = pd.read_csv("pitchers.csv", index_col="pitcher")
    h = pd.read_csv("batters.csv", index_col="batter")
    
    pLL = p[p['p_throws'] == 'L']['hev_L']
    pLR = p[p['p_throws'] == 'L']['hev_R']
    pRL = p[p['p_throws'] == 'R']['hev_L']
    pRR = p[p['p_throws'] == 'R']['hev_R']
    
    hLL = h[h['stand'] == 'L']['hev_L']
    hLR = h[h['stand'] == 'L']['hev_R']
    hRL = h[h['stand'] == 'R']['hev_L']
    hRR = h[h['stand'] == 'R']['hev_R']
    
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

def getHEV():
    d = {'hev': [],
         'runs': []
         }
    
    for i in range(657, 825):
        hev = i / 1000
        d['hev'].append(hev)
    
    scaler = MinMaxScaler(feature_range=(-0.15, 0.15))
    runs = scaler.fit_transform(pd.Series(d['hev']).to_numpy().reshape(-1,1))
    for i, n in enumerate(d['hev']):
        d['runs'].append(runs[i][0])
    
    df = pd.DataFrame(d, columns=d.keys())
    return df.to_csv('hev.csv', index=False)

# getUmps()
# getBets()
# getFielding()
# getBullpens()
# getPitching()
# getHitters()
# getMatchups()
# getParks()
# getHEV()
