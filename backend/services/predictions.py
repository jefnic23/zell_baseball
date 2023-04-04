import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import Batter, Fielding, Matchup, Park, Pitcher, Ump, Woba
from backend.schemas.betting_data import Scores
from backend.schemas.game import Game


class Predictions:
    def __init__(
        self, 
        betting_data: Scores,
        game: Game,
        session: AsyncSession
    ):
        self.betting_data = betting_data
        self.game_data = game.gameData
        self.live_data = game.liveData
        self.session = session


    async def get_prediction_data(self) -> dict:
        '''Get all prediction data for a given game.'''
        
        home_team_query = (
            select(Park)
            .where(Park.park == self.game_data.teams.home.name)
        )
        away_team_query = (
            select(Park)
            .where(Park.park == self.game_data.teams.away.name)
        )
        home_pitcher_query = (
            select(Pitcher)
            .where(Pitcher.id == self.game_data.probablePitchers.home.id)
        )
        away_pitcher_query = (
            select(Pitcher)
            .where(Pitcher.id == self.game_data.probablePitchers.away.id)
        )
        home_bullpen_query = (
            select(Pitcher)
            .where(Pitcher.id.in_(
                [id for id in self.live_data.boxscore.teams.home.bullpen]
            ))
        )
        away_bullpen_query = (
            select(Pitcher)
            .where(Pitcher.id.in_(
                [id for id in self.live_data.boxscore.teams.away.bullpen]
            ))
        )
        home_lineup_query = (
            select(Batter)
            .where(Batter.id.in_(
                [id for id in self.live_data.boxscore.teams.home.battingOrder]
            ))
        )
        away_lineup_query = (
            select(Batter)
            .where(Batter.id.in_(
                [id for id in self.live_data.boxscore.teams.away.battingOrder]
            ))
        )

        home_team = await self.session.execute(home_team_query)
        away_team = await self.session.execute(away_team_query)
        home_pitcher = await self.session.execute(home_pitcher_query)
        away_pitcher = await self.session.execute(away_pitcher_query)
        home_bullpen = await self.session.execute(home_bullpen_query)
        away_bullpen = await self.session.execute(away_bullpen_query) 
        home_lineup = await self.session.execute(home_lineup_query)
        away_lineup = await self.session.execute(away_lineup_query)

        return {
            'home_team': home_team.scalar(),
            'away_team': away_team.scalar(),
            'home_pitcher': home_pitcher.scalar(),
            'away_pitcher': away_pitcher.scalar(),
            'home_bullpen': home_bullpen.scalars().all(),
            'away_bullpen': away_bullpen.scalars().all(),
            'home_lineup': home_lineup.scalars().all(),
            'away_lineup': away_lineup.scalars().all()
        }


    def get_bullpen(
        self, 
        bullpen: list[Pitcher], 
        lineup: list[Batter]
    ) -> float:
        '''Query Bullpen table by player id and return team bullpen run value.'''
        bullpen_woba = [player.woba for player in bullpen]
        offense_woba = [player.woba for player in lineup]
        return self.odds_ratio(
            (sum(offense_woba) / len(offense_woba)), 
            (sum(bullpen_woba) / len(bullpen_woba)), 
            'league'
        )


    async def get_fielding(
        self, 
        lineup: list[int], 
        innings: int
    ) -> float:
        '''Query Fielding table by player id and return team defense run value.'''
        runs = 0
        fielders = await self.session.execute(
            select(Fielding)
            .where(Fielding.id.in_([id for id in lineup]))
        )
        for player in fielders.all():
            try:
                runs += player.runs
            except:  # noqa: E722
                runs += 0
        return round(runs * (innings/9), 2)


    async def get_ump(
        self,
        id: int, 
        innings: int
    ) -> float:
        '''Query Ump table by ump id and return run value.'''
        try:
            ump = await self.session.execute(select(Ump).where(Ump.id == id))
            runs = ump.one().runs
        except:  # noqa: E722
            runs = 0
        return round(runs * (innings/9), 2)


    async def odds_ratio(
        self, 
        hitter: float, 
        pitcher: float,
        matchup: int
    ) -> float:
        '''
        Calculate odds ratio of a batter/pitcher matchup.
        Query Matchups table by odds ratio and return run value.
        '''
        query = await self.session.execute(
            select(Matchup)
            .where(Matchup.id == matchup)
        )
        league = query.one().odds
        odds = round(hitter * pitcher / league, 3)
        if odds < 0.269:
            return -0.1
        elif 0.269 <= odds <= 0.399:
            woba = await self.session.execute(
                select(Woba)
                .where(Woba.odds == odds)
            )
            return woba.one().runs
        else:
            return 0.1


    def pvb(
        self, 
        pitcher: Pitcher, 
        lineup: list[Batter]
    ) -> float:
        '''Queries Pitchers and Batters tables by player id and returns run value.'''
        handedness_dict = {
            ('S', 'R'): ('hitter.woba_l', 'pitcher.woba_r', 'LR'),
            ('S', 'L'): ('hitter.woba_r', 'pitcher.woba_l', 'RL'),
            ('L', 'L'): ('hitter.woba_l', 'pitcher.woba_l', 'LL'),
            ('R', 'R'): ('hitter.woba_r', 'pitcher.woba_r', 'RR')
        }
        runs = sum(
            self.oddsRatio(eval(hitter_woba), eval(pitcher_woba), matchup_id)
            for hitter in lineup
            for (hitter_stance, pitcher_throws), (hitter_woba, pitcher_woba, matchup_id)
            in handedness_dict.items()
            if hitter.stand == hitter_stance and pitcher.p_throws == pitcher_throws
        )
        return round(runs, 2) 


    @staticmethod
    def get_handicap(
        home_team: Park, 
        away_team: Park, 
        innings: int
    ) -> float:
        '''Returns difference between home and away team handicaps'''
        return round((home_team.handicap - away_team.handicap) * (innings/9), 2)
    

    @staticmethod
    def get_innings(
        pitcher: Pitcher, 
        pvb: float, 
        bullpen: float, 
        scheduled: int, 
        pvb_modifier: float
    ) -> float: 
        '''
        Query Pitchers table by starting pitcher id and 
        return average innings pitched per start. On error
        a default value is returned.
        '''
        try:
            innings_per_start = pitcher.ip / scheduled
        except (AttributeError, TypeError, ZeroDivisionError):
            innings_per_start = 4.8 / scheduled
        innings_weighted = (
            (pvb * innings_per_start) + 
            (bullpen * (1 - innings_per_start))
        )
        return round(innings_weighted * pvb_modifier, 2)


    @staticmethod
    def get_temp(
        temp: int, 
        innings: int
    ) -> float:
        '''Get run value based on game time temperature.'''
        temp_ranges = {
            range(0, 47): -0.225, 
            range(47, 54): -0.15, 
            range(54, 63): -0.075, 
            range(63, 72): 0.0,
            range(72, 80): 0.1, 
            range(80, 88): 0.2
        }
        for temp_range, run_value in temp_ranges.items():
            if temp in temp_range:
                return round(run_value * (innings/9), 2)
        return round(0.3 * (innings/9), 2)


    @staticmethod
    def get_wind(
        venue: str, 
        wind_data: str, 
        innings: int
    ) -> float:
        '''
        Get run value based on game time wind speed and direction.
        Only applies to Wrigley Field.
        '''
        speed, direction = wind_data.split(' mph, ')
        wind = 0
        if venue == "Chicago Cubs" and int(speed) >= 10:
            wind_values = {"In": -0.15, "Out": 0.15}
            wind = wind_values.get(direction, 0)
            wind *= max(int(speed) - 9, 0)
        return round(wind * (innings/9), 2)
