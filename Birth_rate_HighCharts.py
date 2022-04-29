"""
##############################################################################
#######                 PROJECT NAME : Birth rate in Surrey            #######
##############################################################################
                                Synopsis:
Script which plots interactive horizontal bar/ bar/ spline and line charts 
represeting birth rate in recent years for each region in Surrey
"""
### Import required libraries
import pandas as pd
from pandas_schema import Column, Schema
from pandas_schema.validation import CustomElementValidation, InRangeValidation, InListValidation
import numpy as np
import justpy as jp


### Import data from .csv files and create dataframes
data1 = pd.read_csv('Birth rate.csv')
data2 = pd.read_csv('Deaths by area of usual residence.csv')
### Merge dataframes based on 2 rows, and drop all non-matching data
data = data1.merge(data2, how = 'inner', left_on=['Region', 'Time Period'], right_on=['Region','Year'])
### Create new column with difference from number of births - deaths in same area
data['Birth rate'] = data['Birth rate - Total number of births'] - data['All deaths by area of usual residence']

### Update dataframe - only desired columns
data = data[['Region','Year', 'Birth rate']]

### Custom validation function for integer
def int_check(num):
    """
    Parameneters:
        num { any }
    Return
        Bool
    """
    try:
        int(num)
    except ValueError:
        return False
    return True

### Custom validators for pandas_schema's Schema
### integer
int_validation = [CustomElementValidation(lambda i: int_check(i),'is not integer')]
### null check
null_validation = [CustomElementValidation(lambda a: a is not np.nan, 'cannot be empty')]
### list of allowed data points
town_list = ['Elmbridge','Epsom and Ewell','Guildford','Mole Valley','Reigate and Banstead','Runnymede','Spelthorne','Surrey Heath','Tandridge','Waverley','Woking']


### Schema for validation dataframe
schema = Schema([
    ### Validate if cell contain one of the values from town_list
    Column('Region',[InListValidation(town_list)]),
    ### Validate if cell value is within range 2010-2018 and if cell is not empty
    Column('Year',[InRangeValidation(2010,2019)]+null_validation),
    ### Validate for integer and null values
    Column('Birth rate', int_validation+null_validation)
])

### Validate and find errors in dataframe based on prepared Schema
errors = schema.validate(data)
errors_index_rows = [e.row for e in errors]

### Isolate valid data and create new dataframe
data_clean = data.drop(index=errors_index_rows)

### Create new files with clean data and errors from original dataframe
pd.DataFrame({'Errors':errors}).to_csv('errors.csv')
data_clean.to_csv('clean_data.csv')


### Convert to MultiIndex dataframe, based on birth rate,
### Flatten dataframe and validate for any NaN values
data_final = data_clean.groupby(['Year','Region']).sum().unstack().dropna()

### Convert Birth rate from object type as integer
data_final['Birth rate'] = data_final['Birth rate'].astype(int)


### Extracting amount of found errors
error_count = pd.read_csv('errors.csv').shape[0]



### HighChart javascript object
chart_def = """
{
        chart: {
            type: 'bar'
        },
        title: {
            text: 'Chart of Type Bar'
        },
        xAxis: {
            categories: []
        },
        yAxis: {
            title: {
                text: ''
            }
        },
        series: []
}
"""


### Function - button change of chart types
def button_change(self, _):
    self.chart.options.chart.type = self.value
    self.chart.options.title.text = f'Chart of Type {self.value}'


### JustPy page
def app():
    ### Defining list of aviable types of chart
    chart_type = ['bar', 'column', 'line', 'spline']
    ### Webpage build in Quasar framework
    wp = jp.QuasarPage()
    ### Adding content to page
    h1 = jp.QDiv(a=wp, text='Birth Rate Analysis', classes='text-h3 text-center q-pa-md')
    ### Adding content to page
    p1 = jp.QDiv(a=wp, text=f'Removed data rows: {error_count}', classes='text-p1 text-center q-pa-md')
    ### Adding Quasar buttons to page
    hc = jp.QBtnToggle(toggle_color='red', push=True, glossy=True, a=wp, input=button_change, value='bar', classes='q-ma-md')
    ### One button for each item in the list chart_type
    for type in chart_type:
        hc.options.append({'label': type.capitalize(), 'value': type})

    ### Loading chart javascript object in JustPy page
    hc.chart = jp.HighCharts(a=wp, classes='q-ma-lg', options=chart_def)
    ### Defining x axis as index of dataframe
    hc.chart.options.xAxis.categories = list(data_final.index)
    ### Defining y axis title
    hc.chart.options.yAxis.title.text = 'Birth rate'
    ### Looping through columns to retrieve data needed to plot
    ### and assinging it to series in javascript object of Highcharts
    hc_data = [{'name': v1, 'data':[ v2 for v2 in data_final[v1]]} for v1 in data_final.columns]
    hc.chart.options.series = hc_data



    ### Return JustPy webpage
    return wp

### Run JustPy
jp.justpy(app)
