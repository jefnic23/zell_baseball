from pydantic import BaseModel


class PredictionData(BaseModel):
    away_bullpen_factor: float
    away_fielding_factor: float
    away_matchups: float
    away_offense_factor: float
    home_bullpen_factor: float
    home_fielding_factor: float
    home_matchups: float
    home_offense_factor: float
    park_factor: float
    temp_factor: float
    ump_factor: float
    wind_factor: float