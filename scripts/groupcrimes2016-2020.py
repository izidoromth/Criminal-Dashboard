import pandas as pd

# Estelionato
df_fraud  = pd.read_csv('./data/pcpr/estelionato/estelionato_2016_2020_bairros.csv')
df_fraud['data_fato'] = pd.to_datetime(df_fraud['data_fato'])

few_occurr_dists = df_fraud['descBairro'].value_counts()
few_occurr_dists = few_occurr_dists[few_occurr_dists > 30]

df_fraud = df_fraud[df_fraud['descBairro'].isin(few_occurr_dists.index)]
df_fraud = df_fraud[~df_fraud['descBairro'].str.contains('PREJ')]
df_fraud = df_fraud[~df_fraud['descBairro'].str.contains('INFORMADO')]

df_fraud['month_year'] = df_fraud['data_fato'].dt.to_period('M').astype(str)

df_fraud = df_fraud.groupby(by=['descBairro', 'month_year']).sum().reset_index()



# Furto e roubo
df_robbery  = pd.read_csv('./data/pcpr/furto_e_roubo/furto_roubo_2016_2020_bairros.csv')
df_robbery['data_fato'] = pd.to_datetime(df_robbery['data_fato'])

few_occurr_dists = df_robbery['descBairro'].value_counts()
few_occurr_dists = few_occurr_dists[few_occurr_dists > 30]

df_robbery = df_robbery[df_robbery['descBairro'].isin(few_occurr_dists.index)]
df_robbery = df_robbery[~df_robbery['descBairro'].str.contains('PREJ')]
df_robbery = df_robbery[~df_robbery['descBairro'].str.contains('INFORMADO')]

df_robbery['month_year'] = df_robbery['data_fato'].dt.to_period('M').astype(str)

df_robbery = df_robbery.groupby(by=['descBairro', 'month_year']).sum().reset_index()



# Tráfico de Drogas

df_drug  = pd.read_csv('./data/pcpr/trafico_drogas/drogas_2016_2020_bairros.csv')
df_drug['data_fato'] = pd.to_datetime(df_drug['data_fato'])

few_occurr_dists = df_drug['descBairro'].value_counts()
few_occurr_dists = few_occurr_dists[few_occurr_dists > 30]

df_drug = df_drug[df_drug['descBairro'].isin(few_occurr_dists.index)]
df_drug = df_drug[~df_drug['descBairro'].str.contains('PREJ')]
df_drug = df_drug[~df_drug['descBairro'].str.contains('INFORMADO')]

df_drug['month_year'] = df_drug['data_fato'].dt.to_period('M').astype(str)

df_drug = df_drug.groupby(by=['descBairro', 'month_year']).sum().reset_index()



# Violência doméstica

df_dome_viol  = pd.read_csv('./data/pcpr/violencia_domestica/violencia_domestica_2016_2020_bairros.csv')
df_dome_viol['data_fato'] = pd.to_datetime(df_dome_viol['data_fato'])

few_occurr_dists = df_dome_viol['descBairro'].value_counts()
few_occurr_dists = few_occurr_dists[few_occurr_dists > 30]

df_dome_viol = df_dome_viol[df_dome_viol['descBairro'].isin(few_occurr_dists.index)]
df_dome_viol = df_dome_viol[~df_dome_viol['descBairro'].str.contains('PREJ')]
df_dome_viol = df_dome_viol[~df_dome_viol['descBairro'].str.contains('INFORMADO')]

df_dome_viol['month_year'] = df_dome_viol['data_fato'].dt.to_period('M').astype(str)

df_dome_viol = df_dome_viol.groupby(by=['descBairro', 'month_year']).sum().reset_index()



# Agrupamento dos dataframes

df_fraud = df_fraud.assign(tipo='Estelionato')
df_robbery = df_robbery.assign(tipo='Furto/Roubo')
df_drug = df_drug.assign(tipo='Tráfico de drogas')
df_dome_viol = df_dome_viol.assign(tipo='Violência Doméstica')

df_all_crimes = pd.concat([df_fraud, df_robbery, df_drug, df_dome_viol], ignore_index=True)

df_all_crimes.sort_values(by='month_year', inplace=True)

df_all_crimes.to_csv('./data/pcpr/crimes2016-2020.csv', index=False)