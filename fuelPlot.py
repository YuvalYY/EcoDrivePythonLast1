import csv
import os

import matplotlib.pyplot as plt

import cutter

COLORS = ['#00FF00', '#7FFF00', '#FFFF00', '#FF7F00', '#FF0000']
DIVIDERS = []


class fuelPlot:
    def __init__(self, dir_path, ordered_landmarks_model_path, optimal_model_path):
        self._fig, self.ax = plt.subplots()
        self.landmark_order = {}
        self.load(dir_path, ordered_landmarks_model_path, optimal_model_path)

    def load(self, dir_path, ordered_landmarks_model_path, optimal_model_path):
        self.load_landmarks(ordered_landmarks_model_path)
        self.load_dir(dir_path)
        # self.load_file(optimal_model_path, plot_color=self.GREEN_PLOT_COLOR)

    def load_landmarks(self, input_path):
        with open(input_path, 'r') as f:
            csv_reader = csv.reader(f)
            i = 0
            for row in csv_reader:
                self.landmark_order[key_from_gps(row[0], row[1])] = i
                i += 1

    def load_dir(self, input_dir):
        for filename in os.listdir(input_dir):
            self.load_file(os.path.join(input_dir, filename))
        plt.gca().invert_yaxis()

    def load_file(self, input_path):
        matrix = load_model_matrix(input_path)
        for i in range(len(matrix) - 1):
            xs = [key_from_gps(matrix[i][0], matrix[i][1]), key_from_gps(matrix[i + 1][0], matrix[i + 1][1])]
            ys = [matrix[i][2], matrix[i + 1][2]]
            plt.plot(xs, ys, color=get_edge_color(matrix[i][3]))
        pointsx = [key_from_gps(row[0], row[1]) for row in matrix]
        pointsy = [row[2] for row in matrix]
        self.ax.scatter(pointsx, pointsy)

    def show(self):
        plt.gca().invert_yaxis()
        self.ax.set_title('Graph')
        self.ax.set_xlabel('(lat, long)')
        self.ax.set_ylabel('speed')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        plt.tick_params(
            axis='x',  # changes apply to the x-axis
            which='both',  # both major and minor ticks are affected
            bottom=False,  # ticks along the bottom edge are off
            top=False,  # ticks along the top edge are off
            labelbottom=False)  # labels along the bottom edge are off
        plt.tight_layout()
        plt.show()


def load_model_matrix(file_path):
    temp_matrix = []
    with open(file_path, 'r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            temp_matrix.append([float(row[0]), float(row[1]), int(row[2]), float(row[3])])
    return temp_matrix


def load_fuel_color_dividers(dir_path):
    x = []
    print(dir_path)
    for filename in os.listdir(dir_path):
        with open(os.path.join(dir_path, filename), "r") as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                x.append(float(row[-1]))
    step = max(x) / 5
    global DIVIDERS
    DIVIDERS = [step, step * 2, step * 3, step * 4]


def key_from_gps(lat, lon):
    return f'{lat},{lon}'


def get_edge_color(value):
    for i in range(len(COLORS) - 1):
        if value < DIVIDERS[i]:
            return COLORS[i]
    return COLORS[-1]


def cut():
    cutter.cut_dir(r"C:\Users\Lior\Dropbox\EE-Drive\Database\Eliav To Home 2\Model Files",
                   r"C:\Users\Lior\Dropbox\EE-Drive\Database\Cut for FuelPlot",
                   (31.860132199862605, 34.712515094777174), (31.84180734177865, 34.710048755663365))


if __name__ == '__main__':
    dpath = r"C:\Users\Lior\Dropbox\EE-Drive\Database\Cut for FuelPlot"
    landmark_model = r"C:\Users\Lior\Dropbox\EE-Drive\Database\Cut for FuelPlot\eliav 1 2019-11-14-15-19-35.csv"
    # First cut the models
    # then load them onto the plot and see everything turns nice
    # calc the best path
    # mark it somehow
    cut()
    load_fuel_color_dividers(dpath)
    print(f'{len(DIVIDERS)} {len(COLORS)}')
    graph = fuelPlot(dpath, landmark_model, None)
    graph.show()
