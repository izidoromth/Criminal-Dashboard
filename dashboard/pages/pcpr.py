import dash
from dash import html, dcc, Output, Input, State, callback, ctx
import dash_bootstrap_components as dbc
from datasources.pcpr_datasource import PcprDatasource
from datasources.common_datasource import CommonDatasource
from assets.styles import *
import numpy as np
from statsmodels.regression.linear_model import OLS
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import Layout
import pandas as pd
import geopandas as gpd
from pysal.explore import esda
from pysal.lib import weights
from datetime import datetime
from assets.utils import to_month_year_str
import statsmodels.formula.api as smf

pcpr_datasource = PcprDatasource.instance()
common_datasource = CommonDatasource.instance()

dash.register_page(__name__, path='/pcpr', title="Painel Criminal: PCPR")

temporal_tab = html.Div(children=[
        dcc.Location(id='loc'),
		dcc.Graph(id="temporal_model_pcpr"),
		html.Div([
			dcc.Graph(id="most_frequent_crimes_pcpr"),
			html.Div(id="variance_label_pcpr", style={'font-size':'25px', 'margin': '10px 30px'})],
			style={'display':'flex', 'flex-direction':'row', 'justify-content':'space-between'}
		)		
	],
)

spatial_tab = html.Div(children=[
		dcc.Graph(id="spatial_model_occurrences_pcpr"),
		dcc.Graph(id="spatial_model_lag_pcpr"),
		dcc.Graph(id="spatial_model_clusters_pcpr"),
		dcc.Graph(id="spatial_model_significants_pcpr"),
	],
	className="temporal-tab"
)

spatiotemporal_tab = html.Div(children=[
	dcc.Graph(id="spatiotemporal_map_pcpr"),
	html.Div([
		dcc.Dropdown(id='spatiotemporal_select_pcpr', placeholder="Selecione o mês da anomalia",style={'width':'250px'}),
		html.Div(id="spatiotemporal_variance_pcpr", style={'font-size':'25px', 'margin': '10px 30px'})],
		style={'display':'flex', 'flex-direction':'column', 'justify-content':'space-between'})],
	style=spatio_temporal_class
)

layout = html.Div(
    [
		dcc.Tabs(
			[
				dcc.Tab(label="Análise Temporal", value="temporal-tab-pcpr", selected_className="custom-tab--selected"),
				dcc.Tab(label="Análise Espacial", value="spatial-tab-pcpr", selected_className="custom-tab--selected"),
				dcc.Tab(label="Análise Espaço-Temporal", value="spatiotemporal-tab-pcpr", selected_className="custom-tab--selected"),
			],
			id="card-tabs-pcpr",
			value="temporal-tab-pcpr",
			persistence=True
        ),
        html.Div(id="card-content-pcpr"),
    ],
	style={'margin-top':'40px','background-color': 'white'}
)

@callback(
	Output("card-content-pcpr", "children"), 
	[Input("card-tabs-pcpr", "value")]
)
def change_tab_content(active_tab):
	if active_tab == 'temporal-tab-pcpr':
		return temporal_tab
	elif active_tab == 'spatial-tab-pcpr':
		return spatial_tab
	elif active_tab == 'spatiotemporal-tab-pcpr':
		return spatiotemporal_tab

@callback(
    Output("temporal_model_pcpr", "figure"),
	Output("variance_label_pcpr","children"),
	Input("sidebar-apply", "n_clicks"),
	Input("my-date-picker-single","value"),
	[State("date-range-filter","value"),	
	State("occurrence-type-select","value")]
)
def create_temporal_outlier_model_view_pcprp(n_clicks,  navbar_date, dates, type):
	if ctx.triggered[0]['prop_id'] == "my-date-picker-single.value":
		pcpr_datasource.filter_by_end_date(navbar_date)

	initial_date = datetime.strptime(dates[0],'%Y-%m-%d').date() if dates != None and ctx.triggered[0]['prop_id'] == "sidebar-apply.n_clicks" else pcpr_datasource.getMinDate()
	end_date = datetime.strptime(dates[1],'%Y-%m-%d').date() if dates != None and ctx.triggered[0]['prop_id'] == "sidebar-apply.n_clicks" else pcpr_datasource.getMaxDate()

	pcpr_df = pcpr_datasource.df[(pcpr_datasource.df['data_fato'] >= initial_date) & (pcpr_datasource.df['data_fato'] <= end_date)]
	pcpr_df = pcpr_df[pcpr_df['tipo'] == type] if type != None else pcpr_df
	pcpr_df = pcpr_df.groupby(['data_fato','PANDEMIA']).sum().reset_index()
	pcpr_df['LAG1'] = pcpr_df['qtde_boletins'].shift(1).fillna(0)
	pcpr_df['LAG2'] = pcpr_df['qtde_boletins'].shift(2).fillna(0)
	# pcpr_df['LAG3'] = pcpr_df['qtde_boletins'].shift(3).fillna(0)
	# pcpr_df['LAG4'] = pcpr_df['qtde_boletins'].shift(4).fillna(0)
	pcpr_df['TEMPO'] = np.arange(pcpr_df.shape[0])

	X, y = pcpr_df[['TEMPO','LAG1','LAG2','PANDEMIA']], pcpr_df['qtde_boletins']

	model = OLS(y, X).fit()

	df_results = pd.DataFrame([y, model.predict(X)]).transpose()
	df_results['Data'] = pcpr_df['data_fato']
	df_results.rename(columns={'Unnamed 0':'PREVISTAS', 'qtde_boletins':'ATENDIDAS'},inplace=True)
	df_results.drop([0],inplace=True)

	df_results['ERRO'] = df_results['PREVISTAS'] - df_results['ATENDIDAS']
	df_results['Z-SCORE'] = (df_results['ERRO'] - df_results['ERRO'].mean())/df_results['ERRO'].std()
	df_results['OUTLIER'] = df_results['Z-SCORE'].apply(lambda x: 1*(abs(x) >= 2.17))

	fig1 = px.line(df_results, x='Data', y=['ATENDIDAS','PREVISTAS'])
	fig1.data[0].line.color = 'rgba(135, 148, 168, .85)'
	fig1.data[1].line.color = 'rgba(75, 83, 94, 1)'

	try:
		fig2 = px.scatter(df_results[df_results['OUTLIER'] == 1], x='Data', y='ATENDIDAS', color_discrete_sequence=[secondary])
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

	var_exp_str = '0'
	if(model.rsquared > 0):
		var_exp_str = str(round(model.rsquared,2)).split(".")[1] if len(str(round(model.rsquared,2)).split(".")) > 1 else str(round(model_results.rsquared,2))

	return fig, f'Variância total explicada pelo modelo: {var_exp_str}%'

@callback(
    Output("most_frequent_crimes_pcpr", "figure"),
	Input("sidebar-apply", "n_clicks"),
	Input("temporal_model_pcpr","relayoutData"),
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
		initial_date = datetime.strptime(dates[0],'%Y-%m-%d').date() if dates != None else pcpr_datasource.getMinDate()
		end_date = datetime.strptime(dates[1],'%Y-%m-%d').date() if dates != None else pcpr_datasource.getMaxDate()

	dfg = pcpr_datasource.df[
			(pcpr_datasource.df['data_fato'] >= initial_date) & 
			(pcpr_datasource.df['data_fato'] <= end_date)
		].groupby(['tipo']).sum().reset_index().rename(columns={'tipo':'Natureza', 'qtde_boletins':'Ocorrências'}).sort_values(by="Ocorrências",ascending=False)
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
    [Output("spatial_model_occurrences_pcpr", "figure"),
	Output("spatial_model_lag_pcpr", "figure"),
	Output("spatial_model_clusters_pcpr", "figure"),
	Output("spatial_model_significants_pcpr", "figure")],
	Input("sidebar-apply", "n_clicks"),
	Input("my-date-picker-single","value"),
	[State("date-range-filter","value"),	
	State("occurrence-type-select","value")]
)
def create_spatial_outlier_model_view(n_clicks, navbar_date, dates, occurrence_type):	
	if ctx.triggered[0]['prop_id'] == "my-date-picker-single.value":
		pcpr_datasource.filter_by_end_date(navbar_date)

	initial_date = datetime.strptime(dates[0],'%Y-%m-%d').date() if dates != None and ctx.triggered[0]['prop_id'] == "sidebar-apply.n_clicks" else pcpr_datasource.getMinDate()
	end_date = datetime.strptime(dates[1],'%Y-%m-%d').date() if dates != None and ctx.triggered[0]['prop_id'] == "sidebar-apply.n_clicks" else pcpr_datasource.getMaxDate()

	gmc_ref = pcpr_datasource.df[(pcpr_datasource.df['data_fato'] >= initial_date) & (pcpr_datasource.df['data_fato'] <= end_date) & (pcpr_datasource.df['tipo'] == occurrence_type)].groupby(['descBairro']).sum().reset_index().set_index('descBairro') if occurrence_type != None else pcpr_datasource.df[(pcpr_datasource.df['data_fato'] >= initial_date) & (pcpr_datasource.df['data_fato'] <= end_date)].groupby(['descBairro']).sum().reset_index().set_index('descBairro')
	gmc_ref = gmc_ref.join(common_datasource.dem)
	gmc_ref.dropna(inplace=True)
	gmc_ref['Ocorrências p.'] = gmc_ref['qtde_boletins'] / gmc_ref['População Total']
	gmc_ref.drop(columns=['qtde_boletins','População Total'], inplace=True)
	
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
	Output("spatiotemporal_map_pcpr","figure"),
	Output("spatiotemporal_select_pcpr","options"),	
	Output("spatiotemporal_variance_pcpr","children"),
	Input("sidebar-apply", "n_clicks"),
	Input("spatiotemporal_select_pcpr","value"),
	Input("my-date-picker-single","value")
)
def create_spatiotemporal_map_figure(n_clicks,outlier_date,navbar_date):
	f = ('qtde_boletins ~ ' +
		'ano ' +
		'+ mes ' +
		'+ descBairro ' +
		'+ lag1' +
		'+ lag2' +
		'+ lag3' +
		'+ lag4' +
		'- 1')

	training_data = (pcpr_datasource.ocorrencias_bairro_mes[
						(pcpr_datasource.ocorrencias_bairro_mes['mes'] <= int(navbar_date.split('-')[1])) &
						(pcpr_datasource.ocorrencias_bairro_mes['ano'] <= int(navbar_date.split('-')[0]))])

	stm = smf.ols(f, data=training_data).fit()

	outliers_df = pd.DataFrame(np.concatenate((training_data.drop(columns=['lag1','lag2','lag3','lag4']).values, stm.predict().reshape((-1,1))), axis=1),
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

	var_exp_str = '0'
	if(stm.rsquared > 0):
		var_exp_str = str(round(stm.rsquared,2)).split(".")[1] if len(str(round(stm.rsquared,2)).split(".")) > 1 else str(round(stm.rsquared,2))

	return fig, marks, f'Variância total explicada pelo modelo: {var_exp_str}%'