import pandas as pd
import os

def load_data(file_path):

    return pd.read_excel(file_path)

def transpose_table(df):
    df_transposed = df.melt(id_vars=['MPAN', 'Date'], var_name='Hour', value_name='Value')

    df_transposed['Hour'] = pd.to_datetime(df_transposed['Hour'], format='%H:%M').dt.time
    df_transposed['Week'] = pd.to_datetime(df_transposed['Date']).dt.isocalendar().week

    return df_transposed

def calculate_statistics(df_transposed):
    return df_transposed.groupby(['MPAN', 'Week']).agg({'Value': ['mean', 'max', 'min']}).reset_index()

def save_results(result, output_path_template=
                 'results_second_task/result_{}.xlsx'):
    os.makedirs('results_second_task', exist_ok = True)
    mpans = result['MPAN'].unique()
    for mpan in mpans:
        mpan_result = result[result['MPAN'] == mpan]
        mpan_result.columns = [' '.join(col).strip() for col in mpan_result.columns.values]
        mpan_result.to_excel(output_path_template.format(mpan), index=False)

def main():

    data = load_data('interval_data.xlsx')

    transposed_data = transpose_table(data)

    result_data = calculate_statistics(transposed_data)

    save_results(result_data)

    print("Results saved in results_second_task folder")

if __name__ == "__main__":
    main()