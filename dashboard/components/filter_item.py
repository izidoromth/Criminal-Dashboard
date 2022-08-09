from dash import html, dcc
from datetime import datetime

def filter_item(Title, items):
    return html.Div([html.Div(Title),*items], className="filter_item")