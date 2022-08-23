from gc import callbacks
import dash
from dash import html, dcc, callback, Input, Output, State, ctx
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import Layout
import pandas as pd
import statsmodels.formula.api as smf
from datetime import datetime
from assets.styles import *
from datasources.gmc_datasource import GmcDatasource

gmc_datasource = GmcDatasource.instance()

dash.register_page(__name__, path='/gmc', title="Painel Criminal: GMC")

temporal_tab = html.Div(children=[
        dcc.Location(id='loc'),
		dcc.Graph(id="model_outliers"),
		dcc.Graph(id="most_frequent_crimes"),
	],
)

spatial_tab = html.Div('Espacial')

spatiotemporal_tab = html.Div('Espaço-temporal')

layout = html.Div(
    [
		dcc.Tabs(
			[
				dcc.Tab(label="Análise Temporal", value="temporal-tab", selected_className="custom-tab--selected"),
				dcc.Tab(label="Análise Espacial", value="spatial-tab", selected_className="custom-tab--selected"),
				dcc.Tab(label="Análise Espaço-Temporal", value="spatiotemporal-tab", selected_className="custom-tab--selected"),
			],
			id="card-tabs",
			value="temporal-tab"
        ),
        html.Div(id="card-content"),
    ]
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
    Output("model_outliers", "figure"),
	Input("sidebar-apply", "n_clicks"),
	Input("my-date-picker-single","value"),
	[State("date-range-filter","value"),	
	State("occurrence-type-select","value")]
)
def create_outlier_model_view(n_clicks, navbar_date, dates, type):
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
	df_gmc_ols_model['x10_feriado'] = df_gmc_ols_model['FERIADO']
	df_gmc_ols_model['x11_pandemia'] = df_gmc_ols_model['OCORRENCIA_DATA_SEM_HORARIO'].apply(lambda x: 1 if x >= datetime.strptime('11/04/2020','%d/%m/%Y').date() else 0)
	df_gmc_ols_model['x12_dia_semana'] = df_gmc_ols_model['OCORRENCIA_DATA_SEM_HORARIO'].apply(lambda x: x.weekday())

	model_features = ['x0_final_de_semana','x1_time','x2_lag1','x3_lag2','x4_lag3','x5_lag4','x6_lag5','x7_lag6','x8_lag7','x10_feriado','x11_pandemia']
	model_formula = ' + '.join(model_features)	
	model_results = smf.ols(formula=f'OCORRENCIAS_ATENDIDAS ~ {model_formula} - 1', data=df_gmc_ols_model).fit()
	
	print(model_results.summary())

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

	return fig

@callback(
    Output("most_frequent_crimes", "figure"),
	Input("sidebar-apply", "n_clicks"),
	State("date-range-filter","value"),
)
def create_frequent_crimes_view(n_clicks, dates):
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
	})

	return fig