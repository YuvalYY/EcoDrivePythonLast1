import os
from csv import reader
from csv import writer
from enum import Enum

R = 8.314
MMAir = 28.97
MILLIS_IN_HOUR = 3600000
DEFAULT_VOLUMETRIC_EFFICIENCY = 80  # percent
HEADER = ['Time', 'Latitude', 'Longitude', 'Speed', 'Fuel Consumption Rate']


class FuelTypes(Enum):  # grams of air to 1 gram of fuel, g/dm^3
    GASOLINE = 14.7, 820
    DIESEL = 14.5, 750


class CommandNames(Enum):
    SPEED = "Vehicle Speed"
    AIR_INTAKE_TEMP = 'Air Intake Temperature'
    ENGINE_RPM = 'Engine RPM'
    INTAKE_MANIFOLD_PRESSURE = "Intake Manifold Pressure"
    MAF = "Mass Air Flow"
    FUEL_CONSUMPTION_RATE = 'Fuel Consumption Rate'


def combine_rpm_dir(input_path, output_path, engine_disp, fuel_type,
                    volumetric_efficiency=DEFAULT_VOLUMETRIC_EFFICIENCY):
    gps_files, obd_files, output_files = __load_for_combining(input_path, output_path)
    for i in range(len(output_files)):
        print("creating " + output_files[i])
        with open(output_files[i], "w+", newline='') as f:
            csv_writer = writer(f)
            csv_writer.writerow(HEADER)
            csv_writer.writerows(
                combine_rpm_files(load_csv_file(gps_files[i]), load_csv_file(obd_files[i]), engine_disp, fuel_type,
                                  volumetric_efficiency))


def combine_maf_dir(input_path, output_path, fuel_type):
    gps_files, obd_files, output_files = __load_for_combining(input_path, output_path)
    for i in range(len(output_files)):
        print("creating "+output_files[i])
        with open(output_files[i], "w+", newline='') as f:
            csv_writer = writer(f)
            csv_writer.writerow(HEADER)
            csv_writer.writerows(
                combine_maf_files(load_csv_file(gps_files[i]), load_csv_file(obd_files[i]), fuel_type))


def combine_fuel_dir(input_path, output_path):
    gps_files, obd_files, output_files = __load_for_combining(input_path, output_path)
    for i in range(len(output_files)):
        print("creating " + output_files[i])
        with open(output_files[i], "w+", newline='') as f:
            csv_writer = writer(f)
            csv_writer.writerow(HEADER)
            csv_writer.writerows(
                combine_fuel_files(load_csv_file(gps_files[i]), load_csv_file(obd_files[i])))


def load_csv_file(input_path):
    with open(input_path, "r") as f:
        matrix = []
        csv_reader = reader(f)
        for row in csv_reader:
            matrix.append(row)
        return matrix


def calc_maf(rpm, map1, iat, engine_disp, volumetric_efficiency=DEFAULT_VOLUMETRIC_EFFICIENCY):
    iat = iat + 273.15  # converting celsius to kelvin
    imap = rpm * map1 / iat / 2  # synthetic variable
    return ((imap / 60) * (volumetric_efficiency / 100) * engine_disp * (MMAir / R)) / 1000


def calc_fuel(maf, fuel_type):
    return (maf * 3600) / (fuel_type.value[0] * fuel_type.value[1])


def combine_rpm_files(gps_matrix, obd_matrix, engine_disp, fuel_type,
                      volumetric_efficiency=DEFAULT_VOLUMETRIC_EFFICIENCY):
    output_matrix = []
    for gps_call in gps_matrix:
        output_matrix.append(
            __generate_rpm_full_call(gps_call, obd_matrix, engine_disp, fuel_type, volumetric_efficiency))
    return output_matrix


def combine_maf_files(gps_matrix, obd_matrix, fuel_type):
    output_matrix = []
    for gps_call in gps_matrix:
        output_matrix.append(__generate_maf_full_call(gps_call, obd_matrix, fuel_type))
    return output_matrix


def combine_fuel_files(gps_matrix, obd_matrix):
    output_matrix = []
    for gps_call in gps_matrix:
        output_matrix.append(__generate_fuel_full_call(gps_call, obd_matrix))
    return output_matrix


def __load_for_combining(input_path, output_path):
    gps_files = []
    obd_files = []
    output_files = []
    # Load the file paths into lists and generate the output_files list
    for filename in os.listdir(input_path):
        if filename.endswith('.csv'):
            if 'GPS' in filename:
                gps_files.append(os.path.join(input_path, filename))
                # might switch the space to the other side after the update for the app
                output_files.append(os.path.join(output_path, filename.replace('GPS ', '')))
            elif 'OBD' in filename:
                obd_files.append(os.path.join(input_path, filename))
    # Sort them so now all three would be aligned with one another
    sorted(gps_files)
    sorted(obd_files)
    sorted(output_files)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    return gps_files, obd_files, output_files


def __generate_rpm_full_call(gps_call, obd_matrix, engine_disp, fuel_type, volumetric_efficiency):
    time = int(gps_call[0])
    speed = 0
    rpm = 0
    map1 = 0
    iat = 0
    speed_diff = -1
    rpm_diff = -1
    map1_diff = -1
    iat_diff = -1
    for row in obd_matrix:
        if row[1] == CommandNames.ENGINE_RPM.value:
            if rpm_diff == -1 or abs(int(row[0]) - time) < rpm_diff:
                rpm = float(row[2])
                rpm_diff = abs(int(row[0]) - time)
        elif row[1] == CommandNames.INTAKE_MANIFOLD_PRESSURE.value:
            if map1_diff == -1 or abs(int(row[0]) - time) < map1_diff:
                map1 = float(row[2])
                map1_diff = abs(int(row[0]) - time)
        elif row[1] == CommandNames.AIR_INTAKE_TEMP.value:
            if iat_diff == -1 or abs(int(row[0]) - time) < iat_diff:
                iat = float(row[2])
                iat_diff = abs(int(row[0]) - time)
        else:
            if speed_diff == -1 or abs(int(row[0]) - time) < speed_diff:
                speed = int(row[2])
                speed_diff = abs(int(row[0]) - time)
    return [gps_call[0], gps_call[1], gps_call[2], speed,
            calc_fuel(calc_maf(rpm, map1, iat, engine_disp, volumetric_efficiency), fuel_type)]


def __generate_maf_full_call(gps_call, obd_matrix, fuel_type):
    time = int(gps_call[0])
    speed = 0
    maf = 0
    speed_diff = -1
    maf_diff = -1
    for row in obd_matrix:
        if row[1] == CommandNames.MAF.value:
            if maf_diff == -1 or abs(int(row[0]) - time) < maf_diff:
                maf = float(row[2])
                maf_diff = abs(int(row[0]) - time)
        else:
            if speed_diff == -1 or abs(int(row[0]) - time) < speed_diff:
                speed = int(row[2])
                speed_diff = abs(int(row[0]) - time)
    return [gps_call[0], gps_call[1], gps_call[2], speed, calc_fuel(maf, fuel_type)]


def __generate_fuel_full_call(gps_call, obd_matrix):
    time = int(gps_call[0])
    speed = 0
    fuel = 0
    speed_diff = -1
    fuel_diff = -1
    for row in obd_matrix:
        if row[1] == CommandNames.FUEL_CONSUMPTION_RATE.value:
            if fuel_diff == -1 or abs(int(row[0]) - time) < fuel_diff:
                fuel = float(row[2])
                fuel_diff = abs(int(row[0]) - time)
        else:
            if speed_diff == -1 or abs(int(row[0]) - time) < speed_diff:
                speed = int(row[2])
                speed_diff = abs(int(row[0]) - time)
    return [gps_call[0], gps_call[1], gps_call[2], speed, fuel]
