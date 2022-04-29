import dash_leaflet as dl
from dash import html

MAP_ID = "map"
MARKER_GROUP_ID = "marker-group"
COORDINATE_CLICK_ID = "coordinate-click-id"

map = html.Div([
    dl.Map(style={'width': '1000px', 'height': '500px'},
        center=[-17.782769, -50.924872],
        zoom=30,
        children=[
            dl.TileLayer(url="http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}"),
            dl.LayerGroup(id=MARKER_GROUP_ID)
        ], id=MAP_ID),
    html.P("Coordinate (click on map):"),
    html.Div(id=COORDINATE_CLICK_ID)])