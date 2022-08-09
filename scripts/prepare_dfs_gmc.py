import pandas as pd

df_gmc = pd.read_csv('./data/gmc/sigesguarda_cleaned.csv')
df_gmc['OCORRENCIA_DATA_SEM_HORARIO'] = pd.to_datetime(df_gmc['OCORRENCIA_DATA'], format='%Y-%m-%d %H:%M:%S.%f').dt.date

df_alltime = df_gmc.groupby(['OCORRENCIA_DATA_SEM_HORARIO']).size().reset_index(name='OCORRENCIAS_ATENDIDAS')

df_alltime.to_csv('./dashboard/datasources/df_alltime_allcrimes_series.csv')