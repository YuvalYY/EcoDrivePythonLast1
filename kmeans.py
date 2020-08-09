import os
from csv import reader

import numpy as np
from sklearn.cluster import KMeans

import util


def get_and_save_centers(input_dir, output_path, k):
    centers = get_centers(input_dir, k)
    with open(output_path, 'w+') as f:
        for center in centers:
            f.write(str(center[0]) + ',' + str(center[1]) + '\n')
    return centers


def get_centers(input_dir, k):
    np.set_printoptions(threshold=np.inf)
    x = np.array(load_dir_gps(input_dir), dtype=('float', 'float'))
    kmeans = KMeans(n_clusters=k, n_init=300, max_iter=600, precompute_distances='auto').fit(x)
    return kmeans.cluster_centers_


def load_dir_gps(input_dir):
    tuple_list = []
    for filename in os.listdir(input_dir):
        tuple_list.extend(load_file_gps(os.path.join(input_dir, filename)))
    return tuple_list


def load_file_gps(input_path):
    tuple_list = []
    with open(input_path, "r") as f:
        csv_reader = reader(f)
        next(csv_reader)
        for row in csv_reader:
            tuple_list.append((float(row[1]), float(row[2])))
    return tuple_list333
