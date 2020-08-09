import os
from csv import reader
from csv import writer

from geopy import distance

HEADER = ['Time', 'Latitude', 'Longitude', 'Speed', 'Fuel Consumption Rate']


def cut_dir(input_path, output_path, start, end):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for filename in os.listdir(input_path):
        cut_file(os.path.join(input_path, filename), os.path.join(output_path, filename), start, end)


# Changed to findclosest2, if you want to cut regularly return it to findclosest
def cut_file(input_path, output_path, start, end):
    matrix = load_csv_file(input_path)
    start_pos, end_pos = __find_closest2(matrix, start, end)
    with open(output_path, "w+", newline='') as f:
        csv_writer = writer(f)
        csv_writer.writerows(matrix[start_pos:end_pos])


def load_csv_file(input_path):
    with open(input_path, "r") as f:
        matrix = []
        csv_reader = reader(f)
        next(csv_reader)
        for row in csv_reader:
            matrix.append(row)
        return matrix


def __find_closest(matrix, start, end):
    start_pos = -1
    end_pos = -1
    start_diff = -1
    end_diff = -1
    for i in range(len(matrix)):
        if start_diff == -1 or distance.distance(start, (float(matrix[i][1]), float(matrix[i][2]))) < start_diff:
            start_pos = i
            start_diff = distance.distance(start, (float(matrix[i][1]), float(matrix[i][2])))
        if end_diff == -1 or distance.distance(end, (float(matrix[i][1]), float(matrix[i][2]))) < end_diff:
            end_pos = i
            end_diff = distance.distance(end, (float(matrix[i][1]), float(matrix[i][2])))
    return start_pos, end_pos


def __find_closest2(matrix, start, end):
    start_pos = -1
    end_pos = -1
    start_diff = -1
    end_diff = -1
    for i in range(len(matrix)):
        if start_diff == -1 or distance.distance(start, (float(matrix[i][0]), float(matrix[i][1]))) < start_diff:
            start_pos = i
            start_diff = distance.distance(start, (float(matrix[i][0]), float(matrix[i][1])))
        if end_diff == -1 or distance.distance(end, (float(matrix[i][0]), float(matrix[i][1]))) < end_diff:
            end_pos = i
            end_diff = distance.distance(end, (float(matrix[i][0]), float(matrix[i][1])))
    return start_pos, end_pos
