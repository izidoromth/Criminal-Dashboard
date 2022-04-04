dataprep: sigesguarda.csv DIVISA_DE_BAIRROS.geojson
	python dataprep.py

app: app.py sigesguarda_cleaned.csv divisa_bairros_cleaned.geojson
	python app.py