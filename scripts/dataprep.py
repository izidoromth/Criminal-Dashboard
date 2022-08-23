import pandas as pd
import json
import geopandas as gpd
import numpy as np

df_gmc = pd.read_csv('./data/gmc/sigesguarda.csv', delimiter=';', encoding='ISO-8859-1')

def prepare_district_names(district):
  if('CIC' in district or 'CIDADE INDUSTRIAL' in district):
    return 'CIDADE INDUSTRIAL DE CURITIBA'
  elif('BOQUEIRÃO ' in district):
    return 'BOQUEIRÃO' 
  elif(' JARDIM OSASCO' in district):
    return 'JARDIM OSASCO'
  elif('AFONSO PENA ' in district):
    return 'AFONSO PENA'
  else:
    return district

df_gmc.drop(df_gmc.index[[0]], inplace=True)
df_gmc = df_gmc[~df_gmc['ATENDIMENTO_ANO'].isnull()]
df_gmc = df_gmc[~df_gmc['LOGRADOURO_NOME'].isnull()]
df_gmc = df_gmc[~df_gmc['ATENDIMENTO_BAIRRO_NOME'].isnull()]
df_gmc['ATENDIMENTO_ANO'] = df_gmc['ATENDIMENTO_ANO'].astype(int)
df_gmc['ATENDIMENTO_BAIRRO_NOME'] = df_gmc['ATENDIMENTO_BAIRRO_NOME'].apply(prepare_district_names)
df_gmc['ATENDIMENTO_BAIRRO_NOME'] = df_gmc['ATENDIMENTO_BAIRRO_NOME'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

df_gmc['OCORRENCIA_DATA_SEM_HORARIO'] = pd.to_datetime(df_gmc['OCORRENCIA_DATA'], format='%Y-%m-%d %H:%M:%S.%f').dt.date

feriados_nacionais = pd.read_excel('./data/feriados_nacionais.xls')

feriados_nacionais.drop(np.arange(936,945),inplace=True)
feriados_nacionais['OCORRENCIA_DATA_SEM_HORARIO'] = pd.to_datetime(feriados_nacionais['Data'], format='%Y-%m-%d %H:%M:%S', errors='ignore').dt.date
feriados_nacionais.drop(columns=['Data'],inplace=True)

df_gmc = df_gmc.merge(feriados_nacionais, on='OCORRENCIA_DATA_SEM_HORARIO', how='left')
df_gmc['FERIADO'] = df_gmc['Feriado'].apply(lambda x: 1 if not pd.isna(x) else 0)
df_gmc.drop(columns=['Dia da Semana','Feriado'], inplace=True)

df_gmc.to_csv('./data/gmc/sigesguarda_cleaned.csv', index=False)

f = open('./data/DIVISA_DE_BAIRROS.geojson',)

bairros_geojson = json.load(f)

f.close()

geojsondf = gpd.GeoDataFrame.from_features(bairros_geojson["features"])

# ï¿½
def district_name_convert(nome):
  if(nome == '�GUA VERDE'):
    return 'AGUA VERDE'
  elif(nome == '�GUA VERDE'):
    return 'AGUA VERDE'
  elif(nome == 'JARDIM DAS AM�RICAS'):
    return 'JARDIM DAS AMERICAS'
  elif(nome == 'GUA�RA'):
    return 'GUAIRA'
  elif(nome == 'S�O FRANCISCO'):
    return 'SAO FRANCISCO'
  elif(nome == 'ALTO DA GL�RIA'):
    return 'ALTO DA GLORIA'
  elif(nome == 'LIND�IA'):
    return 'LINDOIA'
  elif(nome == 'CENTRO C�VICO'):
    return 'CENTRO CIVICO'
  elif(nome == 'JUVEV�'):
    return 'JUVEVE'
  elif(nome == 'CAP�O DA IMBUIA'):
    return 'CAPAO DA IMBUIA'
  elif(nome == 'SEMIN�RIO'):
    return 'SEMINARIO'
  elif(nome == 'PORT�O'):
    return 'PORTAO'
  elif(nome == 'AH�'):
    return 'AHU'
  elif(nome == 'REBOU�AS'):
    return 'REBOUCAS'
  elif(nome == 'MOSSUNGU�'):
    return 'MOSSUNGUE'
  elif(nome == 'JARDIM BOT�NICO'):
    return 'JARDIM BOTANICO'
  elif(nome == 'BOQUEIR�O'):
    return 'BOQUEIRAO'
  elif(nome == 'S�TIO CERCADO'):
    return 'SITIO CERCADO'
  elif(nome == 'TARUM�'):
    return 'TARUMA'
  elif(nome == 'S�O LOUREN�O'):
    return 'SAO LOURENCO'
  elif(nome == 'CAP�O RASO'):
    return 'CAPAO RASO'
  elif(nome == 'SANTA QUIT�RIA'):
    return 'SANTA QUITERIA'
  elif(nome == 'S�O MIGUEL'):
    return 'SAO MIGUEL'
  elif(nome == 'ALTO BOQUEIR�O'):
    return 'ALTO BOQUEIRAO'
  elif(nome == 'UMBAR�'):
    return 'UMBARA'
  elif(nome == 'TABO�O'):
    return 'TABOAO'
  elif(nome == 'SANTA C�NDIDA'):
    return 'SANTA CANDIDA'
  elif(nome == 'MERC�S'):
    return 'MERCES'
  elif(nome == 'SANTO IN�CIO'):
    return 'SANTO INACIO'
  elif(nome == 'S�O BRAZ'):
    return 'SAO BRAZ'
  elif(nome == 'S�O JO�O'):
    return 'SAO JOAO'
  else:
    return nome

geojsondf['NOME'] = geojsondf['NOME'].apply(district_name_convert)

geojsondf.to_file('./data/divisa_bairros_cleaned.geojson', driver="GeoJSON")