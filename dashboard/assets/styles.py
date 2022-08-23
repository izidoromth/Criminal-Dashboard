primary = '#25282e'
secondary = '#626c7a'
tertiary = '#e3e1e1'

def rgba(hex, alpha):
    r = int(hex[1:3], 16)  
    g = int(hex[3:5], 16)  
    b = int(hex [5:7], 16) 
    return f'rgba({r},{g},{b},{alpha})'