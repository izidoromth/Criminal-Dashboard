primary = '#25282e'
secondary = '#626c7a'
tertiary = '#e3e1e1'
hotspot = 'rgba(0, 0, 0, 0.8)'
coldspot = 'rgba(180, 180, 180, 0.8)'
high_low = 'rgba(60, 60, 60, 0.8)'
low_high = 'rgba(120, 120, 120, 0.8)'
continuous_grey_scale = ['rgb(217,217,217)','rgb(189,189,189)','rgb(150,150,150)','rgb(115,115,115)','rgb(82,82,82)','rgb(37,37,37)','rgb(0,0,0)']

def rgba(hex, alpha):
    r = int(hex[1:3], 16)  
    g = int(hex[3:5], 16)  
    b = int(hex [5:7], 16) 
    return f'rgba({r},{g},{b},{alpha})'

navbar_datepicker = {
    'transition': 'left .5s',
    'background-color': 'transparent', 
    'color': 'white', 
    'position':'absolute', 
    'left':'50%', 
    'transform': 'translate(-50%,0)',
    'width': '110px',
    'background-color': 'transparent',
    'color': 'white',
}