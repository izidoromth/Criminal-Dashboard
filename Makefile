dataprep: data/gmc/sigesguarda.csv data/DIVISA_DE_BAIRROS.geojson
	python scripts/dataprep.py

app: dashboard/app.py data/gmc/sigesguarda_cleaned.csv data/divisa_bairros_cleaned.geojson
	python dashboard/app.py