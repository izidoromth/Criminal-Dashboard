import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import dcc, html, callback, Input, Output
import datetime as dt
from assets.styles import primary, secondary
from datetime import datetime
from datasources.gmc_datasource import GmcDatasource
from assets.styles import navbar_datepicker

gmc_datasource = GmcDatasource.instance()

NAVBAR = {
	'display': 'flex',
	'flex-direction': 'row',
	'justify-content':'start',
	'margin': '0px',
	'padding': '0px',
	'flex-wrap': 'nowrap',
}

navbar = dbc.Navbar(
    dbc.Container([
		dcc.Location(id="location_navbar"),
		dbc.Button(
			html.I(className="fa fa-sliders"), 
			id="open-sidebar",
			class_name="ms-0",
			style={'background-color':primary}),
		dbc.NavItem(id="pcpr_navitem", children=dbc.NavLink("PCPR", href="/pcpr", class_name="text-white")),
		dbc.NavItem(id="gmc_navitem", children=dbc.NavLink("GMC", href="/gmc", class_name="text-white")),
		dmc.DatePicker(
			id='my-date-picker-single',
			inputFormat='DD, MMM YYYY',
			minDate=gmc_datasource.getMinDate(),
			maxDate=gmc_datasource.getMaxDate(timefix=True),
			value=gmc_datasource.getMaxDate(),
			style=navbar_datepicker,
			clearable=False
		)],
		style=NAVBAR,
	),
	class_name='row p-0 header',
	style={'height':'40px', 'padding':'0px'},
    color=primary,
    dark=True,
)

@callback(
	Output("pcpr_navitem","style"),
	Output("gmc_navitem","style"),
	Input("location_navbar","href")
)
def update_navbar_selected(href):
	if 'pcpr' in href:
		return {'background-color':secondary},{}
	elif 'gmc' in href:
		return {},{'background-color':secondary}
	else:
		return {},{}

# @callback(
# 	Output("navbar-container","style"),
# 	State("navbar-container","style"),
# 	Input("open-sidebar","n_clicks")
# )
# def toggle_navbarContainer_style(style,n_clicks):
# 	if n_clicks:
# 		if style == SIDEBAR_CLOSED:
# 			return SIDEBAR_OPEN
# 		return SIDEBAR_CLOSED
# 	return style
