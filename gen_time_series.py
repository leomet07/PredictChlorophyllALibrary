"""

X-axis: 2013-now
Make everything bigger
Add a legend


"""

from datetime import datetime as dt
from datetime import timedelta
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from scipy import stats
import seaborn as sns
import geopandas as gpd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import sys
import os

# Params:
#   lake = String - name of lake you want to generate a time series for
#   csv = String - path to csv containing predictions, observed values, date
def plot_observed_vs_predicted(df, lake, out_path):
    df.head()
    # get stuff we care about... i.e., specific lake, observations, predictions, and the date
    columns = ['Site','Observed_Chla', 'Predicted_Chla', 'Date']
    df = df[columns]
    df = df.loc[df['Site'].isin([lake])]
    df['Date'] = pd.to_datetime(df['Date'])

    # plot params
    plt.figure(figsize=(12, 6)) 
    plt.scatter(df['Date'], df['Predicted_Chla'], marker='x', label='Predicted')
    plt.scatter(df['Date'], df['Observed_Chla'], marker='o', label='Observed')

    # label the axes
    plt.xlabel('Date (Month-Year)', fontsize=14)  
    plt.ylabel('Chl-a: Predicted vs Observed (µg/L)', fontsize=14)  
    plt.title(f'Observed vs Predicted Chlorophyll-a Concentrations for {lake.title()}', fontsize=16)  

    # format the x-axis to show month and year from earliest in-situ observations (2013)
    # and skip every 2nd month
    plt.xlim(pd.to_datetime('2013-01-01'), pd.to_datetime('2022-12-31'))
    x_axis = plt.gca().xaxis
    x_axis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%b-%Y'))
    x_axis.set_major_locator(plt.matplotlib.dates.MonthLocator(interval=5))

    plt.xticks(rotation=45)
    plt.legend(loc="lower right", fontsize=12)
    
    if not os.path.exists(out_path): 
        os.makedirs(out_path) 

    lake_name = lake.title().replace(' ', '')
    file_path = os.path.join(out_path, f"{lake_name}_time_series.png") 
    
    plt.savefig(file_path)
    plt.close()

def generate_time_series_all_lakes(csv_path, out_path):
    # read the csv
    df = pd.read_csv(csv_path)

    # get the unique lake names
    unique_lakes = df['Site'].unique()
    print(f"Number of unique lakes: ", len(unique_lakes))

    # for every single lake we have, generate a time series
    for lake in unique_lakes:
        plot_observed_vs_predicted(df, lake, out_path)
        print(f"Saved %s successfully", lake)



if __name__ == "__main__":

    # Arguments: 
    # csv_path: the path to the csv with predictions/observations.
    # out_folder_name: the folder where you want to save this time series to.
    #                   doesn't need to exist, program will make a new one.


    if len(sys.argv) != 3:
        print(
            "python export_raster.py <csv_path> <out_folder_name>"
        )
        sys.exit(1)

    csv_path = sys.argv[1]
    out_folder = sys.argv[2]
    
    generate_time_series_all_lakes(
        csv_path,
        out_folder
    )