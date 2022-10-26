from gc import callbacks
import dash
from dash import html, dcc, callback, Input, Output, State, ctx
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import Layout
from plotly.subplots import make_subplots
import pandas as pd
import geopandas as gpd
from pysal.explore import esda
from pysal.lib import weights
import statsmodels.formula.api as smf
from statsmodels.regression.linear_model import OLS
from datetime import datetime
from assets.styles import *
from datasources.gmc_datasource import GmcDatasource
from datasources.common_datasource import CommonDatasource
from assets.utils import to_month_year_str
import time
start_time = time.time()

gmc_datasource = GmcDatasource.instance()
common_datasource = CommonDatasource.instance()

dash.register_page(__name__, path='/gmc', title="Painel Criminal: GMC")

temporal_tab = html.Div(children=[
        dcc.Location(id='loc'),
		dcc.Graph(id="temporal_model"),
		html.Div([
				dcc.Graph(id="most_frequent_crimes"),
				html.Div(id="variance_label", style={'font-size':'25px', 'margin': '10px 30px'})
			],
			style={'display':'flex', 'flex-direction':'row', 'justify-content':'space-between'}
		)		
	],
)

spatial_tab = html.Div(children=[
		dcc.Graph(id="spatial_model_occurrences"),
		dcc.Graph(id="spatial_model_lag"),
		dcc.Graph(id="spatial_model_clusters"),
		dcc.Graph(id="spatial_model_significants"),
	],
	className="temporal-tab"
)

spatiotemporal_tab = html.Div(children=[
	dcc.Graph(id="spatiotemporal_map"),
	html.Div([
		dcc.Dropdown(id='spatiotemporal_select', placeholder="Selecione o mês da anomalia",style={'width':'250px'}),
		html.Div(id="spatiotemporal_variance", style={'font-size':'25px', 'margin': '10px 30px'})],
		style={'display':'flex', 'flex-direction':'column', 'justify-content':'space-between'})],
	style=spatio_temporal_class
)

layout = html.Div(
    [
		dcc.Tabs(
			[
				dcc.Tab(label="Análise Temporal", value="temporal-tab", selected_className="custom-tab--selected"),
				dcc.Tab(label="Análise Espacial", value="spatial-tab", selected_className="custom-tab--selected"),
				dcc.Tab(label="Análise Espaço-Temporal", value="spatiotemporal-tab", selected_className="custom-tab--selected"),
			],
			id="card-tabs",
			value="temporal-tab",
			persistence=True
        ),
        html.Div(id="card-content"),
    ],
	style={'margin-top':'40px','background-color': 'white'}
)

@callback(
	Output("card-content", "children"), 
	[Input("card-tabs", "value")]
)
def change_tab_content(active_tab):
	if active_tab == 'temporal-tab':
		return temporal_tab
	elif active_tab == 'spatial-tab':
		return spatial_tab
	elif active_tab == 'spatiotemporal-tab':
		return spatiotemporal_tab

@callback(
    Output("temporal_model", "figure"),
	Output("variance_label","children"),
	Input("sidebar-apply", "n_clicks"),
	Input("my-date-picker-single","value"),
	[State("date-range-filter","value"),	
	State("occurrence-type-select","value")]
)
def create_temporal_outlier_model_view(n_clicks, navbar_date, dates, type):
	if ctx.triggered[0]['prop_id'] == "my-date-picker-single.value":
		gmc_datasource.filter_by_end_date(navbar_date)

	initial_date = datetime.strptime(dates[0],'%Y-%m-%d').date() if dates != None and ctx.triggered[0]['prop_id'] == "sidebar-apply.n_clicks" else gmc_datasource.getMinDate()
	end_date = datetime.strptime(dates[1],'%Y-%m-%d').date() if dates != None and ctx.triggered[0]['prop_id'] == "sidebar-apply.n_clicks" else gmc_datasource.getMaxDate()

	df_gmc_ols_model = gmc_datasource.df[(gmc_datasource.df['OCORRENCIA_DATA_SEM_HORARIO'] >= initial_date) & (gmc_datasource.df['OCORRENCIA_DATA_SEM_HORARIO'] <= end_date)]
	df_gmc_ols_model = df_gmc_ols_model[df_gmc_ols_model['NATUREZA1_DESCRICAO'] == type] if type != None else df_gmc_ols_model
	df_gmc_ols_model = df_gmc_ols_model.groupby(['OCORRENCIA_DATA_SEM_HORARIO','FERIADO']).size().reset_index(name='OCORRENCIAS_ATENDIDAS')
	df_gmc_ols_model['x0_final_de_semana'] = df_gmc_ols_model['OCORRENCIA_DATA_SEM_HORARIO'].apply(lambda x: 1 if x.weekday() == 5 or x.weekday() == 6 else 0)
	df_gmc_ols_model['x1_time'] = np.arange(df_gmc_ols_model.shape[0])
	df_gmc_ols_model['x2_lag1'] = df_gmc_ols_model['OCORRENCIAS_ATENDIDAS'].shift(1).fillna(0)
	df_gmc_ols_model['x3_lag2'] = df_gmc_ols_model['OCORRENCIAS_ATENDIDAS'].shift(2).fillna(0)
	df_gmc_ols_model['x4_lag3'] = df_gmc_ols_model['OCORRENCIAS_ATENDIDAS'].shift(3).fillna(0)
	df_gmc_ols_model['x5_lag4'] = df_gmc_ols_model['OCORRENCIAS_ATENDIDAS'].shift(4).fillna(0)
	df_gmc_ols_model['x6_lag5'] = df_gmc_ols_model['OCORRENCIAS_ATENDIDAS'].shift(5).fillna(0)
	df_gmc_ols_model['x7_lag6'] = df_gmc_ols_model['OCORRENCIAS_ATENDIDAS'].shift(6).fillna(0)
	df_gmc_ols_model['x8_lag7'] = df_gmc_ols_model['OCORRENCIAS_ATENDIDAS'].shift(7).fillna(0)
	df_gmc_ols_model['x9_window_mean'] = df_gmc_ols_model['OCORRENCIAS_ATENDIDAS'].shift(1).rolling(window=7).mean().fillna(0)
	df_gmc_ols_model['x10_feriado'] = df_gmc_ols_model['FERIADO'].astype(int)
	df_gmc_ols_model['x11_pandemia'] = df_gmc_ols_model['OCORRENCIA_DATA_SEM_HORARIO'].apply(lambda x: 1 if x >= datetime.strptime('11/04/2020','%d/%m/%Y').date() else 0)
	df_gmc_ols_model['x12_dia_semana'] = df_gmc_ols_model['OCORRENCIA_DATA_SEM_HORARIO'].apply(lambda x: x.weekday())

	model_features = ['x0_final_de_semana','x1_time','x2_lag1','x3_lag2','x4_lag3','x5_lag4','x6_lag5','x7_lag6','x8_lag7','x10_feriado','x11_pandemia']
	X_model5, y_model5 = df_gmc_ols_model[model_features], df_gmc_ols_model['OCORRENCIAS_ATENDIDAS']

	model_results = OLS(y_model5, X_model5).fit()

	# print(model_results.summary())

	df_results = pd.DataFrame([df_gmc_ols_model['OCORRENCIAS_ATENDIDAS'], model_results.predict(df_gmc_ols_model[model_features])]).transpose().reset_index()
	df_results['Data'] = df_gmc_ols_model['OCORRENCIA_DATA_SEM_HORARIO']
	df_results.drop(columns=['index'],inplace=True)
	df_results.rename(columns={'Unnamed 0':'OCORRENCIAS_PREVISTAS'}, inplace=True)
	df_results['OCORRENCIAS_PREVISTAS'] = df_results['OCORRENCIAS_PREVISTAS'].astype(int)
	df_results['ERRO'] = df_results['OCORRENCIAS_PREVISTAS'] - df_results['OCORRENCIAS_ATENDIDAS']
	df_results['Z-SCORE'] = (df_results['ERRO'] - df_results['ERRO'].mean())/df_results['ERRO'].std()
	df_results['OUTLIER'] = df_results['Z-SCORE'].apply(lambda x: 1 if abs(x) >= 2.575 else 0)
	df_results.rename(columns={'OCORRENCIAS_ATENDIDAS': 'Atendidas','OCORRENCIAS_PREVISTAS':'Previstas'},inplace=True)

	fig1 = px.line(df_results, x='Data', y=['Atendidas','Previstas'])
	fig1.data[0].line.color = rgba(primary, .25)
	fig1.data[1].line.color = rgba(primary, .65)
	try:
		fig2 = px.scatter(df_results[df_results['OUTLIER'] == 1], x='Data', y='Atendidas', color_discrete_sequence=[secondary])
		fig2['data'][0]['showlegend'] = True
		fig2['data'][0]['name'] = 'Outlier'
	except:
		fig2 = px.scatter()

	fig = go.Figure(data=fig1.data + fig2.data, layout=Layout(plot_bgcolor=tertiary))
	fig.update_xaxes(
		rangeslider_visible=True,
		rangeselector=dict(
			buttons=list([
				dict(count=1, label="1m", step="month", stepmode="backward"),
				dict(count=6, label="6m", step="month", stepmode="backward"),
				dict(count=1, label="YTD", step="year", stepmode="todate"),
				dict(count=1, label="1y", step="year", stepmode="backward"),
				dict(step="all")
			])
		)
	)
	fig.update_yaxes(fixedrange=False)
	fig.update_layout(
		autosize=False,
		height=375,
		margin=dict(
			l=35,
			r=10,
			b=10,
			t=20,
			pad=0
		),
	)

	return fig, f'Variância total explicada pelo modelo: {str(round(model_results.rsquared,2)).split(".")[1]}%'

@callback(
    Output("most_frequent_crimes", "figure"),
	Input("sidebar-apply", "n_clicks"),
	Input("temporal_model","relayoutData"),
	State("date-range-filter","value"),
)
def create_frequent_crimes_view(n_clicks, relayoutData, dates):
	initial_date, end_date = None, None

	if relayoutData != None and 'xaxis.range' in relayoutData:
		initial_date = datetime.strptime(relayoutData['xaxis.range'][0][0:10],'%Y-%m-%d').date()
		end_date = datetime.strptime(relayoutData['xaxis.range'][1][0:10],'%Y-%m-%d').date()
	elif relayoutData != None and 'xaxis.range[0]' in relayoutData and 'xaxis.range[1]' in relayoutData:
		initial_date = datetime.strptime(relayoutData['xaxis.range[0]'][0:10],'%Y-%m-%d').date()
		end_date = datetime.strptime(relayoutData['xaxis.range[1]'][0:10],'%Y-%m-%d').date()
	else:
		initial_date = datetime.strptime(dates[0],'%Y-%m-%d').date() if dates != None else gmc_datasource.getMinDate()
		end_date = datetime.strptime(dates[1],'%Y-%m-%d').date() if dates != None else gmc_datasource.getMaxDate()

	dfg = gmc_datasource.df[
			(gmc_datasource.df['OCORRENCIA_DATA_SEM_HORARIO'] >= initial_date) & 
			(gmc_datasource.df['OCORRENCIA_DATA_SEM_HORARIO'] <= end_date)
		].groupby(['NATUREZA1_DESCRICAO']).size().to_frame().reset_index().rename(columns={'NATUREZA1_DESCRICAO':'Natureza', 0:'Ocorrências'}).sort_values(by="Ocorrências",ascending=False).head(10)
	fig = px.histogram(dfg, x='Natureza', y = 'Ocorrências',color_discrete_sequence=[rgba(primary, .85)])
	fig.update_layout({
		'width':450, 
		'height':450, 
		'plot_bgcolor': tertiary,
		'autosize': False,
		'margin': dict(
			l=35,
			r=10,
			b=10,
			t=20,
			pad=0
		),
		'legend': dict(font = dict(family = "Courier", size = 50, color = "white"))
	})

	return fig

@callback(
    [Output("spatial_model_occurrences", "figure"),
	Output("spatial_model_lag", "figure"),
	Output("spatial_model_clusters", "figure"),
	Output("spatial_model_significants", "figure")],
	Input("sidebar-apply", "n_clicks"),
	Input("my-date-picker-single","value"),
	[State("date-range-filter","value"),	
	State("occurrence-type-select","value")]
)
def create_spatial_outlier_model_view(n_clicks, navbar_date, dates, type):	
	if ctx.triggered[0]['prop_id'] == "my-date-picker-single.value":
		gmc_datasource.filter_by_end_date(navbar_date)

	initial_date = datetime.strptime(dates[0],'%Y-%m-%d').date() if dates != None and ctx.triggered[0]['prop_id'] == "sidebar-apply.n_clicks" else gmc_datasource.getMinDate()
	end_date = datetime.strptime(dates[1],'%Y-%m-%d').date() if dates != None and ctx.triggered[0]['prop_id'] == "sidebar-apply.n_clicks" else gmc_datasource.getMaxDate()

	gmc_ref = gmc_datasource.df[(gmc_datasource.df['OCORRENCIA_DATA_SEM_HORARIO'] >= initial_date) & (gmc_datasource.df['OCORRENCIA_DATA_SEM_HORARIO'] <= end_date)].groupby(['ATENDIMENTO_BAIRRO_NOME']).size().reset_index(name='OCORRENCIAS_ATENDIDAS').set_index('ATENDIMENTO_BAIRRO_NOME')
	gmc_ref = gmc_ref.join(common_datasource.dem)
	gmc_ref.dropna(inplace=True)
	gmc_ref['Ocorrências p.'] = gmc_ref['OCORRENCIAS_ATENDIDAS'] / gmc_ref['População Total']
	gmc_ref.drop(columns=['OCORRENCIAS_ATENDIDAS','População Total'], inplace=True)
	
	db = gpd.GeoDataFrame(common_datasource.bairros.join(gmc_ref[["Ocorrências p."]]), crs=common_datasource.bairros.crs).to_crs(epsg=3857)[["Ocorrências p.", "geometry"]].dropna()

	w = weights.KNN.from_dataframe(db, k=6)
	w.transform = "R"

	db["Ocorrências p. lag"] = weights.spatial_lag.lag_spatial(w, db["Ocorrências p."])

	lisa = esda.moran.Moran_Local(db["Ocorrências p."], w)

	spots_labels = {
		0: "Non-Significant",
		1: "HH",
		2: "LH",
		3: "LL",
		4: "HL",
	}

	db['labels'] = pd.Series(lisa.q, index=db.index).map(spots_labels)
	db['labels_sig'] = pd.Series(1*(lisa.p_sim < 0.05)*lisa.q, index=db.index).map(spots_labels)
	db.reset_index(inplace=True)

	fig1 = px.choropleth_mapbox(db, geojson=common_datasource.bairros_geojson, color="Ocorrências p.",
			color_continuous_scale=continuous_rdbu_scale,
			locations="NOME", featureidkey='properties.NOME',
			center={"lat": -25.459717, "lon": -49.278820},
			mapbox_style="carto-positron", zoom=9)

	fig2 = px.choropleth_mapbox(db, geojson=common_datasource.bairros_geojson, color="Ocorrências p. lag",
			color_continuous_scale=continuous_rdbu_scale,
			locations="NOME", featureidkey='properties.NOME',
			center={"lat": -25.459717, "lon": -49.278820},
			mapbox_style="carto-positron", zoom=9)

	fig3 = px.choropleth_mapbox(db, geojson=common_datasource.bairros_geojson, color="labels",
			color_discrete_map={'HH':hotspot, 'LL':coldspot, 'HL':high_low, 'LH':low_high},
			locations="NOME", featureidkey='properties.NOME',
			center={"lat": -25.459717, "lon": -49.278820},
			mapbox_style="carto-positron", zoom=9)

	fig4 = px.choropleth_mapbox(db, geojson=common_datasource.bairros_geojson, color="labels_sig",
			color_discrete_map={'Non-Significant':rgba(tertiary, .3), 'HH':hotspot, 'LL':coldspot, 'HL':high_low, 'LH':low_high},
			locations="NOME", featureidkey='properties.NOME',
			center={"lat": -25.459717, "lon": -49.278820},
			mapbox_style="carto-positron", zoom=9)
	
	fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, width=650)
	fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, width=650)
	fig3.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, width=650)
	fig4.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, width=650)

	return fig1, fig2, fig3, fig4

@callback(
	Output("spatiotemporal_map","figure"),
	Output("spatiotemporal_select","options"),	
	Output("spatiotemporal_variance","children"),
	Input("sidebar-apply", "n_clicks"),
	Input("spatiotemporal_select","value"),
	Input("my-date-picker-single","value")
)
def create_spatiotemporal_map_figure(n_clicks,outlier_date,navbar_date):
	f = ('OCORRENCIAS ~ ' +
		'OCORRENCIA_ANO ' +
		'+ OCORRENCIA_MES ' +
		'+ ATENDIMENTO_BAIRRO_NOME ' +
		'+ OCORRENCIAS_LAG1' +
		'+ OCORRENCIAS_LAG2' +
		'+ OCORRENCIAS_LAG3' +
		'+ OCORRENCIAS_LAG4' +
		'- 1')

	training_data = (gmc_datasource.ocorrencias_bairro_mes[
						(gmc_datasource.ocorrencias_bairro_mes['OCORRENCIA_MES'] <= int(navbar_date.split('-')[1])) &
						(gmc_datasource.ocorrencias_bairro_mes['OCORRENCIA_ANO'] <= int(navbar_date.split('-')[0]))])

	stm = smf.ols(f, data=training_data).fit()

	outliers_df = pd.DataFrame(np.concatenate((training_data.drop(columns=['OCORRENCIAS_LAG1','OCORRENCIAS_LAG2','OCORRENCIAS_LAG3','OCORRENCIAS_LAG4']).values, stm.predict().reshape((-1,1))), axis=1),
								columns=['OCORRENCIA_ANO','OCORRENCIA_MES','ATENDIMENTO_BAIRRO_NOME','OCORRENCIAS_ATENDIDAS','OCORRENCIAS_PREVISTAS'])

	outliers_df['OCORRENCIAS_PREVISTAS'] = outliers_df['OCORRENCIAS_PREVISTAS'].astype(int)
	outliers_df['ERRO'] = outliers_df['OCORRENCIAS_PREVISTAS'] - outliers_df['OCORRENCIAS_ATENDIDAS']
	outliers_df['Z-SCORE'] = (outliers_df['ERRO'] - outliers_df['ERRO'].mean())/outliers_df['ERRO'].std()
	outliers_df['OUTLIER'] = outliers_df['Z-SCORE'].apply(lambda x: 1*(abs(x) >= 2.575))

	outliers = (
		outliers_df[outliers_df['OUTLIER'] == 1]
		if outlier_date == None
		else outliers_df[(outliers_df['OUTLIER'] == 1) & (outliers_df['OCORRENCIA_ANO'] == int(outlier_date.split('/')[1])) & (outliers_df['OCORRENCIA_MES'] == int(outlier_date.split('/')[0]))])

	fig = px.choropleth_mapbox(
		outliers, 
		geojson=common_datasource.bairros_geojson, color="ATENDIMENTO_BAIRRO_NOME",
		hover_data=["OCORRENCIA_ANO","OCORRENCIA_MES","OCORRENCIAS_ATENDIDAS","OCORRENCIAS_PREVISTAS"],
		locations="ATENDIMENTO_BAIRRO_NOME", featureidkey='properties.NOME',
		center={"lat": -25.459717, "lon": -49.278820},
		mapbox_style="carto-positron", zoom=9)
	fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, width=800, height=650)

	marks = []
	for idx, row in outliers_df[outliers_df['OUTLIER'] == 1].iterrows():
		if((row['OCORRENCIA_ANO'],row['OCORRENCIA_MES']) not in marks):
			marks.append((row['OCORRENCIA_ANO'],row['OCORRENCIA_MES']))
		
	marks.sort()

	marks = [to_month_year_str(x) for x in marks]

	return fig, marks, f'Variância total explicada pelo modelo: {str(round(stm.rsquared,2)).split(".")[1]}%'