
from time import time
import pandas as pd
from datetime import datetime
import datetime as dt
import geopandas as gpd
import json

aux_df = pd.read_csv('./data/gmc/sigesguarda_cleaned.csv', dtype='unicode')
aux_df['OCORRENCIA_DATA_SEM_HORARIO'] = pd.to_datetime(aux_df['OCORRENCIA_DATA'], format='%Y-%m-%d %H:%M:%S.%f').dt.date
        
class GmcDatasource:

    _instance = None

    def __init__(self):
        aux_dem = pd.read_csv('./data/renda.csv')
        aux_dem = aux_dem[['Bairros','População Total']].set_index('Bairros')

        self.df = aux_df
        self.ocorrencias_bairro_mes = pd.read_csv('./data/gmc/ocorrencias_bairro_mes.csv')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def filter_by_end_date(self, end_date):
        if end_date == None:
            end_date = aux_df['OCORRENCIA_DATA_SEM_HORARIO'].max()
        else:
            end_date = datetime.strptime(end_date,'%Y-%m-%d').date()
            
        self.df = aux_df[aux_df['OCORRENCIA_DATA_SEM_HORARIO'] <= end_date]

    def getMinDate(self):
        return self.df['OCORRENCIA_DATA_SEM_HORARIO'].min()

    def getMaxDate(self,timefix=False):
        if timefix:
            return self.df['OCORRENCIA_DATA_SEM_HORARIO'].max() + dt.timedelta(days=1)
        else:
            return self.df['OCORRENCIA_DATA_SEM_HORARIO'].max()

    def getCrimesType(self):
        return self.df['NATUREZA1_DESCRICAO'].unique().tolist()