# -*- coding: utf-8 -*-
"""
Functions for visualization
"""
import numpy as np
#import pandas as pd
#import geopandas as gpd
from bokeh.sampledata.us_states import data as states
from shapely import affinity
from shapely.geometry import Polygon
from shapely.geometry import mapping, shape

###############################################################################
def df_filter(df,cond_cols=[]):
    """ df: dataframe
        cond_cols: list of conditions on which to filter the dataframe. List
    of list: first element contains column name, second is 'in' or 'notin' 
    depending on whether the elements must match the condition or not. Third 
    element is a list of values to match.
        Returns a copy of the original dataframe on which we applied the 
    filters passed.
    """
    df_out = df.copy()
    
    # Loop through conditions
    for cond in cond_cols:
        # Column to filter on, and values to match or not match
        col = cond[0]
        vals = cond[2]
        
        if cond[1] == 'in':
            df_out = df_out.loc[df_out[col].isin(vals),:]
        elif cond[1] == 'notin':
            df_out = df_out.loc[~df_out[col].isin(vals),:]
    
    return df_out
###############################################################################
def date_to_year_week(d):
    d_str = np.str(d)
    year = np.int(d_str[:4])
    if len(d_str) > 5:
        week = np.int(d_str[-2:])
    else:
        week = np.int(d_str[-1])
        
    return [year, week]
###############################################################################
def states_adjust(xs,ys,state_code):
    if state_code == 'AK':
#        scale = 1#0.4
#        xoff= 0 #1.2e6
#        yoff= 0#-4.8e6
#        rotate = 0#30
        scale = 0.4
        xoff= 24 #1.2e6
        yoff= -29#-4.8e6
        rotate = 0#30
#        origin = (-150,61)
#        # Adjust locations with positive longitude
#        max_i = max(xs)
#        for i in range(len(xs)):
#            if xs[i] > 0:
#                xs[i] = xs[i]-max_i-180
         
    elif state_code == 'HI':
        scale = 0.8
        xoff= 55#4.6e6
        yoff= 5#-1.1e6
        rotate = 10

    polygon = Polygon(zip(xs,ys))
#    geom = affinity.translate(shape(polygon), xoff=xoff, yoff=yoff)
#    geom = affinity.scale(geom, scale, scale)
#    geom = affinity.rotate(geom, rotate)
    
    geom = affinity.scale(shape(polygon), xfact=scale, yfact=scale)
    geom = affinity.rotate(geom, rotate)
    geom = affinity.translate(geom, xoff=xoff, yoff=yoff)

    new_coord = mapping(geom)['coordinates'][0]
    new_xs = [x[0] for x in new_coord]
    new_ys = [x[1] for x in new_coord]
    
    return new_xs, new_ys
###############################################################################
def adjust_city_coords(cities_data):
    
    n_cities = len(cities_data)
    latitudes, longitudes = np.zeros(n_cities), np.zeros(n_cities)
    
    # Loop through all cities
    for i in range(n_cities):
        # Get latitude y and longitude x
        geoloc = cities_data['GeoLocation'][i]
        ys_i,xs_i = map(float,geoloc[1:-1].split(','))
        
        # Adjust coordinates for Hawaii and Alaska only
        state_i = cities_data['StateCode'][i]
        if state_i in ['AK','HI']:
            state_i_xs, state_i_ys = states[state_i]["lons"], states[state_i]["lats"]
            state_i_xs.append(xs_i)
            state_i_ys.append(ys_i)
            state_i_xs_ajd, state_i_ys_adj = states_adjust(state_i_xs, state_i_ys,state_i)
            xs_i, ys_i = state_i_xs_ajd[-1],state_i_ys_adj[-1]
            
            # extra adjustment for anchorage for some reason
            if state_i == 'AK':
                xs_i = xs_i - 8.5
                xs_i = xs_i + 1.4
        
        # Save coordinates for city i
        latitudes[i] = ys_i
        longitudes[i] = xs_i
    
    # latitude and longitude coordinates
    cities_data.loc[:,'Longitude'] = longitudes
    cities_data.loc[:,'Latitude'] = latitudes
    
    return cities_data
###############################################################################
def set_stype(figure,  xlabel="", ylabel=""):
    #figure.title = 
    figure.title.align ='center'
    
    figure.xaxis.axis_label=xlabel
    figure.yaxis.axis_label =ylabel
    figure.xaxis.axis_label_text_font="times"
    
    figure.yaxis.axis_label_text_font="times"
    figure.xaxis.axis_label_text_font_style ="bold"
    figure.yaxis.axis_label_text_font_style ="bold"
    
    figure.title.text_font = "times"
    figure.title.text_font_style = "bold"
###############################################################################