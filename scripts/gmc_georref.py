
import math
import pandas as pd
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent='your_app_name')

df_gmc = pd.read_csv('./data/gmc/sigesguarda_cleaned.csv')

addresses = df_gmc['LOGRADOURO_NOME'].unique()

address_georef = {}

for address in addresses:
    if address not in address_georef.keys():
        try:
            location = geolocator.geocode(f'{address}, CURITIBA')
            lat, lon = location.latitude, location.longitude
            _, lat_whole = math.modf(lat)
            _, lon_whole = math.modf(lon)

            if(lat_whole != -25 or lon_whole != -49):
                location = geolocator.geocode(f'RUA {address}, CURITIBA')
                lat, lon = location.latitude, location.longitude
                _, lat_whole = math.modf(lat)
                _, lon_whole = math.modf(lon)
                
                if(lat_whole != -25 or lon_whole != -49):
                    location = geolocator.geocode(f'AVENIDA {address}, CURITIBA')
                    lat, lon = location.latitude, location.longitude
                    _, lat_whole = math.modf(lat)
                    _, lon_whole = math.modf(lon)
            
            if(lat_whole == -25 and lon_whole == -49):
                address_georef[address] = lat, lon
        except:        
            address_georef[address] = "",""

gmc_georref_df = pd.DataFrame(address_georef).transpose().reset_index().rename(columns={'index':'LOGRADOURO', 0:'LATITUDE', 1:'LONGITUDE'})
gmc_georref_df.to_csv('../data/gmc/addresses_georref.csv',index=False)
