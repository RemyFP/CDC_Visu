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
from bokeh.models.widgets import RadioButtonGroup, Div, RadioGroup, CheckboxGroup
from bokeh.layouts import column,WidgetBox,row#,widgetbox
#import matplotlib as plt
#import matplotlib.cm as cm
# itertools handles the cycling

from bokeh.palettes import Category20#,brewer, Category10, Viridis256
#from bokeh.models import FixedTicker#,HoverTool#,NumeralTickFormatter
#from bokeh.io import curdoc
from datetime import datetime as dt

###############################################################################
###############################################################################
def ts_tab(cities_data, cities_epi,states_epi):
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
    age_group_startup = 'Overall'
    state_startup = 'TX'
    city_startup = 'State' # city_startup = 'Austin'
#    week_startup = dates_list[0]
    # List of locations to display
    to_display = [[city_startup,state_startup]]
    selected = [city_startup + ' - ' + state_startup]
#    selected_id = [[x[:-4],x[-2:]] for x in selected]
    
    
    ### Get list of cities per state
    state_to_cities = {}
    for s in np.unique(cities_data['StateCode']):
        df_s = visu_fn.df_filter(cities_data,cond_cols=[['StateCode','in',[s]]])
        cities_s = np.unique(df_s['City']).tolist()
        state_to_cities.update({s:['State'] + cities_s})
    
    ## Get all data in a single dataframe
    states_epi.loc[:,'City'] = 'State'
    keep_cols = ['Date','StateCode','Year','Week','Metric','Age','City','Value']
    all_epi = states_epi[keep_cols].append(cities_epi[keep_cols],ignore_index=True)
    all_epi.sort_values(by=['Year','Week'],inplace=True) # needed to use all_rates dict
    
    # Get cumulative data
    rates_cumul = all_epi.loc[:,['Metric','Age','StateCode','City','Date','Value']].copy()
    rates_cumul.loc[:,'Value'] = rates_cumul.groupby(['Metric','Age','StateCode','City'])['Value'].cumsum()
    
    
    ## Get all rates values in a dictionary
    all_rates = all_epi.groupby(['Metric','Age','StateCode','City'])[['Date','Value']].\
        apply(lambda x: dict(x.values)).to_dict()
    all_cumul = rates_cumul.groupby(['Metric','Age','StateCode','City'])[['Date','Value']].\
        apply(lambda x: dict(x.values)).to_dict()


    ## Get lists of possible selections
    state_list = list(state_to_cities.keys())
    cities_list = state_to_cities[state_startup]
    
    
    ## Data to start
    if display_startup == 'Weekly':
        data_dict = all_rates
    elif display_startup == 'Cumulative':
        data_dict = all_cumul
    y_startup = [list(data_dict[(metric_startup,age_group_startup,
                                 to_display[0][1],to_display[0][0])].values())]
    
    ## Dates to display
    dates_ = [dt.strptime(' '.join(map(str,visu_fn.date_to_year_week(x))) + ' 1',\
                                 "%Y %W %w") for x in dates_list]
    x_dates = [dates_ for i in range(len(y_startup))]
    
    # Color palette
    color_palette = Category20[20]
    
    ## Create  graph
    min_y,max_y = [0],[np.max(y_startup)]
    xs = x_dates
    xs.extend([[dates_[:1]],[dates_[:1]]])
    y_startup.extend([min_y,max_y])
    legend_values = selected + ['','']
    
    colors = []
    for i in range(len(xs) -2):
        colors.append(color_palette[i % 20])
    colors.extend(['#ffffff','#ffffff'])

#    colors = (Category10[len(xs)-2])[0:len(xs)] +['#ffffff','#ffffff']
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
    
    ## Define interaction controllers
    displays_list = ['Weekly','Cumulative']
    display_button = RadioButtonGroup(labels=displays_list, active=displays_list.index(display_startup))
    metrics_button = RadioButtonGroup(labels=metrics_list, active=metrics_list.index(metric_startup))
    age_group_button = RadioButtonGroup(labels=age_groups_list, active=age_groups_list.index(age_group_startup))
    state_button = RadioGroup(labels=state_list, active=state_list.index(state_startup))
    cities_button = CheckboxGroup(labels=cities_list, active=[0])
    selected_button = CheckboxGroup(labels=selected, active=list(range(len(selected))))
    
    # Text above graph
    div_text_bar = ''# '<b>' + city_startup + ' - ' + state_startup +  '</b>'
    div_bar = Div(text=div_text_bar,width=700, height=20)
    
    ###########################################################################
    def new_state_callback(attr, old, new):
        # Get new selected value
        new_state = state_list[state_button.active]
        selected = list(selected_button.labels)
        
        ## Selected cities to display in that state
        # List of cities, and the ones to display
        cities_list = state_to_cities[new_state]
        active_ = [i for i in range(len(cities_list)) if 
                   (cities_list[i] + ' - ' + new_state) in selected]
        # Update the check box for cities
        cities_button.labels = []
        cities_button.active = []
        cities_button.labels = cities_list
        cities_button.active = active_
        
        return
    ###########################################################################
    def selected_callback(attr, old, new):
        # Update checkbox of selected cities to display
        selected = list(selected_button.labels)
        active_ = list(selected_button.active)
        new_selected = [selected[i] for i in active_]
        selected_button.active = list(range(len(new_selected)))
        selected_button.labels = new_selected
        return
    ###########################################################################
    def city_callback(attr, old, new):
        # List of cities checked may have changed
        if len(cities_button.labels) > 0:
            change = False
            selected = list(selected_button.labels)
            new_state = state_list[state_button.active]
            cities_list = list(cities_button.labels)
            
            new_city = [cities_list[i] for i in cities_button.active if 
                        (cities_list[i] + ' - ' + new_state) not in selected]
            
            if len(new_city) > 0:
                # New city added
                selected.append(new_city[0] + ' - ' + new_state)
                change = True
            
            else: # city was removed
                removed_c = [cities_list[i] for i in range(len(cities_list)) if \
                             (i not in cities_button.active) and \
                             (cities_list[i] + ' - ' + new_state) in selected]
                if len(removed_c) > 0:
                    selected.remove(removed_c[0] + ' - ' + new_state)
                    change = True
            
            if change: # Actually need to modify selected list
                selected_button.labels = selected
                selected_button.active = list(range(len(selected)))
        
        return
    ###########################################################################
    def graph_callback(attr, old, new):
        # Get list of data to display
        new_display = displays_list[display_button.active]
        new_metric = metrics_list[metrics_button.active]
        new_age_group = age_groups_list[age_group_button.active]
        selected = list(selected_button.labels)
        
        # Update display data
        if new_display == 'Weekly':
            data_dict = all_rates
        elif new_display == 'Cumulative':
            data_dict = all_cumul
            
        # Pairs containing city and state
        selected_id = [[x[:-5],x[-2:]] for x in selected]
        
        if len(selected_id) > 0:
            new_y = [list(data_dict[(new_metric,new_age_group,x[1],x[0])].values())
                 for x in selected_id]
            x_dates = [dates_ for i in range(len(new_y))]
            min_y,max_y = [0],[np.max(new_y)]
            
            colors = []
            for i in range(len(x_dates)):
                colors.append(color_palette[i % 20])
            
            legend_values = selected + ['','']
        else:
            x_dates = [dates_]
            new_y = [0]*len(dates_)
            min_y,max_y = [0],[1]
            colors = ['#ffffff']
            legend_values = ['','','']
            
        new_y.extend([min_y,max_y])
        xs = x_dates
        xs.extend([[dates_[:1]],[dates_[:1]]])
        colors.extend(['#ffffff','#ffffff'])
        
        new_source = ColumnDataSource(data=dict(
              x = xs,
              y = new_y,
              color = colors,
              group = legend_values))
        source.data = new_source.data
        
        new_text = ''# '|'.join(selected_button.labels)# '<b>' + new_city + ' - ' + new_state + '</b>'
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
    display_button.on_change('active',graph_callback)
    metrics_button.on_change('active',graph_callback)
    age_group_button.on_change('active',graph_callback)
    
    state_button.on_change('active',new_state_callback)
    
    cities_button.on_change('active',city_callback)
    
    selected_button.on_change('active',selected_callback)
    selected_button.on_change('active',graph_callback)
    
    # Put controls in their own elements 
    controls = WidgetBox(row(Div(text='',width=50, height=5),display_button),
                         row(Div(text='',width=50, height=5),metrics_button),
                         row(Div(text='',width=50, height=5),age_group_button))
    controls2 = WidgetBox(row(column(Div(text='<b>  State</b>',height=12),state_button,width=90),
                              column(Div(text='<b>    City</b>',height=12),cities_button,width=200),
                              column(Div(text='<b>    Selected</b>',height=12),selected_button,width=280)))
    	
    # Create a row layout
    layout = row(controls2,column(row(Div(text='',width=50, height=5),div_bar),controls,p_ts))
    
    ### Make a tab with the layout
    tab = Panel(child=layout, title = 'Single Group')
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
#
## State map
##tab_state_map_ = tab_state_map.map_tab(cities_data, states_epi)
##tab_city_map_ = tab_city_map.map_tab(cities_data, cities_epi)
#tab_ts_ = ts_tab(cities_data, cities_epi,states_epi)
#
## Put all the tabs into one application
#tabs = Tabs(tabs = [tab_ts_])
#
## Put the tabs in the current document for display
#curdoc().add_root(tabs)
#curdoc().title = 'Influenza Pandemic Simulation'