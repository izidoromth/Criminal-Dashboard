import json
from unicodedata import category
import dash
from dash import html, dcc, Output, Input
import pandas as pd
import threading
import plotly.express as px
from pages.styles import *
from pages.map import *

df = pd.read_csv('./data/sigesguarda_cleaned.csv')
f = open('./data/divisa_bairros_cleaned.geojson', encoding='utf-8')

bairros_geojson = json.load(f)

f.close()

# Create app.
app = dash.Dash(__name__, external_scripts=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.layout = (
    html.Div(
        [
            dcc.Location(id='url', refresh=False),
            dcc.Link('Map', href='/map'),
            # map,
            html.Div(id='heatmap'),
            html.Div(
                dcc.Slider(
                    df['ATENDIMENTO_ANO'].min(),
                    df['ATENDIMENTO_ANO'].max(),
                    step=None,
                    id='crossfilter-year--slider',
                    value=df['ATENDIMENTO_ANO'].max(),
                    marks={str(year): str(year) for year in df['ATENDIMENTO_ANO'].unique()}
                ), 
                style=slider
            ),
            html.Div(
                [
                    dcc.Dropdown(
                        df['ATENDIMENTO_BAIRRO_NOME'].sort_values().unique(),
                        '',
                        id='crossfilter-district',
                        style={ 'width': '300px'}
                    ),
                    html.Div(
                        id='histogram', 
                        style={ 'width': '1400px'}
                    ),
                ], 
                style=histogram_div
            )
        ], 
        style=main_div
    )
)

@app.callback(
    Output('histogram', 'children'),
    Input('crossfilter-district', 'value')
)
def histogram_update(district):
    districts = df['ATENDIMENTO_BAIRRO_NOME'].sort_values().unique()
    crimes_per_year = None
    if(district in districts):
        crimes_per_year = df[df['ATENDIMENTO_BAIRRO_NOME'] == district][['ATENDIMENTO_ANO','NATUREZA1_DESCRICAO']].value_counts().reset_index().sort_values(by='ATENDIMENTO_ANO')
    else:
        crimes_per_year = df[['ATENDIMENTO_ANO','NATUREZA1_DESCRICAO']].value_counts().reset_index().sort_values(by='ATENDIMENTO_ANO')
    fig = px.line(pd.DataFrame(dict(x=crimes_per_year['ATENDIMENTO_ANO'], y = crimes_per_year[0], color = crimes_per_year['NATUREZA1_DESCRICAO'])).sort_values(by='x'),x='x',y='y',color='color')
    fig.update_layout({'plot_bgcolor': '#232775',
                       'paper_bgcolor': '#232775',})
    fig.update_layout(
        font_color='white',
        legend=dict(
            bgcolor = '#00055C',
            font=dict(
                family="Courier",
                size=12,
                color="white"
            )))
    fig.update_traces(
        marker=dict
            (
                size=12,
                line=dict(
                    width=2,
                    color='white')
            ),
        selector=dict(mode='markers'))
    return dcc.Graph(figure=fig)

@app.callback(
    Output('heatmap', 'children'),
    Input('crossfilter-year--slider', 'value')
)
def heatmap_update(year):
    ocorrencias_bairro = df[df['ATENDIMENTO_ANO'] == year]['ATENDIMENTO_BAIRRO_NOME'].value_counts().to_frame().reset_index().rename(columns={'ATENDIMENTO_BAIRRO_NOME': 'OCORRENCIAS', 'index': 'NOME'})
    fig=px.choropleth_mapbox(
            ocorrencias_bairro, geojson=bairros_geojson, color="OCORRENCIAS",
            locations="NOME", featureidkey="properties.NOME",
            center={"lat": -25.459717, "lon": -49.278820},
            mapbox_style="carto-positron", zoom=9
        )
    fig.update_layout(
        {
            'plot_bgcolor': '#232775',
            'paper_bgcolor': '#232775'
        }
    )
    fig.update_layout(
        font_color='white',
        legend=dict(
            bgcolor = '#00055C',
            font=dict(
                family="Courier",
                size=12,
                color="white"
            )
        )
    )
    return dcc.Graph(figure=fig)

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