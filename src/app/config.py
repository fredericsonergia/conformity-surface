from pydantic import BaseSettings
import configparser
import pickle
from sklearn.tree import DecisionTreeRegressor


class Settings(BaseSettings):
    w: int = 800
    h: int = 400
    r: float = 6
    R: float = 100
    data_path: str = "../data/"
    static_path:str = "../static/"
    loaded_model: DecisionTreeRegressor = None
    

