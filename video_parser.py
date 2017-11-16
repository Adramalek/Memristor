import argparse
import pandas as pd
import cv2
from recognize_digits import *
from os.path import exists, isfile
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


def collect_data(frames, data_name):
    dataframe = pd.DataFrame()
    time = frange(0.0, len(frames), step=1/30)
    data = []
    for frame in frames:
        data.append(float(''.join(find_digits(frame))) * 1e-6)
    dataframe['Time'] = time
    dataframe[data_name] = data
    return dataframe

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('video', type=str, help='Specifies a source video')
    parser.add_argument('result_file', type=str, help='Specifies a location where result should be stored')
    parser.add_argument('--data_name', type=str, nargs='?', default='Data',
                        help='Specifies a column name of actual data')

    args = parser.parse_args()

    if not exists(args.video) or not isfile(args.video):
        parser.error('Either ' + args.video + ' is not file or it does not exist.')

    frames = get_frames(args.video)
    dataframe = collect_data(frames, args.data_name)
    dataframe.to_csv(path_or_buf=args.result_file)
