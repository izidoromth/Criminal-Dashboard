import json
from unicodedata import category
import dash
from dash import html, dcc, Output, Input
import pandas as pd
import threading
import plotly.express as px
from map import *

df = pd.read_csv('./sigesguarda_cleaned.csv')
f = open('./divisa_bairros_cleaned.geojson', encoding='utf-8')

bairros_geojson = json.load(f)

f.close()

# Create app.
app = dash.Dash(__name__, external_scripts=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),

    dcc.Link('Map', href='/map'),

    # map,
    html.Div(id='heatmap'),
    html.Div(id='histogram')
    ]
)

@app.callback(Output('histogram', 'children'),
              [Input('url', 'pathname')])
def histogram_update(pathname):
    crimes_per_year = df[['ATENDIMENTO_ANO','NATUREZA1_DESCRICAO']].value_counts().reset_index().sort_values(by='ATENDIMENTO_ANO')
    return dcc.Graph(figure=px.line(pd.DataFrame(dict(x=crimes_per_year['ATENDIMENTO_ANO'], y = crimes_per_year[0], color = crimes_per_year['NATUREZA1_DESCRICAO'])).sort_values(by='x'),x='x',y='y',color='color'))

@app.callback(Output('heatmap', 'children'),
              [Input('url', 'pathname')])
def heatmap_update(pathname):
    ocorrencias_bairro = df['ATENDIMENTO_BAIRRO_NOME'].value_counts().to_frame().reset_index().rename(columns={'ATENDIMENTO_BAIRRO_NOME': 'OCORRENCIAS', 'index': 'NOME'})
    return dcc.Graph(figure=px.choropleth_mapbox(ocorrencias_bairro, geojson=bairros_geojson, color="OCORRENCIAS",
                            locations="NOME", featureidkey="properties.NOME",
                            center={"lat": -25.459717, "lon": -49.278820},
                            mapbox_style="carto-positron", zoom=9))


# @app.callback(Output(MARKER_GROUP_ID, 'children'), [Input(MAP_ID, 'click_lat_lng')])
# def set_marker(x):
#     if not x:
#         return None
#     return dl.Marker(position=x, children=[dl.Tooltip('Test')])
# 
# 
# @app.callback(Output(COORDINATE_CLICK_ID, 'children'), [Input(MAP_ID, 'click_lat_lng')])
# def click_coord(e):
#     if not e:
#         return "-"
#     return json.dumps(e)

if __name__ == '__main__':
    app.run_server(debug=True, port=8150)