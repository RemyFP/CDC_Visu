# -*- coding: utf-8 -*-
import os
import numpy as np
#import pandas as pd
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
from bokeh.models.widgets import Tabs#,RadioButtonGroup, Div
# from bokeh.layouts import column,row, widgetbox,WidgetBox
from bokeh.io import curdoc

#folder_path = ['C:','Users','remyp','Research','CDC Flu Pandemic','Visualization','Data']
#folder = os.sep.join(folder_path)
#os.chdir(folder)
import data_prep
import visu_fn
import tab_city_map
import tab_state_map
import tab_ts_single_loc
import tab_ts_single_group


### Inputs
# Get data
data_folder = os.sep.join([os.getcwd(),'Data'])
cities_data, cities_epi, states_epi = data_prep.data_prep(data_folder)

# State map
tab_state_map_ = tab_state_map.map_tab(cities_data, states_epi)
tab_city_map_ = tab_city_map.map_tab(cities_data, cities_epi)
tab_ts_single_loc_ = tab_ts_single_loc.ts_tab(cities_data, cities_epi,states_epi)
tab_ts_single_group_ = tab_ts_single_group.ts_tab(cities_data, cities_epi,states_epi)

# Put all the tabs into one application
tabs = Tabs(tabs = [tab_city_map_,tab_state_map_,tab_ts_single_loc_,tab_ts_single_group_])

# Put the tabs in the current document for display
curdoc().add_root(tabs)
curdoc().title = 'Influenza Pandemic Simulation'


# To run from Spyder (radio buttons won't work)
#from bokeh.io import output_file
#from bokeh.plotting import show as show_inline
#from bokeh.io import show
#output_file('foo.html')
#show(tabs)#,browser="chrome")

# To run from command (in the folder of the file) using the command
# bokeh serve --show main_visu.py
# curdoc().add_root(column(regions_button_plt,source_set_button_plot,div,p_ts))
# curdoc().title = "Venezuela Situational Awareness"



# Put the tabs in the current document for display
#curdoc().add_root(tabs)
#curdoc().title = 'Flu High Risk population'

