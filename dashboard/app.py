# import dash
# from dash import html, dcc, Output, Input
# from pages.home import *
# 
# # Create app.
# app = dash.Dash(__name__)
# app.layout = home
# 
# if __name__ == '__main__':
#     app.run_server(debug=True, port=8150)

import dash_bootstrap_components as dbc
import dash
from dash import Input, Output, State, html, dcc
from components.navbar import navbar
from components.filter import sidebar

FA = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.2/css/all.min.css"

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, FA], use_pages=True)

app.layout = html.Div(
    [
        dcc.Location(id='location'), 
        navbar,
        sidebar,
        dash.page_container],
    id="layout",
    className='content-full p-0')

if __name__ == '__main__':
    app.run_server(debug=False, port=8150, host='0.0.0.0')