import os
from csv import reader

from geopy import distance
from pyperclip import copy

import modeler


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


def roundig_test():
    for i in range(101):
        print(i, 5 * round(i / 5))


def calc_csv_fuel_cost(input_path, has_headers=True):
    temp_matrix = []
    sum0 = 0
    with open(input_path, 'r') as file:
        if has_headers:
            next(file, None)
        for line in file:
            linesplit = line.split(',')
            temp_matrix.append([int(linesplit[0]), float(linesplit[-1])])
    for i in range(len(temp_matrix) - 1):
        sum0 += modeler.calculate_cost(temp_matrix[i][0], temp_matrix[i + 1][0], temp_matrix[i][1],
                                       temp_matrix[i + 1][1])
    return sum0


def calc_model_fuel_cost(input_path):
    lastlinecost = 0
    sum0 = 0.0
    with open(input_path, 'r') as f:
        csv_reader = reader(f)
        for line in csv_reader:
            sum0 += float(line[-1])
            lastlinecost = float(line[-1])
    return sum0 - lastlinecost
