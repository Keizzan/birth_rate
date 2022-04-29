"""
##############################################################################
#######                 PROJECT NAME : Birth rate in Surrey            #######
##############################################################################
                                Synopsis:
Script read csv file, validates its records and plots bar chart for yearly birth rate in Surrey
"""
### Import required libraries
import pandas as pd
import matplotlib.pyplot as plt
from pandas_schema import Column, Schema
from pandas_schema.validation import CustomElementValidation, InRangeValidation, InListValidation
import numpy as np


### Import dataframe from .csv file
data = pd.read_csv('Birth rate.csv')

### Update dataframe - only desired columns
data = data[['Region','Time Period', 'Birth rate - Total number of births']]

### Custom validation function for integer
def int_check(num):
    try:
        int(num)
    except ValueError:
        return False
    return True

### Custom validators for pandas_schema's Schema
### integer
int_validation = [CustomElementValidation(lambda i: int_check(i),'is not integer')]
null_validation = [CustomElementValidation(lambda a: a is not np.nan, 'cannot be empty')]
### list of allowed data points
town_list = ['Elmbridge','Epsom and Ewell','Guildford','Mole Valley','Reigate and Banstead','Runnymede','Spelthorne','Surrey Heath','Tandridge','Waverley','Woking']


### Schema for validation dataframe
schema = Schema([
    ### Validate if cell contain one of the values from town_list
    Column('Region',[InListValidation(town_list)]),
    ### Validate if cell value is within range 2010-2018 and if cell is not empty
    Column('Time Period',[InRangeValidation(2010,2019)]+null_validation),
    ### Validate for integer and null values
    Column('Birth rate - Total number of births', int_validation+null_validation)
])

### Validate and find errors in dataframe based on prepared Schema
errors = schema.validate(data)
errors_index_rows = [e.row for e in errors]

### Isolate valid data and create new dataframe
data_clean = data.drop(index=errors_index_rows)

### Create new files with clean data and errors from original dataframe
pd.DataFrame({'Errors':errors}).to_csv('output/errors.csv')
data_clean.to_csv('output/clean_data.csv')


### Convert to MultiIndex dataframe, based on birth rate,
### Flatten dataframe and validate for any NaN values
data_final = data_clean.groupby(['Time Period','Region']).sum().unstack().dropna()

### Convert Birth rate from object type as integer
data_final['Birth rate - Total number of births'] = data_final['Birth rate - Total number of births'].astype(int)

### Retrieve amount of erros
err = pd.read_csv('output/errors.csv')['Errors'].shape[0]


### Plotting
data_final.plot.bar(figsize=(35,15))
plt.title('Birth Rate', loc='left')
plt.figtext(0.5,0.01, f"Errors: {err}", ha='center')
plt.show()



