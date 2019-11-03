# -*- coding: utf-8 -*-
"""
Prepares data to be used for the flu pandemic visualization
"""

import os
import numpy as np
import pandas as pd
import visu_fn

np.set_printoptions(linewidth=130)
pd.set_option('display.width', 130)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.options.display.float_format = '{:,.8f}'.format
pd.set_option('precision', -1)

###############################################################################
###############################################################################
def df_type_optimize(df,category_cols=[],downcast_nb=False,ignore_cols=[]):
    """ category_cols: list of columns to convert into categories
        downcast_nb: whether to downcast number columns that are not in
    category_cols
        ignore_cols: any column that should not be modified
        Transforms columns of a dataframe into a category if passed as input, 
    otherwise number columns are downcast
    """
#    df = cities_epi.copy()
    if len(category_cols) > 0:
        for c in category_cols:
            if (c in  df.columns) and (c not in ignore_cols):
                df.loc[:,c] = df[c].astype('category')
    
    if downcast_nb:
        for c in df.columns:
            if (c not in category_cols) and (c not in ignore_cols):
                if df[c].dtype == 'int64':
                    df.loc[:,c] = df[c].apply(pd.to_numeric,downcast='unsigned')
                elif df[c].dtype == 'float64':
                    df.loc[:,c] = df[c].apply(pd.to_numeric,downcast='float')
    
    return df
###############################################################################
# Check dataframe memory usage
#cities_epi.memory_usage(deep=True).sum()
## To open csv with specified format for columns
#dtypes = optimized_gl.drop('date',axis=1).dtypes
#dtypes_col = dtypes.index
#dtypes_type = [i.name for i in dtypes.values]
#column_types = dict(zip(dtypes_col, dtypes_type))
#read_and_optimized = pd.read_csv('game_logs.csv',dtype=column_types,parse_dates=['date'],infer_datetime_format=True)
#read_and_optimized_xl = pd.read_excel('game_logs.csv',dtype=column_types,parse_dates=['date'])
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
    states_epi = states_epi.loc[states_epi['State'] != 'Entire Network',:]
    
    # Optimize column types
    states_epi = df_type_optimize(states_epi,category_cols=states_epi.columns,
                                  ignore_cols=['Value'])
    print('before cities_epi')
    # Set case rates in each city equal to the state numbers
    cities_epi = cities_data.loc[:,['ID','State','City']]
    cities_epi = pd.merge(cities_epi,states_epi,left_on='State',right_on='State',how='left')
    
    # Optimize column types
    cities_epi = df_type_optimize(cities_epi,category_cols=cities_epi.columns,
                                  ignore_cols=['Value'])
    
    # Replace NAs by zero
    cities_epi.fillna({'Value':0},inplace=True)
    states_epi.fillna({'Value':0},inplace=True)
    
    # Order dataframes
    states_epi.sort_values(by=['StateCode','Year','Week'],inplace=True)
    cities_epi.sort_values(by=['ID','Year','Week'],inplace=True)
    
    # Remove columns not used
    state_cols = ['Date','StateCode','Metric','Age','Value']
    cities_cols = ['Date','StateCode','Metric','Age','City','Value']
    states_epi = states_epi.loc[:,state_cols]
    cities_epi = cities_epi.loc[:,cities_cols]
    
     ## Cumulative data
     # States
    states_epi.loc[:,'CumulValue'] = states_epi.groupby(['Metric','Age','StateCode'])['Value'].cumsum()
    # Cities
    cities_epi.loc[:,'CumulValue'] = cities_epi.groupby(['Metric','Age','StateCode','City'])['Value'].cumsum()
    
    return cities_data, cities_epi, states_epi
###############################################################################
def data_dict(cities_data, cities_epi, states_epi):
    ### Get list of cities per state
    state_to_cities = {}
    for s in np.unique(cities_data['StateCode']):
        df_s = visu_fn.df_filter(cities_data,cond_cols=[['StateCode','in',[s]]])
        cities_s = np.unique(df_s['City']).tolist()
        state_to_cities.update({s:['State'] + cities_s})
#    print('before all rates in dict')
#    ## Get all data in a single dataframe
#    states_epi.loc[:,'City'] = 'State'
#    keep_cols = ['Date','StateCode','Year','Week','Metric','Age','City','Value']
#    all_epi = states_epi[keep_cols].append(cities_epi[keep_cols],ignore_index=True)
#    all_epi.sort_values(by=['Year','Week'],inplace=True) # needed to use all_rates dict
#    
#    # Get all rates values in a dictionary
#    all_rates = all_epi.groupby(['Metric','Age','StateCode','City'])[['Date','Value']].\
#        apply(lambda x: dict(x.values)).to_dict()
#    print('before cumulative dict')
#    ## Cumulative data
#    rates_cumul = all_epi.loc[:,['Metric','Age','StateCode','City','Date','Value']]
#    rates_cumul.loc[:,'Value'] = rates_cumul.groupby(['Metric','Age','StateCode','City'])['Value'].cumsum()
#    
#    # Get all rates values in a dictionary
#    all_cumul = rates_cumul.groupby(['Metric','Age','StateCode','City'])[['Date','Value']].\
#        apply(lambda x: dict(x.values)).to_dict()
#    print('after cumulative dict')
    return state_to_cities#, all_rates, all_cumul
###############################################################################