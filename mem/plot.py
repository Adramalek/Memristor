from matplotlib import pyplot as plt
from sys import argv
import pandas as pd
import numpy as np
import os
import argparse
from utils import static_var


__all__ = ['to_normal_csv',
           'concat_diff',
           'df_filter',
           'df_add_col',
           'plot']


def to_normal_csv(_processed_data_path, _data_path, split_packs=False, raw_packs=None,
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
                if split_packs:
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
        for key, val in col_cond.items():
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


def plot(df, directory, axis_y, ymunit, ylim=(-0.3, 100), axis_x='Time', xmunit='sec', shape='b-',
         fig=1, figsize=(80, 40), subplot=111, file_name=None):
    plt.figure(fig, figsize=figsize)
    plt.subplot(subplot)
    plt.plot(df[axis_x], df[axis_y], shape)
    plt.title(axis_y)
    plt.xlabel(axis_x+', '+xmunit)
    plt.ylabel(axis_y+', '+ymunit)
    plt.ylim(ylim[0], ylim[1])
    plt.legend()
    plt.savefig(os.path.join(directory, (file_name if file_name else axis_y)+'.png'))

