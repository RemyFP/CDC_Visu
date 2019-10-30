# -*- coding: utf-8 -*-
"""
Prepares data to be used for the flu pandemic visualization
"""

import os
import numpy as np
import pandas as pd
#import glob
#import geopandas as gpd
# import json
# from bokeh.io import output_notebook, output_file
# from bokeh.io import show
# from bokeh.plotting import figure
# from bokeh.models import GeoJSONDataSource,LinearColorMapper,ColorBar
# from bokeh.models import ColumnDataSource,FactorRange,Panel
# from bokeh.palettes import brewer, Category20, Viridis256, Category10
# from bokeh.models import FixedTicker,NumeralTickFormatter,HoverTool
# from bokeh.plotting import show as show_inline
#from bokeh.models.widgets import Tabs#,RadioButtonGroup, Div
# from bokeh.layouts import column,row, widgetbox,WidgetBox
#from bokeh.io import curdoc

np.set_printoptions(linewidth=130)
pd.set_option('display.width', 130)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.options.display.float_format = '{:,.8f}'.format
pd.set_option('precision', -1)

###############################################################################
###############################################################################
def data_prep(data_folder):
#    folder = 'C:\\Users\\remyp\\Research\\CDC Flu Pandemic\\Visualization\\Data'
    
    cities_filename = 'Cities.xlsx'
    cases_filename = '2009 pandemic - State level.csv'
    
    cities_path = data_folder + os.sep + cities_filename
    cases_path = data_folder + os.sep + cases_filename
    
    cities_data = pd.read_excel(cities_path,sheet_name = 'Cities')
    case_data = pd.read_csv(cases_path)
    
    # Rename columns
    cities_data.rename(columns={'StateAbbr':'StateCode',
                                'StateDesc':'State',
                                'PopulationCount':'Population',
                                'CityName':'City'},inplace=True)
    
    # Get map from state abbreviation to long name
    state_map = cities_data.loc[:,['StateCode','State']].\
        drop_duplicates(keep='first')
    
    ### Dummy data
    # Keep rate data only
    rate_cols = ['HospitalizationRate','DeathRate','CaseRate']
    info_cols = ['Date','State','Age']
    case_data = case_data.loc[:,info_cols + rate_cols]
    
    # Add year and week from date
    case_data.loc[:,'Year'] = case_data.apply(lambda x:\
                 np.int(np.str(x['Date'])[:4]),axis=1)
    case_data.loc[:,'Week'] = case_data.apply(lambda x:\
                 np.int(np.str(x['Date']).replace(np.str(x['Year']),'')),axis=1)
    
    # Convert to long format
    states_epi = pd.melt(case_data, id_vars=info_cols + ['Year','Week'], value_vars=rate_cols)
    states_epi.rename(columns={'variable':'Metric','value':'Value'},inplace=True)
    
    # Add state abbreviations
    states_epi = pd.merge(states_epi,state_map,left_on='State',
                          right_on='State',how='left')
    
    # Set case rates in each city equal to the state numbers
    cities_epi = cities_data.loc[:,['ID','State','City']]
    cities_epi = pd.merge(cities_epi,states_epi,left_on='State',right_on='State',how='left')
    
    # Replace NAs by zero
    cities_epi.fillna({'Value':0},inplace=True)
    states_epi.fillna({'Value':0},inplace=True)
    
    return cities_data, cities_epi, states_epi
