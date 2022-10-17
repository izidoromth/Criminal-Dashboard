
from time import time
import pandas as pd
from datetime import datetime
import datetime as dt
import geopandas as gpd
import json

class CommonDatasource:

    _instance = None

    def __init__(self):
        aux_dem = pd.read_csv('./data/renda.csv')
        aux_dem = aux_dem[['Bairros','População Total']].set_index('Bairros')

        f = open('./data/divisa_bairros_cleaned.geojson', encoding='utf-8')

        self.dem = aux_dem
        self.bairros = gpd.read_file('./data/divisa_bairros_cleaned.geojson').set_index('NOME')
        self.bairros_geojson = json.load(f)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance