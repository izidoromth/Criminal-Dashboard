import dash
from dash import html, dcc, Output, Input, State
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/pcpr')

layout = html.Div(children=[
		html.Div(['PCPR ' for i in range(0,1000)]),
	],
)