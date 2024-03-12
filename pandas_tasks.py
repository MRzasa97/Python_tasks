import pandas as pandas
import numpy as numpy
from datetime import datetime, timedelta
from dateutil.parser import parse
import os
import sys

def load_and_merge_csv_files(file_pattern):
    print(file_pattern)
    files = [file for file in os.listdir() if file.startswith(file_pattern)]
    dataframes = []
    for file in files:
        try:
            if file.endswith('.csv'):
                dataframes.append(pandas.read_csv(file, encoding='ISO-8859-1'))
            elif file.endswith('.xlsx'):
                dataframes.append(pandas.read_excel(file))
        except Exception as e:
            print(f"Error reading file {file}: {e}")
    
    return pandas.concat(dataframes, ignore_index=True)

def drop_duplicate_rows(dataframe):
    return dataframe.drop_duplicates()

def show_null_values(dataframe):
    print(f"Null values in the dataframe: \n{dataframe.isnull().sum()}")

def fill_null_values(dataframe, value=1337):
    dataframe.fillna(value=value, inplace=True)

def calculate_days_difference(dataframe):
    date_formats = ['%m/%d/%Y', '%d/%m/%Y']
    for format in date_formats:
        try:
            dataframe['Date'] = pandas.to_datetime(dataframe['Date'], format=format)
            dataframe['Acctg Date'] = pandas.to_datetime(dataframe['Acctg Date'], format=format)
            break
        except ValueError:
            print(f"Failed to parse dates with format {format}")
            continue

    dataframe['Days_Difference'] = (dataframe['Acctg Date'] - dataframe['Date']).dt.days

def calculate_business_days_difference(dataframe):
    uk_bank_holidays_2019 = ['2019-01-01', '2019-04-19', '2019-04-22', '2019-05-06', '2019-05-27', '2019-08-26', '2019-12-25', '2019-12-26']
    uk_bank_holidays_2020 = ['2020-01-01', '2020-04-10', '2020-04-13', '2020-05-08', '2020-05-25', '2020-08-31', '2020-12-25', '2020-12-28']

    uk_bank_holidays = uk_bank_holidays_2019 + uk_bank_holidays_2020

    valid_rows = dataframe['Acctg Date'].notnull() & dataframe['Date'].notnull()

    dataframe.loc[valid_rows, 'Business_Days_Difference'] = numpy.busday_count(
        dataframe.loc[valid_rows, 'Date'].values.astype('datetime64[D]'), 
        dataframe.loc[valid_rows, 'Acctg Date'].values.astype('datetime64[D]'),
        weekmask='1111100', holidays=uk_bank_holidays
    )
def  convert_amount_to_pln(dataframe, fx_rates):
    data = pandas.merge(dataframe, fx_rates, on='Currency', how='left')
    data['Amount_PLN'] = data['Amount'] / data['Per USD'] * fx_rates.loc[fx_rates['Currency'] == 'PLN', 'Per USD'].values[0]
    return data

def create_and_save_files(dataframe, output_folder='results'):
    os.makedirs(output_folder, exist_ok=True)
    for type_value, group in dataframe.groupby('Type'):
        output_file = os.path.join(output_folder, f"{type_value}.xlsx")
        
        with pandas.ExcelWriter(output_file, engine='xlsxwriter', date_format='dd/mm/yyyy', datetime_format='dd/mm/yyyy') as writer:
            group.to_excel(writer, sheet_name='Sheet1', index=False)

def main():
    numpy.set_printoptions(threshold=sys.maxsize)
    merged_data = load_and_merge_csv_files('Table_1')
    merged_data = drop_duplicate_rows(merged_data)
    show_null_values(merged_data)
    fill_null_values(merged_data)
    calculate_days_difference(merged_data)
    calculate_business_days_difference(merged_data)
    fx_rates = pandas.read_csv('FXrates.csv')
    merged_data = convert_amount_to_pln(merged_data, fx_rates)
    create_and_save_files(merged_data)
    print("Results saved in results folder")

if __name__ == "__main__":
    main()