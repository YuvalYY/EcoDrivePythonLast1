import os
from csv import reader

from geopy import distance
from pyperclip import copy


def calc_dir_distance(input_dir):
    for filename in os.listdir(input_dir):
        print(calc_file_distance(os.path.join(input_dir, filename)))


def calc_file_average_speed(input_path):
    sum1 = 0.0
    total = 0
    with open(input_path, "r") as f:
        csv_reader = reader(f)
        next(csv_reader)
        for row in csv_reader:
            sum1 += int(row[3])
            total += 1
    return sum1 / total


def calc_file_distance(input_path):
    dist = 0.0
    x = load_file_gps(input_path)
    for i in range(len(x) - 1):
        dist += distance.distance(x[i], x[i + 1]).m
    return dist / 1000


def load_file_gps(input_path):
    tuple_list = []
    with open(input_path, "r") as f:
        csv_reader = reader(f)
        next(csv_reader)
        for row in csv_reader:
            tuple_list.append((float(row[1]), float(row[2])))
    return tuple_list


def tuple_list_to_geojson_coordinates(tuple_list):
    string = '{"type": "FeatureCollection","features": [\n'
    for tup in tuple_list:
        string += '{"type": "Feature","properties": {},"geometry": {"type": "Point","coordinates": ['
        string += str(tup[1]) + ',' + str(tup[0])
        string += ']}},\n'
    string = string[:-2]
    string += '\n]}'
    copy(string)
    return string
