import csv
import os

import matplotlib.pyplot as plt
from matplotlib import ticker

import cutter


class GraphView:
    def __init__(self):
        self.optimal_vertices = []
        self._fig, self.ax = plt.subplots()
        self.edges = dict()
        self.landmark_order = dict()
        self.vertices = []
        self.colors = ['#00FF00', '#7FFF00', '#FFFF00', '#FF7F00', '#FF0000']
        self.dividers = []

    def draw(self):
        self.draw_edges()
        self.draw_vertices()
        self.draw_startend()
        if len(self.optimal_vertices) != 0:
            self.draw_optimal_vertices()

    def draw_vertices(self):
        pointsx = [vertex[0] for vertex in self.vertices]
        pointsy = [vertex[1] for vertex in self.vertices]
        self.ax.scatter(pointsx, pointsy, s=20, c="gray", zorder=2)

    def draw_edges(self):
        for key in self.edges:
            keysplit = [float(i) for i in key.split()]
            pointsx = [keysplit[0], keysplit[2]]
            pointsy = [keysplit[1], keysplit[3]]
            plt.plot(pointsx, pointsy, color=self.get_edge_color(self.edges[key]), zorder=1)

    def draw_startend(self, distance=3):  # distance means how far will the start and end be
        speeds = [v[1] for v in self.vertices]
        y = (min(speeds) + max(speeds)) / 2
        self.draw_edge_vertex(-distance, y, 0)
        self.draw_edge_vertex(len(self.landmark_order) + distance, y, len(self.landmark_order) - 1)

    def draw_edge_vertex(self, x, y, landmarkx):  # landmarkx means the landmark to which the edge vertex will connect
        self.ax.scatter(x, y, s=40, c="blue", zorder=2)
        y_to_connect = [v[1] for v in self.vertices if v[0] == landmarkx]
        for connecty in y_to_connect:
            plt.plot([x, landmarkx], [y, connecty], color="gray", zorder=1)

    def draw_optimal_vertices(self):
        pointsx = [vertex[0] for vertex in self.optimal_vertices]
        pointsy = [vertex[1] for vertex in self.optimal_vertices]
        self.ax.scatter(pointsx, pointsy, s=40, c="blue", zorder=2)

    def load_models(self, landmark_path, dir_path, optimal_path=None):
        self.load_landmarks(landmark_path)
        self.load_dir(dir_path)
        self.calc_edges()
        self.calc_dividers()
        if optimal_path:
            self.load_optimal(optimal_path)

    def load_dir(self, dir_path):
        for filename in os.listdir(dir_path):
            self.load_file(os.path.join(dir_path, filename))
        plt.gca().invert_yaxis()

    def load_file(self, file_path):
        matrix = load_model_matrix(file_path)
        self.load_file_edges(matrix)
        self.load_file_vertices(matrix)

    def load_optimal(self, file_path):
        with open(file_path, 'r') as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                landmark = self.landmark_order[key_from_gps(float(row[0]), float(row[1]))]
                self.optimal_vertices.append((landmark, int(row[2])))

    def load_file_edges(self, matrix):
        for i in range(len(matrix) - 1):
            row1 = matrix[i]
            row2 = matrix[i + 1]
            key = self.edge_key(row1[0], row1[1], row1[2], row2[0], row2[1], row2[2])
            if key in self.edges:
                self.edges[key][0] += row1[3]
                self.edges[key][1] += 1
            else:
                self.edges[key] = [row1[3], 1]

    def load_file_vertices(self, matrix):
        self.vertices.extend([(self.landmark_order[key_from_gps(row[0], row[1])], row[2]) for row in matrix])

    def load_landmarks(self, input_path):
        with open(input_path, 'r') as f:
            csv_reader = csv.reader(f)
            i = 0
            for row in csv_reader:
                self.landmark_order[key_from_gps(row[0], row[1])] = i
                i += 1

    def edge_key(self, lat1, lon1, speed1, lat2, lon2, speed2):
        return f'{self.landmark_order[key_from_gps(lat1, lon1)]} {speed1} ' \
               f'{self.landmark_order[key_from_gps(lat2, lon2)]} {speed2} '

    def calc_edges(self):
        for key in self.edges:
            self.edges[key] = self.edges[key][0] / self.edges[key][1]

    def calc_dividers(self):
        limit = max([self.edges[key] for key in self.edges])
        step = limit / len(self.colors)
        self.dividers = [step * i for i in range(1, len(self.colors))]

    def get_edge_color(self, value):
        for i in range(len(self.dividers)):
            if value < self.dividers[i]:
                return self.colors[i]
        return self.colors[-1]

    def show(self):
        plt.gca().invert_yaxis()
        self.ax.set_ylabel('speed')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
        plt.tick_params(
            axis='x',  # changes apply to the x-axis
            which='both',  # both major and minor ticks are affected
            bottom=False,  # ticks along the bottom edge are off
            top=False,  # ticks along the top edge are off
            labelbottom=False)  # labels along the bottom edge are off
        plt.tight_layout()
        plt.show()


def key_from_gps(lat, lon):
    return f'{lat},{lon}'


def load_model_matrix(file_path):
    temp_matrix = []
    with open(file_path, 'r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            temp_matrix.append([float(row[0]), float(row[1]), int(row[2]), float(row[3])])
    return temp_matrix


def cut():
    cutter.cut_dir(r"C:\Users\Lior\Dropbox\EE-Drive\Database\Eliav To Home 2\Model Files",
                   r"C:\Users\Lior\Dropbox\EE-Drive\Database\Cut for FuelPlot",
                   (31.860132199862605, 34.712515094777174), (31.84180734177865, 34.710048755663365))


if __name__ == '__main__':
    graph = GraphView()
    graph.load_models(r"C:\Users\Lior\Dropbox\EE-Drive\Database\Cut for FuelPlot\eliav 1 2019-11-14-15-19-35.csv",
                      r"C:\Users\Lior\Dropbox\EE-Drive\Database\Cut for FuelPlot")
    graph.draw()
    graph.show()
