import dash
from dash import html, dcc, Output, Input, State, callback, ctx
import dash_bootstrap_components as dbc
from datasources.pcpr_datasource import PcprDatasource
from assets.styles import *
import numpy as np
from statsmodels.regression.linear_model import OLS
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import Layout
import pandas as pd
from datetime import datetime

pcpr_datasource = PcprDatasource.instance()

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

spatial_tab = html.Div(children=["Espacial"
		# dcc.Graph(id="spatial_model_occurrences"),
		# dcc.Graph(id="spatial_model_lag"),
		# dcc.Graph(id="spatial_model_clusters"),
		# dcc.Graph(id="spatial_model_significants"),
	],
	className="temporal-tab"
)

spatiotemporal_tab = html.Div(children=["Espaço-temporal"
	# dcc.Graph(id="spatiotemporal_map"),
	# dcc.Dropdown(id='spatiotemporal_select', placeholder="Selecione o mês da anomalia",style={'width':'250px'})
	],
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

	return fig, f'Variância total explicada pelo modelo: {str(round(model.rsquared,2)).split(".")[1]}%'

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