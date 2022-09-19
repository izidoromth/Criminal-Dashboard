primary = '#25282e'
secondary = '#626c7a'
tertiary = '#e3e1e1'
hotspot = 'rgba(103, 0, 31, 1)'
coldspot = 'rgba(6, 50, 100, 1)'
high_low = 'rgba(184, 0, 55, 1)'
low_high = 'rgba(12, 103, 207, 1)'
continuous_rdbu_scale = ['rgba(6, 50, 100, 1)', 'rgba(57, 134, 188, 1)', 'rgba(156, 202, 225, 1)', 'rgba(240, 156, 123, 1)', 'rgba(182, 32, 47, 1)', 'rgba(103, 0, 31, 1)']

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