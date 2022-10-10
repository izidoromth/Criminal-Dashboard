import pandas as pd

# Estelionato
df_fraud  = pd.read_csv('./data/pcpr/estelionato/estelionato_2016_2020_bairros.csv')
df_fraud['data_fato'] = pd.to_datetime(df_fraud['data_fato'])
# df_fraud = df_fraud[~df_fraud['descBairro'].str.contains('PREJ')]
# df_fraud = df_fraud[~df_fraud['descBairro'].str.contains('INFORMADO')]

# df_fraud['month_year'] = df_fraud['data_fato'].dt.to_period('M').astype(str)

df_fraud = df_fraud.groupby(by=['data_fato']).sum().reset_index()

# Furto e roubo
df_robbery  = pd.read_csv('./data/pcpr/furto_e_roubo/furto_roubo_2016_2020_bairros.csv')
df_robbery['data_fato'] = pd.to_datetime(df_robbery['data_fato'])
# df_robbery = df_robbery[~df_robbery['descBairro'].str.contains('PREJ',na=False)]
# df_robbery = df_robbery[~df_robbery['descBairro'].str.contains('INFORMADO',na=False)]

# df_robbery['month_year'] = df_robbery['data_fato'].dt.to_period('M').astype(str)

df_robbery = df_robbery.groupby(by=['data_fato']).sum().reset_index()



# Tráfico de Drogas

df_drug  = pd.read_csv('./data/pcpr/trafico_drogas/drogas_2016_2020_bairros.csv')
df_drug['data_fato'] = pd.to_datetime(df_drug['data_fato'])
# df_drug = df_drug[~df_drug['descBairro'].str.contains('PREJ',na=False)]
# df_drug = df_drug[~df_drug['descBairro'].str.contains('INFORMADO',na=False)]

# df_drug['month_year'] = df_drug['data_fato'].dt.to_period('M').astype(str)

df_drug = df_drug.groupby(by=['data_fato']).sum().reset_index()



# Violência doméstica

df_dome_viol  = pd.read_csv('./data/pcpr/violencia_domestica/violencia_domestica_2016_2020_bairros.csv')
df_dome_viol['data_fato'] = pd.to_datetime(df_dome_viol['data_fato'])
# df_dome_viol = df_dome_viol[~df_dome_viol['descBairro'].str.contains('PREJ',na=False)]
# df_dome_viol = df_dome_viol[~df_dome_viol['descBairro'].str.contains('INFORMADO',na=False)]

# df_dome_viol['month_year'] = df_dome_viol['data_fato'].dt.to_period('M').astype(str)

df_dome_viol = df_dome_viol.groupby(by=['data_fato']).sum().reset_index()



# Agrupamento dos dataframes

df_fraud = df_fraud.assign(tipo='Estelionato')
df_robbery = df_robbery.assign(tipo='Furto/Roubo')
df_drug = df_drug.assign(tipo='Tráfico de drogas')
df_dome_viol = df_dome_viol.assign(tipo='Violência Doméstica')

df_all_crimes = pd.concat([df_fraud, df_robbery, df_drug, df_dome_viol], ignore_index=True)

df_all_crimes.sort_values(by='data_fato', inplace=True)

df_all_crimes.drop(columns=['horaFato'],inplace=True)

df_all_crimes.to_csv('./data/pcpr/crimes2016-2020.csv', index=False)