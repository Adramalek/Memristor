import argparse
import logging
import pandas as pd
from utils import init_log, storage_dir, positive, exists_file, static_var
from mem.experiment import *
from comm import COMPortController
from mem.plot import *
from os.path import join, exists, isfile
from os import mkdir, listdir
from sys import argv
from threading import Event

__all__ = ['reset',
           'experiment',
           'init_argparser']


def root_dir(func):
    def wrapper(*args, **kwargs):
        if not exists(args[0].memristor):
            mkdir(args[0].memristor)
        meas = join(args[0].memristor, args[0].storage_path)
        if not exists(meas):
            mkdir(meas)
        setattr(args[0], 'meas', meas)
        func(*args, **kwargs)
    return wrapper


@root_dir
def reset(args):
    init_log('resetting.log')
    comp = COMPortController(args.port)
    comp.reset()
    comp.close()
    pass


@root_dir
def experiment(args):
    init_log(join(args.meas, 'experiment.log'))
    comp = COMPortController(args.port)
    viwriter = Viwriter(path=join(args.meas, args.video_storage), flip=args.flip)
    high = args.init_high
    period = high + args.init_low
    low = period - high
    iteration = 1
    stopper = Event()
    while period <= args.max_period:
        while low > 0:
            logging.info('Iteration {}'.format(iteration))
            comp.timeout = 10
            comp.set_high_del(high)
            comp.set_low_del(low)
            logging.info("Run H{} L{}".format(high, low))
            comp.timeout = None
            viwriter.start('P{}H{}'.format(period, high))
            write_voltage('P{}H{}.csv'.format(period, high), high, low, stopper)
            comp.start()
            stop_writing(stopper)
            viwriter.stop()
            comp.reset()
            high += args.step_high
            low = period - high
            logging.info('\n')
            iteration += 1
            stopper.clear()
        high = args.init_high
        period += args.step_low
        low = period - high

    viwriter.release()
    comp.close()


@root_dir
def plot(args):
    read_val = -5

    if not args.normal_csv:
        normal_csv_path = join(args.result_dir, 'Processed.csv')
        to_normal_csv(normal_csv_path, args.file,
                      split_packs=args.split_packs,
                      disgusting_decimal_sign=args.rep_decimal_sign,
                      disgusting_separator=args.rep_separator)
        dataframe = pd.read_csv(normal_csv_path)
    else:
        dataframe = pd.read_csv(args.file)

    if args.external_csv:
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
    filtered.to_csv(path_or_buf=join(args.result_dir, 'Filtered.csv'))

    plot(filtered, args.result_dir, 'Voltage', 'V')
    plot(filtered, args.result_dir, 'Current', 'uA', fig=2, shape='r-')
    plot(filtered, args.result_dir, 'Conductivity', 'S', fig=3, shape='g-')

    if args.split_packs:
        packages_directory = join(args.result_dir, 'packs')
        if not exists(packages_directory):
            mkdir(packages_directory)

        raw_packs = join(packages_directory, 'raw')
        if not exists(raw_packs):
            mkdir(raw_packs)

        filtered_packs = join(packages_directory, 'filtered')
        if not exists(filtered_packs):
            mkdir(filtered_packs)

        plots_directory = join(packages_directory, 'packs_plots')
        if not exists(plots_directory):
            mkdir(plots_directory)

        files = [f for f in listdir(raw_packs) if isfile(join(raw_packs, f)) and
                 f.split('.')[0]]
        figure = 1
        for file in files:
            dataframe = pd.read_csv(join(raw_packs, file))
            dataframe.columns = ['Time', 'Voltage', 'Current']

            filtered = df_filter(dataframe)
            filtered.to_csv(path_or_buf=join(filtered_packs, 'Filtered_'+file))
            plot(filtered, plots_directory, 'Current', 'uA', file_name='Filtered_current_'+str(file.split('.')[0])+'.png')
            figure += 1


@root_dir
def dummy(args):
    print('Hello')


def init_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-D', '--storage_path', type=str, metavar='dir', nargs='?', default='meas')
    parser.add_argument('memristor', type=str, metavar='name')
    subparsers = parser.add_subparsers()

    parser_dummy = subparsers.add_parser('dummy')
    parser_dummy.set_defaults(func=dummy)

    parser_exp = subparsers.add_parser('exp')
    parser_exp.add_argument('port', type=str)
    parser_exp.add_argument('-V', '--video_storage', type=str, metavar='dir', nargs='?',
                            default='video')
    parser_exp.add_argument('-H', '--init_high', type=positive, metavar='ms', nargs='?', default=10)
    parser_exp.add_argument('-L', '--init_low', type=positive, metavar='ms', nargs='?', default=10)
    parser_exp.add_argument('-P', '--max_period', type=positive, metavar='ms', nargs='?', default=10000)
    parser_exp.add_argument('-sh', '--step_high', type=positive, metavar='ms', nargs='?', default=10)
    parser_exp.add_argument('-sl', '--step_low', type=positive, metavar='ms', nargs='?', default=10)
    parser_exp.add_argument('-f', '--flip', action='store_true')
    parser_exp.set_defaults(func=experiment)

    parser_reset = subparsers.add_parser('reset')
    parser_reset.add_argument('port', type=str)
    parser_reset.add_argument('-T', '--time', type=positive, metavar='sec', nargs='?', default=120)
    parser_reset.set_defaults(func=reset)

    parser_plot = subparsers.add_parser('plot')
    parser_plot.add_argument('file', type=exists_file, help='Specifies a source data location')
    parser_plot.add_argument('-R', '--result_dir', type=storage_dir, nargs='?', default='meas',
                             help='Specifies a results storage location')
    parser_plot.add_argument('-E', '--external_csv', type=exists_file, metavar='location', nargs='?', default=None,
                             help='Specifies external source to concatenate (excluding share columns)')
    parser_plot.add_argument('-C', '--concat_by', type=str, nargs='?', metavar='column',
                             required='--external_csv' in argv, default='Time',
                             help='Specifies a share column to restrict rows count.'
                                  '\nRequires --external_csv option to be specified')
    parser_plot.add_argument('-P', '--split_packs', action='store_true',
                             help='Enables splitting of source data into individual packs (based on time)')
    parser_plot.add_argument('-N', '--normal_csv', action='store_true',
                             help='Indicates converting source data to normal csv format as unnecessary.')
    parser_plot.add_argument('-S', '--rep_separator', type=str, nargs='?', metavar='char', default=';',
                             required='-N' not in argv,
                             help='Specifies a target disgusting separator which must be replaced! ";" by default.'
                                  '\nCannot be specified with --normal_csv option.')
    parser_plot.add_argument('-D', '--rep_decimal_sign', type=str, nargs='?', metavar='char', default=',',
                             required='-N' not in argv,
                             help='Specifies a target disgusting decimal sign which must be replaced! "," by default.'
                                  '\nCannot be specified with --normal_csv option.')

    return parser

