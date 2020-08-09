import csv
import os

import matplotlib.pyplot as plt


class PltGraph:
    GREY_PLOT_COLOR = '#b3b3b3'
    GREEN_PLOT_COLOR = '#1aff1a'

    def __init__(self, dir_path, ordered_landmarks_model_path, optimal_model_path):
        """
        :param dir_path: Path for the directory which holds the model files
        :param ordered_landmarks_model_path: Path for a model file which contains all the landmarks
        :param optimal_model_path: Path for the optimal model
        """
        self._fig, self.ax = plt.subplots()
        self.landmark_order = {}
        self.load(dir_path, ordered_landmarks_model_path, optimal_model_path)

    def load(self, dir_path, ordered_landmarks_model_path, optimal_model_path):
        self.load_landmarks(ordered_landmarks_model_path)
        self.load_dir(dir_path)
        self.load_file(optimal_model_path, plot_color=self.GREEN_PLOT_COLOR)

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

    def load_file(self, input_path, plot_color=GREY_PLOT_COLOR):
        points_x = []
        points_y = []
        with open(input_path, 'r') as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                points_x.append(self.landmark_order[key_from_gps(row[0], row[1])])
                points_y.append(float(row[2]))
        #self.ax.scatter(points_x, points_y, s=7)
        plt.plot(points_x, points_y, color=plot_color)

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


def key_from_gps(lat, lon):
    return f'{lat},{lon}'


if __name__ == '__main__':
    graph = PltGraph(r"C:\Users\Lior\Dropbox\EE-Drive\Database\Cut for FuelPlot",
                     r"C:\Users\Lior\Dropbox\EE-Drive\Database\Cut for FuelPlot\eliav 1 2019-11-14-15-19-35.csv",
                     r"C:\Users\Lior\Dropbox\EE-Drive\Database\Cut for FuelPlot\eliav 1 2019-11-14-15-19-35.csv")
    graph.show()
