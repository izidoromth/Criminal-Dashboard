
from time import time
import pandas as pd
from datetime import datetime
import datetime as dt
import geopandas as gpd
import json

aux_df = pd.read_csv('./data/pcpr/crimes2016-2020.csv')
aux_df['data_fato'] = pd.to_datetime(aux_df['data_fato'], format='%Y-%m-%d').dt.date

class PcprDatasource:

    _instance = None

    def __init__(self):
        # aux_dem = pd.read_csv('./data/renda.csv')
        # aux_dem = aux_dem[['Bairros','População Total']].set_index('Bairros')

        # f = open('./data/divisa_bairros_cleaned.geojson', encoding='utf-8')

        self.df = aux_df
        self.df['PANDEMIA'] = self.df['data_fato'].apply(lambda x: 1*(x >= datetime.strptime('11/04/2020','%d/%m/%Y').date()))

        # self.ocorrencias_bairro_mes = pd.read_csv('./data/gmc/ocorrencias_bairro_mes.csv')
        # self.dem = aux_dem
        # self.bairros = gpd.read_file('./data/divisa_bairros_cleaned.geojson').set_index('NOME')
        # self.bairros_geojson = json.load(f)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def filter_by_end_date(self, end_date):
        if end_date == None:
            end_date = aux_df['data_fato'].max()
        else:
            end_date = datetime.strptime(end_date,'%Y-%m-%d').date()
            
        self.df = aux_df[aux_df['data_fato'] <= end_date]

    def getMinDate(self):
        return self.df['data_fato'].min()

    def getMaxDate(self,timefix=False):
        if timefix:
            return self.df['data_fato'].max() + dt.timedelta(days=1)
        else:
            return self.df['data_fato'].max()

    def getCrimesType(self):
        return self.df['tipo'].unique().tolist()