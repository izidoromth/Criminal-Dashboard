from gc import callbacks
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import numpy as np
import plotly.express as px
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

dash.register_page(__name__, path='/gmc', title="Painel Criminal: GMC")

df = pd.read_csv('./dashboard/datasources/df_alltime_allcrimes_series.csv')

temporal_tab = html.Div(children=[
        dcc.Location(id='loc'),
		dcc.Graph(id="arima_forecast")
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
    Output("arima_forecast", "figure"),
	Input("sidebar-apply", "n_clicks"),
	[State("date-range-filter","start_date"),
	State("date-range-filter","end_date")]
)
def create_arima_view(n_clicks, initial_date, end_date):
	if initial_date == None:
		initial_date = df['OCORRENCIA_DATA_SEM_HORARIO'].min()

	if end_date == None:
		end_date = df['OCORRENCIA_DATA_SEM_HORARIO'].max()

	series = np.array(df[(df['OCORRENCIA_DATA_SEM_HORARIO'] >= initial_date) & (df['OCORRENCIA_DATA_SEM_HORARIO'] <= end_date)]['OCORRENCIAS_ATENDIDAS'].squeeze())
	# arima_model = ARIMA(series, order=(2,2,7))
	# model = arima_model.fit()

	# df_forecast = pd.DataFrame([pd.date_range(start=initial_date,end=end_date), series, model.predict()]).transpose().reset_index().rename(columns={0:'Data', 1:'Real',2:'Previsto'})
	df_forecast = pd.DataFrame([pd.date_range(start=initial_date,end=end_date), series]).transpose().reset_index().rename(columns={0:'Data', 1:'Real',2:'Previsto'})
	fig = px.line(df_forecast,x='Data',y=df_forecast.columns[1:])
	fig.update_xaxes(rangeslider_visible=True)

	return fig