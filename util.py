import datetime
import math
import os
from csv import reader

from geopy import distance
from pyperclip import copy

import modeler


def calc_dir_distance(input_dir):
    average = 0
    for filename in os.listdir(input_dir):
        x = calc_file_distance(os.path.join(input_dir, filename))
        average += x
        print(filename + ' : ' + str(x))
    print('Average is : ' + str(average / len(os.listdir(input_dir))))


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


def csv_to_geojson(input_path):
    return tuple_list_to_geojson_coordinates(load_file_gps(input_path))


def load_file_gps(input_path):
    tuple_list = []
    with open(input_path, "r") as f:
        csv_reader = reader(f)
        next(csv_reader)
        for row in csv_reader:
            tuple_list.append((float(row[1]), float(row[2])))
    return tuple_list


def centers_file_to_geojson(input_path):
    tuple_list = []
    with open(input_path, "r") as f:
        csv_reader = reader(f)
        for row in csv_reader:
            tuple_list.append((float(row[0]), float(row[1])))
    return tuple_list_to_geojson_coordinates(tuple_list)


def dir_to_geojson(input_dir):
    x = []
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        x.extend(load_file_gps(file_path))
    tuple_list_to_geojson_coordinates(x)


def tuple_list_to_geojson_coordinates(tuple_list):
    string = '{"type": "FeatureCollection","features": [\n'
    for tup in tuple_list:
        string += '{"type": "Feature","properties": {"marker-size": "small"},"geometry": {"type": "Point","coordinates": ['
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


def calc_model_dir_fuel_cost(input_dir):
    x = []
    for filename in os.listdir(input_dir):
        d = calc_model_fuel_cost(os.path.join(input_dir, filename))
        print(f'{filename} = {d}')
        x.append(d)
    print(f'best = {min(x)}')
    print(f'avg = {sum(x)/len(x)}')
    print(f'worst = {max(x)}')
    return x


def gps_csv_to_gpx(input_path, output_path):
    name = input_path.split('\\')[-1].replace('.csv', '').replace('GPS ', '')
    string = '<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n<gpx xmlns="http://www.topografix.com/GPX/1/1" ' \
             'creator="MapSource 6.16.1" version="1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
             'xsi:schemaLocation="http://www.topografix.com/GPX/1/1 ' \
             'http://www.topografix.com/GPX/1/1/gpx.xsd">\n<trk>\n<name> '
    string += name
    string += '</name>\n<trkseg>\n'
    with open(input_path, 'r') as f:
        for s in f:
            line = s.strip().split(',')
            string += '<trkpt lat="' + line[1] + '" lon="' + line[2] + '"><ele>0.000000</ele><time>'
            target_date = str(datetime.datetime(1970, 1, 1) + datetime.timedelta(0, 0, 0, int(line[0]))).split(' ')
            string += target_date[0] + 'T' + target_date[1] + 'Z</time></trkpt>\n'
        string += '</trkseg>\n</trk>\n</gpx>'
    with open(output_path, 'w+') as f:
        f.write(string)


def calc_k_for_section(section_length, interval_length, avg_speed):
    return int(math.floor((section_length * 3600) / (interval_length * avg_speed)))
