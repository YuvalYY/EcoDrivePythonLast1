import matplotlib.pyplot as plt

import util


def truncate_float(num):
    return float('%.1f' % num)


def calculate_bin_dict(x):
    bin_dict = dict()
    for num in x:
        key = truncate_float(num)
        print(key)
        if key in bin_dict:
            bin_dict[key] += 1
        else:
            bin_dict[key] = 1
    print(bin_dict)
    return bin_dict


class HistogramView:
    def __init__(self):
        self._fig, self.ax = plt.subplots()

    def draw_block(self, lower_limit, height, width=0.1):
        self.ax.fill([lower_limit, lower_limit, lower_limit + width, lower_limit + width], [0, height, height, 0])

    def draw_line(self, x, height):
        plt.plot([x, x], [0, height], "black", linewidth=2)

    def show(self):
        plt.tight_layout()
        plt.show()


if __name__ == '__main__':
    hview = HistogramView()
    input_dir = r"C:\Users\Lior\Dropbox\EE-Drive\Database\Eliav From Home 1\Model Files"
    x = util.calc_model_dir_fuel_cost(input_dir)
    thing = calculate_bin_dict(x)
    for i in thing:
        key=truncate_float(i)
        hview.draw_block(key, thing[key])
    line_height = max([thing[j] for j in thing]) + 1
    hview.draw_line(min(x), line_height)
    hview.draw_line(sum(x) / len(x), line_height)
    hview.show()
