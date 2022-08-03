import dash
from dash import html, dcc, Output, Input, State
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/gmc')

layout = html.Div(children=[
		html.Div('GMC')
	],
)