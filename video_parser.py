import argparse
import pandas as pd
import cv2
from recognize_digits import *
from os.path import exists, isfile, join
from utils import *
from sys import argv


def get_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    # success, image = cap.read()
    result = []
    success = True
    while success:
        success, image = cap.read()
        result.append(image)
    return result


def collect_data(video_path, data_name):
    dataframe = pd.DataFrame()
    cap = cv2.VideoCapture(video_path)
    success = True
    data = []
    while success:
        success, image = cap.read()
        data.append(float(''.join(find_digits(image))) * 1e-6)
    time = frange(0.0, len(data), step=1/30)
    dataframe['Time'] = time
    dataframe[data_name] = data
    return dataframe


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('video', type=str, help='Specifies a source video')
    parser.add_argument('result_file_mame', type=str, metavar='name',
                        help='Specifies a file where a result should be stored')
    parser.add_argument('-D', '--directory', type=str, metavar='dir',
                        help='Specifies a storage location.')
    parser.add_argument('-C', '--column_name', type=str, nargs='?', metavar='Column', default='Data',
                        help='Specifies a column name of actual data')

    args = parser.parse_args()

    if not exists(args.video) or not isfile(args.video):
        parser.error('Either ' + args.video + ' is not file or it does not exist.')

    dataframe = collect_data(args.video, args.column_name)
    dataframe.to_csv(path_or_buf=join(args.directory, args.result_file) if args.directory else args.result_file)
