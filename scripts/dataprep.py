import pandas as pd
import json
import geopandas as gpd

df = pd.read_csv('./data/sigesguarda.csv', delimiter=';', encoding='ISO-8859-1')

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

df.drop(df.index[[0]], inplace=True)
df = df[~df['ATENDIMENTO_ANO'].isnull()]
df = df[~df['LOGRADOURO_NOME'].isnull()]
df = df[~df['ATENDIMENTO_BAIRRO_NOME'].isnull()]
df['ATENDIMENTO_ANO'] = df['ATENDIMENTO_ANO'].astype(int)
df['ATENDIMENTO_BAIRRO_NOME'] = df['ATENDIMENTO_BAIRRO_NOME'].apply(prepare_district_names)

df.to_csv('./data/sigesguarda_cleaned.csv', index=False)

f = open('./data/DIVISA_DE_BAIRROS.geojson',)

bairros_geojson = json.load(f)

f.close()

geojsondf = gpd.GeoDataFrame.from_features(bairros_geojson["features"])

def district_name_convert(nome):
  if(nome == 'ï¿½GUA VERDE'):
    return 'ÁGUA VERDE'
  elif(nome == 'JARDIM DAS AMï¿½RICAS'):
    return 'JARDIM DAS AMÉRICAS'
  elif(nome == 'GUAï¿½RA'):
    return 'GUAÍRA'
  elif(nome == 'Sï¿½O FRANCISCO'):
    return 'SÃO FRANCISCO'
  elif(nome == 'ALTO DA GLï¿½RIA'):
    return 'ALTO DA GLÓRIA'
  elif(nome == 'LINDï¿½IA'):
    return 'LINDÓIA'
  elif(nome == 'CENTRO Cï¿½VICO'):
    return 'CENTRO CÍVICO'
  elif(nome == 'JUVEVï¿½'):
    return 'JUVEVÊ'
  elif(nome == 'CAPï¿½O DA IMBUIA'):
    return 'CAPÃO DA IMBUIA'
  elif(nome == 'SEMINï¿½RIO'):
    return 'SEMINÁRIO'
  elif(nome == 'PORTï¿½O'):
    return 'PORTÃO'
  elif(nome == 'AHï¿½'):
    return 'AHÚ'
  elif(nome == 'REBOUï¿½AS'):
    return 'REBOUÇAS'
  elif(nome == 'MOSSUNGUï¿½'):
    return 'MOSSUNGUÊ'
  elif(nome == 'JARDIM BOTï¿½NICO'):
    return 'JARDIM BOTÂNICO'
  elif(nome == 'BOQUEIRï¿½O'):
    return 'BOQUEIRÃO'
  elif(nome == 'Sï¿½TIO CERCADO'):
    return 'SÍTIO CERCADO'
  elif(nome == 'TARUMï¿½'):
    return 'TARUMÃ'
  elif(nome == 'Sï¿½O LOURENï¿½O'):
    return 'SÃO LOURENÇO'
  elif(nome == 'CAPï¿½O RASO'):
    return 'CAPÃO RASO'
  elif(nome == 'SANTA QUITï¿½RIA'):
    return 'SANTA QUITÉRIA'
  elif(nome == 'Sï¿½O MIGUEL'):
    return 'SÃO MIGUEL'
  elif(nome == 'ALTO BOQUEIRï¿½O'):
    return 'ALTO BOQUEIRÃO'
  elif(nome == 'UMBARï¿½'):
    return 'UMBARÁ'
  elif(nome == 'TABOï¿½O'):
    return 'TABOÃO'
  elif(nome == 'SANTA Cï¿½NDIDA'):
    return 'SANTA CÂNDIDA'
  elif(nome == 'MERCï¿½S'):
    return 'MERCÊS'
  elif(nome == 'SANTO INï¿½CIO'):
    return 'SANTO INÁCIO'
  elif(nome == 'Sï¿½O BRAZ'):
    return 'SÃO BRAZ'
  elif(nome == 'Sï¿½O JOï¿½O'):
    return 'SÃO JOÃO'
  else:
    return nome

geojsondf['NOME'] = geojsondf['NOME'].apply(district_name_convert)

geojsondf.to_file('./data/divisa_bairros_cleaned.geojson', driver="GeoJSON")  