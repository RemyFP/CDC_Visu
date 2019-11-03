# -*- coding: utf-8 -*-
"""
Time series tab: single location (city or state), multiple groups
"""
import numpy as np
#import pandas as pd
import visu_fn
#from bokeh.sampledata.us_states import data as states
from bokeh.plotting import figure
from bokeh.models import Panel,NumeralTickFormatter#,LinearColorMapper,ColorBar#,GeoJSONDataSource
from bokeh.models import ColumnDataSource#,Slider
#from bokeh.palettes import Viridis256#,brewer, Category20
from bokeh.models import HoverTool#,NumeralTickFormatter#,HoverTool#,FixedTicker
# from bokeh.plotting import show as show_inline
from bokeh.models.widgets import RadioButtonGroup, Div, RadioGroup
from bokeh.layouts import column,WidgetBox,row#,widgetbox
from bokeh.models.tickers import FixedTicker
#import matplotlib as plt
#import matplotlib.cm as cm

from bokeh.palettes import Category10#,brewer, Category20, Viridis256
#from bokeh.models import FixedTicker#,HoverTool#,NumeralTickFormatter
#from bokeh.io import curdoc
from datetime import datetime as dt
import datetime
from functools import partial

###############################################################################
###############################################################################
def ts_tab(cities_data, cities_epi,states_epi,state_to_cities):#, all_rates, all_cumul):
    # Possible metric to show
    metrics_list = np.unique(cities_epi['Metric']).tolist()
    age_groups_list = np.unique(cities_epi['Age']).tolist()
    age_groups_list.sort(key = lambda x: np.int(x[:2].split('-')[0]) if x[:2] != 'Ov' else 99)
    keep_age_groups = ['0-4 yr', '5-17 yr', '18-49 yr', '50-64 yr', '65+ yr','Overall']
    age_groups_list = [a for a in age_groups_list if a in keep_age_groups]
    dates_list = np.unique(cities_epi['Date']).tolist()
    dates_list.sort(key=lambda x: 100*visu_fn.date_to_year_week(x)[0]+\
                                      visu_fn.date_to_year_week(x)[1])
    
    # Select data to display for cities on startup
    display_startup = 'Weekly'
    metric_startup = 'CaseRate'
#    age_group_startup = 'Overall'
    state_startup = 'TX'
    city_startup = 'State' # city_startup = 'Austin'
#    week_startup = dates_list[0]
    display_dict = {'Weekly':'Value','Cumulative':'CumulValue'}
    
    
    ## Get lists of possible selections
    state_list = list(state_to_cities.keys())
    cities_list = state_to_cities[state_startup]
    
    ## Dates to display
    dates_ = [dt.strptime(' '.join(map(str,visu_fn.date_to_year_week(x))) + ' 1',\
                                 "%Y %W %w") for x in dates_list]
    x_dates = [dates_ for x in age_groups_list]
    
    # Data to start
#    if display_startup == 'Weekly':
#        data_dict = all_rates
#    elif display_startup == 'Cumulative':
#        data_dict = all_cumul
#    y_startup = [list(data_dict[(metric_startup,a,state_startup,city_startup)].values())\
#                 for a in age_groups_list]
    
    # Starting data
    y_all_ages = visu_fn.select_data(states_epi,cities_epi,city_startup,
                             state=state_startup,metric=metric_startup).\
                             loc[:,['Age',display_dict[display_startup]]]
    y_startup = [list(visu_fn.df_filter(y_all_ages,cond_cols=[['Age','in',[a]]])\
                      [display_dict[display_startup]]) for a in age_groups_list]
    

    ## Create  graph
    min_y,max_y = [0],[np.max(y_startup)]
    xs = x_dates
    xs.extend([[dates_[:1]],[dates_[:1]]])
    y_startup.extend([min_y,max_y])
    legend_values = age_groups_list[:] + ['','']
    colors = (Category10[len(xs)-2])[0:len(xs)] +['#ffffff','#ffffff']
    source = ColumnDataSource(data=dict(
         x = xs,
         y = y_startup,
         color = colors,
         group = legend_values))
    TOOLS="pan,wheel_zoom,box_zoom,reset,save"
    p_ts = figure(plot_width=1000, plot_height=500,x_axis_type='datetime',
                title='', tools=TOOLS,)
    p_ts.multi_line(
         xs='x',
         ys='y',
         legend='group',
         source=source,
         line_color='color',
         line_width=2)
    p_ts.add_tools(HoverTool(show_arrow=True, line_policy='next', 
        tooltips=[('Group', '@group')]))
    p_ts.legend.location = 'top_left'#(0,290)
    
    # Y axis format
    if max_y[0] > 10:
        y_axis_format = '0,0'
    else:
        y_axis_format = '0.0'
    p_ts.yaxis.formatter=NumeralTickFormatter(format=y_axis_format)
    
    # X axis ticks
    epoch = dt.utcfromtimestamp(0)
    min_date = [dates_[0].month,dates_[0].year]
    max_date = [dates_[-1].month,dates_[-1].year]
#    ticks=[(dates_[i]-epoch).total_seconds() * 1000.0 for i in range(0,len(dates_),5)]
    ticks = [(datetime.datetime(m//12, m%12+1, 1)-epoch).total_seconds() * 1000.0 \
             for m in range(min_date[1]*12+min_date[0]-1, max_date[1]*12+max_date[0])]
    p_ts.xaxis.ticker = FixedTicker(ticks=ticks)
    p_ts.xgrid.ticker = FixedTicker(ticks=ticks)
    
    ## Define interaction controllers
    displays_list = ['Weekly','Cumulative']
    display_button = RadioButtonGroup(labels=displays_list, active=displays_list.index(display_startup))
    metrics_button = RadioButtonGroup(labels=metrics_list, active=metrics_list.index(metric_startup))
    state_button = RadioGroup(labels=state_list, active=state_list.index(state_startup))
    cities_button = RadioGroup(labels=cities_list, active=0)
    
    # Text above graph
    div_text_bar = '<b>' + city_startup + ' - ' + state_startup +  '</b>'
    div_bar = Div(text=div_text_bar,width=700, height=20)
    
    ###########################################################################
    def display_callback(attr, old, new, state_changed=False):
        # Get new selected value
        new_display = displays_list[display_button.active]
        new_metric = metrics_list[metrics_button.active]
        new_state = state_list[state_button.active]
        
        # If new state selected change list of cities
        if state_changed:
            cities_list = state_to_cities[new_state]
            cities_button.labels = cities_list
            cities_button.active = 0
            new_city = cities_list[0]
        else:
            cities_list = state_to_cities[new_state]
            new_city = cities_list[cities_button.active]
        
        # Update display data
#        if new_display == 'Weekly':
#            data_dict = all_rates
#        elif new_display == 'Cumulative':
#            data_dict = all_cumul
            
#        new_y = [list(data_dict[(new_metric,a,new_state,new_city)].values())\
#                 for a in age_groups_list]
        
        y_all_ages = visu_fn.select_data(states_epi,cities_epi,new_city,
                         state=new_state,metric=new_metric).\
                         loc[:,['Age',display_dict[new_display]]]
        new_y = [list(visu_fn.df_filter(y_all_ages,cond_cols=[['Age','in',[a]]])\
                          [display_dict[new_display]]) for a in age_groups_list]
        
        
        
        min_y,max_y = [0],[np.max(new_y)]
        new_y.extend([min_y,max_y])
        new_source = ColumnDataSource(data=dict(
              x = xs,
              y = new_y,
              color = colors,
              group = legend_values))
        source.data = new_source.data
        
        new_text =  '<b>' + new_city + ' - ' + new_state + '</b>'
        div_bar.text = new_text
        
        # Y axis format
        if max_y[0] > 10:
            y_axis_format = '0,0'
        else:
            y_axis_format = '0.0'
        p_ts.yaxis.formatter=NumeralTickFormatter(format=y_axis_format)
        
        return
    ###########################################################################
    # Update events
    display_button.on_change('active', partial(display_callback,state_changed=False))
    metrics_button.on_change('active', partial(display_callback,state_changed=False))
    state_button.on_change('active', partial(display_callback,state_changed=True))
    cities_button.on_change('active', partial(display_callback,state_changed=False))
    
    # Put controls in their own elements 
    controls = WidgetBox(row(Div(text='',width=50, height=5),display_button),
                         row(Div(text='',width=50, height=5),metrics_button))
    controls2 = WidgetBox(row(column(Div(text='<b>  State</b>',height=12),state_button,width=90),
                              column(Div(text='<b>    City</b>',height=12),cities_button,width=200)))
    	
    # Create a row layout
    layout = row(controls2,column(row(Div(text='',width=50, height=5),div_bar),controls,p_ts))
    
    ### Make a tab with the layout
    tab = Panel(child=layout, title = 'Single Location')
    return tab
###############################################################################

#
#
#
#import os
#from bokeh.models.widgets import Tabs#,RadioButtonGroup, Div
#from bokeh.io import curdoc
#
##folder_path = ['C:','Users','remyp','Research','CDC Flu Pandemic','Visualization','Data']
##folder = os.sep.join(folder_path)
##os.chdir(folder)
#import data_prep
##import visu_fn
##import tab_city_map
##import tab_state_map
#
#
#### Inputs
## Get data
#data_folder = os.sep.join([os.getcwd(),'Data'])
#cities_data, cities_epi, states_epi = data_prep.data_prep(data_folder)
#state_to_cities = data_prep.data_dict(cities_data, cities_epi, states_epi)
#
## State map
##tab_state_map_ = tab_state_map.map_tab(cities_data, states_epi)
##tab_city_map_ = tab_city_map.map_tab(cities_data, cities_epi)
##tab_ts_ = ts_tab(cities_data, cities_epi,states_epi)
#tab_ts_ = ts_tab(cities_data, cities_epi,states_epi,state_to_cities)
#
## Put all the tabs into one application
#tabs = Tabs(tabs = [tab_ts_])
#
## Put the tabs in the current document for display
#curdoc().add_root(tabs)
#curdoc().title = 'Influenza Pandemic Simulation'