# -*- coding: utf-8 -*-
import os
from bokeh.models.widgets import Tabs
from bokeh.io import curdoc

#folder_path = ['C:','Users','remyp','Research','CDC Flu Pandemic','Visualization','Data']
#folder = os.sep.join(folder_path)
#os.chdir(folder)
import data_prep
#import visu_fn
import tab_city_map
import tab_state_map
import tab_ts_single_loc
import tab_ts_single_group


### Inputs
# Get data
data_folder = os.sep.join([os.getcwd(),'Data'])
cities_data, cities_epi, states_epi = data_prep.data_prep(data_folder)
#state_to_cities, all_rates, all_cumul = data_prep.data_dict(cities_data, cities_epi, states_epi)
state_to_cities = data_prep.data_dict(cities_data, cities_epi, states_epi)


# State map
print('before state map')
tab_state_map_ = tab_state_map.map_tab(cities_data, states_epi)
print('before city map')
tab_city_map_ = tab_city_map.map_tab(cities_data, cities_epi)
print('before ts single loc')
tab_ts_single_loc_ = tab_ts_single_loc.ts_tab(cities_data, cities_epi,states_epi,
                                              state_to_cities)#, all_rates, all_cumul)
print('before ts single group')
tab_ts_single_group_ = tab_ts_single_group.ts_tab(cities_data, cities_epi,states_epi,
                                                  state_to_cities)#, all_rates, all_cumul)
print('before putting tabs together')
# Put all the tabs into one application
tabs = Tabs(tabs = [tab_city_map_,tab_state_map_,tab_ts_single_loc_,tab_ts_single_group_])

# Put the tabs in the current document for display
curdoc().add_root(tabs)
curdoc().title = 'Influenza Pandemic Simulation'


memory_stuff = False
if memory_stuff:
    # Memory of dataframes
    cities_data.memory_usage(deep=True).sum()
    states_epi.memory_usage(deep=True).sum()
    cities_epi.memory_usage(deep=True).sum()
    
    
    # Total memory used
    import psutil
    process = psutil.Process(os.getpid())
    print(process.memory_info().rss)  # in bytes 
    
    # Profiling
    from guppy import hpy
    hp=hpy()
    h = hp.heap()
    h.byrcs
    byrcs = h.byrcs
    byrcs[0].byid
    byrcs[0].byvia
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
    
    
    
    
    
    import sys
    from numbers import Number
    from collections import Set, Mapping, deque
    
    try: # Python 2
        zero_depth_bases = (basestring, Number, xrange, bytearray)
        iteritems = 'iteritems'
    except NameError: # Python 3
        zero_depth_bases = (str, bytes, Number, range, bytearray)
        iteritems = 'items'
    
    def getsize(obj_0):
        """Recursively iterate to sum size of object & members."""
        _seen_ids = set()
        def inner(obj):
            obj_id = id(obj)
            if obj_id in _seen_ids:
                return 0
            _seen_ids.add(obj_id)
            size = sys.getsizeof(obj)
            if isinstance(obj, zero_depth_bases):
                pass # bypass remaining control flow and return
            elif isinstance(obj, (tuple, list, Set, deque)):
                size += sum(inner(i) for i in obj)
            elif isinstance(obj, Mapping) or hasattr(obj, iteritems):
                size += sum(inner(k) + inner(v) for k, v in getattr(obj, iteritems)())
            # Check for custom object instances - may subclass above too
            if hasattr(obj, '__dict__'):
                size += inner(vars(obj))
            if hasattr(obj, '__slots__'): # can have __slots__ with __dict__
                size += sum(inner(getattr(obj, s)) for s in obj.__slots__ if hasattr(obj, s))
            return size
        return inner(obj_0)
    
    
    
    getsize(all_rates)
    getsize(all_cumul)
