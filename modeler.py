# this class would take the centers list (load from file) and a dir, for each file it will create the file
# it will generate the drive matrix with another column s4et to false
# for each line it will find the closest center and insert into a map of center->all the lines with it
# each center will choose its closest point to be its representation, which will be marked by true in the new column
# we will also need to save in each one, who is its relevant center
# then we will calculate the cost between the points (which will also include normalized speed),
# and the cost between the current one to the next one, with the last one having cost of 0 to the next
import os
from csv import reader
from csv import writer

from geopy import distance

MILLIS_IN_HOUR = 3600000


def generate_dir_models(input_dir, output_dir, centers_file_path):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    centers = load_centers_file(centers_file_path)
    for filename in os.listdir(input_dir):
        generate_file_model(os.path.join(input_dir, filename), os.path.join(output_dir, filename), centers)


def generate_file_model(input_path, output_path, centers_list):
    print("creating model for: " + input_path)
    matrix = load_csv_file(input_path)
    center_lines_dict = {center: [] for center in centers_list}

    for i in range(len(matrix)):
        cc = find_closest_center((matrix[i][1], matrix[i][2]), centers_list)
        center_lines_dict[cc].append(i)
        matrix[i][-1] = cc[1]
        matrix[i][-2] = cc[0]

    for center in center_lines_dict:
        currenti = find_closest_latlon(center, center_lines_dict[center], matrix)
        if currenti != -1:
            matrix[currenti][-3] = True

    with open(output_path, 'w+', newline='') as f:
        csv_writer = writer(f)
        x = generate_model(matrix)
        print(str(len(x)) + ' centers in file')
        csv_writer.writerows(x)


def load_centers_file(input_path):
    centers_list = []
    with open(input_path, "r") as f:
        for line in f:
            centers_list.append((float(line.split(',')[0]), float(line.split(',')[1])))
    return centers_list


def load_csv_file(input_path):
    with open(input_path, "r") as f:
        matrix = []
        csv_reader = reader(f)
        next(csv_reader)
        for row in csv_reader:
            # time, lat, lon, speed, fuel, is closest to its center, center lat, center lon
            matrix.append([float(row[0]), float(row[1]), float(row[2]), int(row[3]), float(row[4]), False, -200, -200])
        return matrix


def find_closest_center(latlon, centers_list):
    closest_center = centers_list[0]
    min_dist = distance.distance(latlon, closest_center)
    for center in centers_list:
        if distance.distance(latlon, center) < min_dist:
            closest_center = center
            min_dist = distance.distance(latlon, center)
    return closest_center


def find_closest_latlon(center, ilist, matrix):
    if len(ilist) != 0:
        closest_i = ilist[0]
        min_dist = distance.distance(matrix[closest_i][1], matrix[closest_i][2], center)
        for i in ilist:
            latlon = (matrix[i][1], matrix[i][2])
            if distance.distance(latlon, center) < min_dist:
                closest_i = i
                min_dist = distance.distance(latlon, center)
        return closest_i
    return -1


def generate_model(matrix):
    i = 0
    model_matrix = []
    # Find the first true
    while not matrix[i][-3]:
        i += 1

    model_matrix.append([matrix[i][-2], matrix[i][-1], 5 * round(float(matrix[i][3]) / 5), 0.0])  # Add the first center
    model_matrix[-1][-1] += calculate_cost(matrix[i][0], matrix[i + 1][0], matrix[i][4], matrix[i + 1][4])
    i += 1  # Advance i
    while i < len(matrix) - 1:
        if matrix[i][-3]:
            model_matrix.append([matrix[i][-2], matrix[i][-1], 5 * round(float(matrix[i][3]) / 5), 0.0])
            model_matrix[-1][-1] += calculate_cost(matrix[i][0], matrix[i + 1][0], matrix[i][4], matrix[i + 1][4])
        else:
            model_matrix[-1][-1] += calculate_cost(matrix[i][0], matrix[i + 1][0], matrix[i][4], matrix[i + 1][4])
        i += 1
    return model_matrix


def calculate_cost(time1, time2, fcr1, fcr2):
    time_in_hours = abs(time1 - time2) / MILLIS_IN_HOUR
    high = max(fcr1, fcr2)
    low = min(fcr1, fcr2)
    return low * time_in_hours + ((high - low) * time_in_hours) / 2
