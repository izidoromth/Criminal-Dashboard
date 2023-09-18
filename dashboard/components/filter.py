import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import callback, Input, Output, State, html, dcc
import datetime as dt
from components.filter_item import filter_item
from datasources.gmc_datasource import GmcDatasource
from assets.styles import navbar_datepicker

gmc_datasource = GmcDatasource.instance()

sidebar = html.Div(
	[
		dcc.Location(id='filter-loc'),
		html.H4("Painel Criminal"),
		filter_item("Intervalo", 
			[dmc.DateRangePicker(
				id='date-range-filter',
				minDate=gmc_datasource.getMinDate(),
				maxDate=gmc_datasource.getMaxDate(timefix=True),
				clearable=True,
				placeholder="Selecione o intervalo de datas",
				style={'width':'220px'},
				# value=[,]
				inputFormat='DD/MM/YYYY',
			)]
		),
		filter_item("Natureza", 
			[dmc.Select(
				placeholder="Selecione a natureza",
				id="occurrence-type-select",
				value=None,
				clearable=True,
				data=gmc_datasource.getCrimesType(),
				style={'width': '220px'},
        	)]
		),
		dbc.Button("Aplicar", id="sidebar-apply", n_clicks=0, class_name="sidebar-apply color-primary")
	],
	id="sidebar",
	className="sidebar-hidden"
)

@callback(
	Output("occurrence-type-select","data"),
	Output("date-range-filter","minDate"),
	Output("date-range-filter","maxDate"),
	Output("occurrence-type-select","value"),
	Input("filter-loc","href")
)
def change_filter_datasource(href):
	if href.split('/')[-1] == 'gmc':
		return gmc_datasource.getCrimesType(), gmc_datasource.getMinDate(), gmc_datasource.getMaxDate(), None

@callback(
    Output("sidebar", "className"),
	Output("layout", "className"),
	Output("my-date-picker-single", "style"),
	State("sidebar", "className"),
    Input("open-sidebar", "n_clicks")
)
def toggle_offcanvas(className, n_clicks):#, close):
	if n_clicks and className == "sidebar-hidden":
		navbar_datepicker['left'] = '40%'
		return "sidebar","content p-0",navbar_datepicker
	navbar_datepicker['left'] = '50%'
	return "sidebar-hidden","content-full p-0",navbar_datepicker