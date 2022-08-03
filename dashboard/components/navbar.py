import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Input, Output, State
from datetime import date

SIDEBAR = {
	'display': 'flex',
	'flex-direction': 'row',
	'justify-content':'start',
	'margin-left': '0px',
	'flex-wrap': 'nowrap',
}

navbar = dbc.Navbar(
    dbc.Container([
		dbc.Button(
			html.I(className="fa fa-sliders"), 
			id="open-sidebar",
			class_name="ms-0"),
		dbc.NavItem(dbc.NavLink("PCPR", href="/pcpr", class_name="text-white")),
		dbc.NavItem(dbc.NavLink("GMC", href="/gmc", class_name="text-white")),
		dcc.DatePickerSingle(
			id='my-date-picker-single',
			display_format='DD, MMM YYYY',
			min_date_allowed=date(1995, 8, 5),
			max_date_allowed=date(2022, 12, 31),
			initial_visible_month=date(2017, 8, 5),
			date=date(2017, 8, 25),
			className="date-picker",			
		)],
		id="navbar-container",
		style=SIDEBAR
	),
	class_name='row h-100 p-0',
    color="primary",
    dark=True,
)

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
