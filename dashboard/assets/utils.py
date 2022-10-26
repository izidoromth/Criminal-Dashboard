def to_month_year_str(obj):
	month = '{:02}'.format(obj[1])
	return f'{month}/{obj[0]}'