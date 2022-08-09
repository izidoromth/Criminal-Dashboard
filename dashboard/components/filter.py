import dash_bootstrap_components as dbc
from dash import callback, Input, Output, State, html, dcc
from datetime import datetime
from components.filter_item import filter_item

sidebar = html.Div(
	[
		html.H4("Painel Criminal"),
		filter_item("Intervalo", 
			[dcc.DatePickerRange(
				id='date-range-filter',
				min_date_allowed=datetime.strptime('01/01/2009','%d/%m/%Y'),
				max_date_allowed=datetime.strptime('01/01/2022','%d/%m/%Y'),
				initial_visible_month=datetime.strptime('01/01/2009','%d/%m/%Y'),
				clearable=True,
				display_format='DD/MM/YYYY',
			)]
		),
		dbc.Button("Aplicar", id="sidebar-apply", n_clicks=0, class_name="sidebar-apply")
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