import dash_bootstrap_components as dbc
from dash import callback, Input, Output, State
from dash import html

sidebar = html.Div(
	[
		html.H4("Painel Criminal"),
		html.P("Some offcanvas content..."),
		# dbc.Button("X", id="sidebar-closebutton", n_clicks=0, class_name="sidebar-closebutton")
	],
	id="sidebar",
	className="sidebar-hidden"
)

@callback(
    Output("sidebar", "className"),
	Output("layout", "className"),
	State("sidebar", "className"),
    Input("open-sidebar", "n_clicks"),
	# Input("sidebar-closebutton","n_clicks")
)
def toggle_offcanvas(className, n_clicks):#, close):
	if n_clicks and className == "sidebar-hidden":
		return "sidebar","content p-0"
	return "sidebar-hidden","content-full p-0"