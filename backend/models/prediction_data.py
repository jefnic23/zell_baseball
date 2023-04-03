from backend.models.betting_data import Scores
from backend.models.mlb.game import Game


class PredictionData:
    def __init__(
        self, 
        betting_data: Scores,
        game: Game
    ):
        self.betting_data = betting_data
        self.game_data = game.gameData
        self.live_data = game.liveData
        

    def getTemp(temp, innings):
        '''Get run value based on game time temperature.'''
        if temp <= 46:
            return round(-0.225 * (innings/9), 2)
        elif 47 <= temp <= 53:
            return round(-0.15 * (innings/9), 2)
        elif 54 <= temp <= 62:
            return round(-0.075 * (innings/9), 2)
        elif 63 <= temp <= 71:
            return 0.0
        elif 72 <= temp <= 79:
            return round(0.1 * (innings/9), 2)
        elif 80 <= temp <= 87:
            return round(0.2 * (innings/9), 2)
        else:
            return round(0.3 * (innings/9), 2)


    def getWind(venue, wind_data, innings):
        '''
        Get run value based on game time wind speed and direction.
        Only applies to Wrigley Field.
        '''
        speed = int(wind_data[0])
        direction = wind_data[1]
        wind = 0
        if venue == "Chicago Cubs" and speed >= 10 and direction == "In":
            for _ in range(0, speed - 10 + 1):
                wind -= 0.15
        if venue == "Chicago Cubs" and speed >= 10 and direction == "Out":
            for _ in range(0, speed - 10 + 1):
                wind += 0.15
        return round(wind * (innings/9), 2)


    def getUmp(ump, innings):
        '''Query Ump table by ump id and return run value.'''
        try:
            runs = Umps.query.filter_by(id=ump).first().runs
        except:
            runs = 0
        return round(runs * (innings/9), 2)


    def getFielding(lineup, innings):
        '''Query Fielding table by player id and return team defense run value.'''
        runs = 0
        fielders = Fielding.query.filter(Fielding.id.in_([id for id in lineup])).all()
        for player in fielders:
            try:
                runs += player.runs
            except:
                runs += 0
        return round(runs * (innings/9), 2)


    def getBullpen(bullpen, lineup):
        '''Query Bullpen table by player id and return team bullpen run value.'''
        bullpen_woba = [player.woba for player in bullpen]
        offense_woba = [player.woba for player in lineup]
        return oddsRatio((sum(offense_woba) / len(offense_woba)), (sum(bullpen_woba) / len(bullpen_woba)), 'league')


    def oddsRatio(hitter, pitcher, matchup):
        '''
        Calculate odds ratio of a batter/pitcher matchup.
        Query Matchups table by odds ratio and return run value.
        '''
        league = Matchups.query.get(matchup).odds
        odds = round(hitter * pitcher / league, 3)
        if 0.269 <= odds <= 0.399:
            return Woba.query.get(odds).runs
        elif odds < 0.269:
            return -0.1
        else:
            return 0.1


    def getInnings(pitcher, pvb, bullpen, scheduled, pvb_modifier): 
        '''
        Query Pitchers table by starting pitcher id and 
        return average innings pitched per start. On error
        a default value is returned.
        '''
        try:
            innings = pitcher.ip / scheduled
            return round(((pvb * innings) + (bullpen * (1 - innings))) * pvb_modifier, 2)
        except:
            # ip/gs
            innings = 4.8 / scheduled
            return round(((pvb * innings) + (bullpen * (1 - innings))) * pvb_modifier, 2)


    def PvB(pitcher, lineup):
        '''Queries Pitchers and Batters tables by player id and returns run value.'''
        runs = 0
        for hitter in lineup:
            try:
                if hitter.stand == "S" or hitter.stand == "L" and pitcher.p_throws == "R":
                    runs += oddsRatio(hitter.woba_r, pitcher.woba_l, 'RL')
                if hitter.stand == "S" or hitter.stand == "R" and pitcher.p_throws == "L":
                    runs += oddsRatio(hitter.woba_l, pitcher.woba_r, 'LR')
                if hitter.stand == "L" and pitcher.p_throws == "L":
                    runs += oddsRatio(hitter.woba_l, pitcher.woba_l, 'LL')
                if hitter.stand == "R" and pitcher.p_throws == "R":
                    runs += oddsRatio(hitter.woba_r, pitcher.woba_r, 'RR')
            except:
                runs += 0
        return round(runs, 2)


    def getHandicap(home_team, away_team, innings):
        '''Returns difference between home and away team handicaps'''
        return round((home_team.handicap - away_team.handicap) * (innings/9), 2)
