# -*- coding: utf-8 -*-
"""
City level map
"""

import numpy as np
import visu_fn
from bokeh.sampledata.us_states import data as states
from bokeh.plotting import figure
from bokeh.models import Panel,LinearColorMapper,ColorBar#,GeoJSONDataSource
from bokeh.models import ColumnDataSource,Slider
#from bokeh.palettes import Viridis256#,brewer, Category20
from bokeh.models import NumeralTickFormatter#,HoverTool#,FixedTicker
# from bokeh.plotting import show as show_inline
from bokeh.models.widgets import RadioButtonGroup, Div
from bokeh.layouts import column,WidgetBox,row#,widgetbox
import matplotlib as plt
import matplotlib.cm as cm
import bokeh.models as bkm

###############################################################################
def map_tab(cities_data, cities_epi):#, states_epi):
    
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
    metric_startup = 'CaseRate'
    age_group_startup = 'Overall'
    week_startup = dates_list[0]
    
    
    ### State coordinates
    state_xs = [states[code]["lons"] for code in states if code not in['AK','HI']]
    state_ys = [states[code]["lats"] for code in states if code not in['AK','HI']]
    state_codes = [code for code in states if code not in['AK','HI']]
    # Alaska and Hawaii need to be adjusted
    AK_xs, AK_ys = visu_fn.states_adjust(states['AK']["lons"], states['AK']["lats"],'AK')
    HI_xs, HI_ys = visu_fn.states_adjust(states['HI']["lons"], states['HI']["lats"],'HI')
    state_xs.extend([AK_xs[:-1],HI_xs])
    state_ys.extend([AK_ys[:-1],HI_ys])
    state_codes.extend(['AK','HI'])
    
    
    ## Get corrected city coordinates
    cities_data = visu_fn.adjust_city_coords(cities_data)
    cities_epi.sort_values(by=['ID'],inplace=True) # needed to use all_rates dict
    
    ## Get all rates values in a dictionary
    all_rates = cities_epi.groupby(['Metric','Age','Date'])[['ID','Value']].\
        apply(lambda x: dict(x.values)).to_dict()

    
    ## Cities list and coordinates
    cities_id = list(all_rates[(metric_startup, age_group_startup, week_startup)].keys())
    city_xs = [cities_data.loc[cities_data['ID'] == x,'Longitude'].values[0] \
               for x in cities_id]
    city_ys = [cities_data.loc[cities_data['ID'] == x,'Latitude'].values[0] \
               for x in cities_id]
    city_names = [cities_data.loc[cities_data['ID'] == x,'City'].values[0] \
               for x in cities_id]
    city_states = [cities_data.loc[cities_data['ID'] == x,'State'].values[0] \
               for x in cities_id]
    
    # Select data to display for cities on startup
    startup_rates = list(all_rates[(metric_startup, age_group_startup, week_startup)].values())
    

    ## Create bokeh map source data
    # States
    col_source_states = ColumnDataSource(data = dict(xs=state_xs,
                                                     ys=state_ys,
                                                     State=state_codes))
    
    # Cities
    col_source_cities = ColumnDataSource(data = dict(xs=city_xs,
                                                     ys=city_ys,
                                                     w=[1.25]*len(city_xs),
                                                     h=[1]*len(city_xs),
                                                     State=city_states,
                                                     City=city_names,
                                                     Rate=startup_rates))
    
    ## Map formatting 
    low_val = 0 # for color bar in legend
    
    # Max value per metric, and formatter for color bar in legend
    max_vals = {}
    metrics_format = {}
    for m in metrics_list:
        m_vals = visu_fn.df_filter(cities_epi,cond_cols=[['Metric','in',[m]]])
        max_vals.update({m:np.percentile(m_vals['Value'],99.9) })
        if max_vals[m] > 10:
            m_format = NumeralTickFormatter(format=",0")
        else:
            m_format = NumeralTickFormatter(format="0.0")
        metrics_format.update({m:m_format})
        
        
    colormap = cm.get_cmap('OrRd') #choose any matplotlib colormap here
    bokehpalette = [plt.colors.rgb2hex(m) for m in colormap(np.arange(colormap.N))]
    #palette = Viridis256 # brewer["Spectral"][8] # Category20[20] # brewer["PRGn"][11]
    color_mapper = LinearColorMapper(palette = bokehpalette, low=low_val,high=max_vals[metric_startup])
    color_bar = ColorBar(color_mapper=color_mapper,width = 650, height = 20,
                         formatter = metrics_format[metric_startup],
                         border_line_color=None, orientation = 'horizontal',
                         location=(0, 0) )
    
    width = 900
    height = 550 # np.int(width*27/56)
    p = figure(title = 'Flu Pandemic in the United States', 
               plot_height = height , plot_width = width, 
               tools = "pan,wheel_zoom,box_zoom,reset", 
               toolbar_location = "left",
               x_range=(-140,-64), y_range=(23, 50))
    
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    
    #Add patch renderer to figure
    state_glyphs = bkm.glyphs.Patches(xs='xs',ys='ys',
              fill_color = 'white',
              line_color = 'grey', line_width = 1, line_alpha = 0.5, fill_alpha = 0.7)
    state_glyphs_renderer = p.add_glyph(source_or_glyph=col_source_states, glyph=state_glyphs)
    state_glyphs_hover = bkm.HoverTool(renderers=[state_glyphs_renderer],
                             tooltips=[('State', '@State')])
    p.add_tools(state_glyphs_hover)
    
    
    # City data
    city_glyphs = bkm.Ellipse(x='xs',y='ys', width="w", height="h",name='cities',
              fill_color = {'field' :'Rate', 'transform' : color_mapper},
              line_color = 'grey',# {'field' :'Rate', 'transform' : color_mapper},
              fill_alpha = 0.7, line_alpha=0.4)#, size = 14)
    city_glyphs_renderer = p.add_glyph(source_or_glyph=col_source_cities, glyph=city_glyphs)
    city_glyphs_hover = bkm.HoverTool(renderers=[city_glyphs_renderer],
                             tooltips=[('City','@City'),('Rate', '@Rate{0,0}')])
    p.add_tools(city_glyphs_hover)
    
    
    #Specify figure layout.
    p.add_layout(color_bar, 'below')
    
    ## Define interaction controllers
    week_slider = Slider(start=1, end=len(dates_list), value=1, step=1, title=None,width=700)
    metrics_button = RadioButtonGroup(labels=metrics_list, active=metrics_list.index(metric_startup))
    age_group_button = RadioButtonGroup(labels=age_groups_list, active=age_groups_list.index(age_group_startup))
    
    
    # Text above graph
    year,week = map(str,visu_fn.date_to_year_week(week_startup))
    div_text_bar = '<b>' + year + ' - Week: ' + week + '</b>'
    div_bar = Div(text=div_text_bar,width=700, height=20)
    
    ###########################################################################
    # Update function
    def display_callback(attr, old, new):
        # Get new score data to display
        new_week = dates_list[week_slider.value-1]
        new_metric = metrics_list[metrics_button.active]
        new_age_group = age_groups_list[age_group_button.active]
        
        # Legend color bar
        color_mapper.high = max_vals[new_metric]
        
        # Slider display value
        new_year,new_week_txt = map(str,visu_fn.date_to_year_week(new_week))
        new_text_bar = '<b>' + new_year + ' - Week: ' + new_week_txt + '</b>'
        div_bar.text = new_text_bar

        # Displayed data
        new_rates = list(all_rates[(new_metric, new_age_group, new_week)].values())
    
        # Patch source data with new rates and update legend
        col_source_cities.patch({'Rate': [(slice(len(new_rates)), new_rates)]})
        color_bar.formatter = metrics_format[new_metric]
    ###########################################################################
    
    
    # Update events
    week_slider.on_change('value', display_callback)
    metrics_button.on_change('active', display_callback)
    age_group_button.on_change('active', display_callback)

    # Figure formatting
    visu_fn.set_stype(p)
    
    # Put controls in a single element
    controls = WidgetBox(row(Div(text='',width=50, height=5),week_slider),
                         row(Div(text='',width=50, height=5),metrics_button),
                         row(Div(text='',width=50, height=5),age_group_button))
    	
    # Create a row layout
    layout = column(row(Div(text='',width=50, height=5),div_bar),controls,p)
    
    ### Make a tab with the layout
    tab = Panel(child=layout, title = 'City Map')
    return tab
###############################################################################