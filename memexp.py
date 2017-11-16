from matplotlib import pyplot as plt
from sys import argv
import pandas as pd
import numpy as np
import os
import argparse
from utils import static_var


def to_normal_csv(_processed_data_path, _data_path, split_packs=False,
                  disgusting_decimal_sign=',', disgusting_separator=';'):
    with open(_processed_data_path, 'w') as proc, open(_data_path, 'r') as data:
        prev_time = 0
        time_summand = 0
        time_step = 2e-4
        package_num = 1
        file = None
        for line in data:
            processed_line = line.replace(disgusting_decimal_sign, '.').replace(disgusting_separator, ',')+'\n'
            time, voltage, current = processed_line.split(',')
            if float(time) == 0.0:
                time_summand = prev_time + time_step
                if args.split_packs:
                    if file:
                        file.close()
                        package_num += 1
                    file = open(os.path.join(raw_packs, 'pack_'+str(package_num)+'.csv'), 'w')
                time = '{:10.4f}'.format(time_summand)
            else:
                time = '{:10.4f}'.format(float(time)+time_summand)
            if split_packs:
                file.write(processed_line+'\n')
            prev_time = float(time)
            current = str(float(current)/1.8)
            processed_line = ','.join((time, voltage, current))
            proc.write(processed_line+'\n')
        if split_packs:
            file.close()


def concat_diff(df, external_df, merge_by):
    if merge_by not in df.columns or merge_by not in external_df.columns:
        raise ValueError('Column '+merge_by+' does not exist')
    columns = [x for x in external_df.columns if x != merge_by and x not in df.columns]
    for column in columns:
        df[column] = external_df[external_df[merge_by].isin(df[merge_by])][column]
    return df


def df_filter(df, **col_cond):
    filtered = df
    if col_cond:
        for key, val in col_cond:
            filtered = filtered[col_cond[key](filtered[key])]
    return filtered


def df_add_col(df, col_name, *based_on_cols, action=lambda *args: max(args), default_val=0):
    if not based_on_cols:
        df[col_name] = default_val
        return df
    columns = []
    for column in based_on_cols:
        columns.append(np.asarray(df[column]))
    column = []
    for row in zip(*columns):
        column.append(action(*row))
    df[col_name] = column
    return df


def plot(df, axis_y, ymunit, ylim=(-0.3, 100), axis_x='Time', xmunit='sec', shape='b-',
         fig=1, figsize=(80, 40), subplot=111, file_name=None):
    plt.figure(fig, figsize=figsize)
    plt.subplot(subplot)
    plt.plot(df[axis_x], df[axis_y], shape)
    plt.title(axis_y)
    plt.xlabel(axis_x+', '+xmunit)
    plt.ylabel(axis_y+', '+ymunit)
    plt.ylim(ylim[0], ylim[1])
    plt.legend()
    plt.savefig(os.path.join(result_plot_path, (file_name if file_name else axis_y)+'.png'))

if __name__ == '__main__':
    meas_dir = 'meas'
    read_val = -5

    parser = argparse.ArgumentParser()
    parser.add_argument('data_path', type=str, help='Specifies a source data location')
    parser.add_argument('data_dir_name', type=str, help='Specifies a results storage location')
    parser.add_argument('--external_csv', type=str, nargs='?', default=None,
                        help='Specifies external source to concatenate (excluding share columns)')
    parser.add_argument('--concat_by', type=str, nargs='?', require='--external_csv' in argv, default='Time',
                        help='Specifies a share column to restrict rows count.'
                             '\nRequires --external_csv option to be specified')
    parser.add_argument('--split_packs', action='store_true',
                        help='Enables splitting of source data into individual packs (based on time)')
    parser.add_argument('--normal_csv', action='store_true',
                        help='Indicates converting source data to normal csv format as unnecessary.')
    parser.add_argument('--rep_separator', type=str, require='--normal_csv' not in argv, default=';',
                        help='Specifies a target disgusting separator which must be replaced!'
                             '\nCannot be specified with --normal_csv option.')
    parser.add_argument('--rep_decimal_sign', type=str, require='--normal_csv' not in argv, default=',',
                        help='Specifies a target disgusting decimal sign separator which must be replaced!'
                             '\nCannot be specified with --normal_csv option.')

    args = parser.parse_args()

    if not os.path.isfile(args.data_path) or not os.path.exists(args.data_path):
        parser.error('Either '+args.data_path+' is not file or it does not exist.')

    data_path = args.data_path

    if not os.path.exists(meas_dir):
        os.makedirs(meas_dir)

    data_dir = os.path.join(meas_dir, args.data_dir_name)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    narmal_csv_path = os.path.join(data_dir, 'Processed.csv')
    result_plot_path = os.path.join(data_dir, 'results')
    if not os.path.exists(result_plot_path):
        os.makedirs(result_plot_path)

    packages_directory = os.path.join(data_dir, 'packs')
    if not os.path.exists(packages_directory):
        os.makedirs(packages_directory)

    raw_packs = os.path.join(packages_directory, 'raw')
    if not os.path.exists(raw_packs):
        os.makedirs(raw_packs)

    filtered_packs = os.path.join(packages_directory, 'filtered')
    if not os.path.exists(filtered_packs):
        os.makedirs(filtered_packs)

    plots_directory = os.path.join(data_dir, 'packs_plots')
    if not os.path.exists(plots_directory):
        os.makedirs(plots_directory)

    if not args.normal_csv:
        to_normal_csv(narmal_csv_path, data_path,
                      split_packs=args.split_packs,
                      disgusting_decimal_sign=args.rep_decimal_sign,
                      disgusting_separator=args.rep_separator)
        dataframe = pd.read_csv(narmal_csv_path)
    else:
        dataframe = pd.read_csv(data_path)

    if args.external_csv:
        if not os.path.exists(args.external_csv) or not os.path.isfile(args.external_csv):
            parser.error('Either ' + args.external_csv + ' is not file or it does not exist.')
        dataframe.columns = ['Time', 'Voltage']
        concat_diff(dataframe, pd.read_csv(args.external_csv), 'Time')
    else:
        dataframe.columns = ['Time', 'Voltage', 'Current']

    filtered = df_filter(dataframe, Voltage=lambda xs: xs > read_val, Current=lambda xs: xs > read_val)

    @static_var('prev_value', 0)
    def divide(*args):
        if len(args) != 2:
            raise ValueError('Number of arguments must be equal to 2')
        result = args[0] / args[1] if args[1] != 0 else divide.prev_value
        divide.prev_value = args[0]
        return result

    filtered = df_add_col(filtered, 'Conductivity', 'Voltage', 'Current', action=divide)
    filtered.to_csv(path_or_buf=os.path.join(data_dir, 'Filtered.csv'))

    plot(filtered, 'Voltage', 'V')
    plot(filtered, 'Current', 'uA', fig=2, shape='r-')
    plot(filtered, 'Conductivity', 'S', fig=3, shape='g-')

    if args.split_packs:
        files = [f for f in os.listdir(raw_packs) if os.path.isfile(os.path.join(raw_packs, f)) and
                 f.split('.')[0]]
        figure = 1
        for file in files:
            dataframe = pd.read_csv(os.path.join(raw_packs, file))
            dataframe.columns = ['Time', 'Voltage', 'Current']

            filtered = df_filter(dataframe)
            filtered.to_csv(path_or_buf=os.path.join(filtered_packs, 'Filtered_'+file))
            plot(filtered, 'Current', 'uA', file_name='Filtered_current_'+str(file.split('.')[0])+'.png')
            figure += 1
