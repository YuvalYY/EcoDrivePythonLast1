import os
from csv import reader
from csv import writer

vertex_dict = {}


# still need to mark the broken files


def generate_and_save_cheapest_model_and_optimal(input_dir, model_output_path, optimal_output_path):
    generate_and_save_cheapest_model(input_dir, model_output_path)
    generate_and_save_optimal(optimal_output_path)


def generate_and_save_optimal(optimal_output_path):
    rows = []
    curr = get_start()
    while curr:
        rows.append(curr.to_row())
        curr = curr.father
    rows = rows[1:-1]  # remove start and end vertices
    with open(optimal_output_path, 'w+', newline='') as f:
        csv_writer = writer(f)
        csv_writer.writerows(rows)


def generate_and_save_cheapest_model(input_dir, output_path):
    with open(output_path, 'w+', newline='') as f:
        csv_writer = writer(f)
        csv_writer.writerows(generate_cheapest_model(input_dir))


def generate_cheapest_model(input_dir):
    create_start_and_end()
    for filename in os.listdir(input_dir):
        load_model_file(os.path.join(input_dir, filename))
    calc_vertex_neighbors()
    dijkstra()
    generate_and_save_optimal(r'C:\Users\Lior\Desktop\Optimal.csv')
    return make_organized_list()


def load_model_file(input_path):
    # Load file
    temp_matrix = []
    with open(input_path, 'r') as f:
        csv_reader = reader(f)
        for row in csv_reader:
            temp_matrix.append([float(row[0]), float(row[1]), int(row[2]), float(row[3])])

    # Connect to start and end unless marked to not connect
    if not input_path.endswith('S.csv') and not input_path.endswith('SE.csv'):
        get_vertex(temp_matrix[0][0], temp_matrix[0][1], temp_matrix[0][2]).add_neighbor(get_start(), 0)
    if not input_path.endswith('E.csv') and not input_path.endswith('SE.csv'):
        get_end().add_neighbor(get_vertex(temp_matrix[-1][0], temp_matrix[-1][1], temp_matrix[-1][2]), 0)

    # Add all the vertexes and connect them
    for i in range(len(temp_matrix) - 1):
        get_vertex(temp_matrix[i + 1][0], temp_matrix[i + 1][1], temp_matrix[i + 1][2]).add_neighbor(
            get_vertex(temp_matrix[i][0], temp_matrix[i][1], temp_matrix[i][2]), temp_matrix[i][3])


def get_vertex(lat, lon, speed):
    key = str(lat) + ',' + str(lon) + ',' + str(speed)
    if key not in vertex_dict:
        vertex_dict[key] = Vertex(lat, lon, speed)
    return vertex_dict[key]


def calc_vertex_neighbors():
    for key in vertex_dict:
        vertex_dict[key].calc_neighbors_cost()


def dijkstra():
    visited_vertexes = []
    found_vertexes = [get_end()]
    while found_vertexes:
        current_vertex = min(found_vertexes, key=lambda x: x.cost_to)
        visited_vertexes.append(current_vertex)
        found_vertexes.remove(current_vertex)
        for neighbor in current_vertex.get_neighbors():
            if neighbor not in visited_vertexes and neighbor not in found_vertexes:
                found_vertexes.append(neighbor)
        current_vertex.update_neighbors()
    print(get_start().cost_to)


def create_start_and_end():
    get_vertex(-200, -200, -1)
    get_vertex(200, 200, -1).cost_to = 0


def get_start():
    return get_vertex(-200, -200, -1)


def get_end():
    return get_vertex(200, 200, -1)


def make_organized_list():
    curr = get_start()
    organized_list = []
    while curr:
        organized_list.append(curr)
        curr = curr.father
    organized_list.remove(get_start())
    organized_list.remove(get_end())

    temp_dict = {v.get_latlon(): [] for v in organized_list}

    # The organized_list is composed of the order at which we traverse from start to end, if the path skips a
    # landmark We will check for it in the for below, but it will not be known Therefore you must devise a new way to
    # organize the list in accordance to the landmarks, perhaps find a file which has all of the landmarks and act
    # according to it
    for v in vertex_dict.values():
        if v.lat != -200 and v.lat != 200:
            temp_dict[v.get_latlon()].append([v.lat, v.lon, v.speed, v.father.speed])

    for _ in temp_dict.values():
        _.sort(key=lambda x: x[2])

    return_list = []
    for vertex in organized_list:
        return_list.extend(temp_dict[vertex.get_latlon()])

    return return_list


class Vertex:
    def __init__(self, lat, lon, speed):
        self.lat = lat
        self.lon = lon
        self.speed = speed
        self.neighbors = []
        self.father = None
        self.cost_to = -1

    def add_neighbor(self, vertex, cost):
        for i in range(len(self.neighbors)):
            if self.neighbors[i][0].get_key() == vertex.get_key():
                self.neighbors[i][1] += 1
                self.neighbors[i][2] += cost
                return
        self.neighbors.append([vertex, 1, cost])

    def get_key(self):
        return str(self.lat) + ',' + str(self.lon) + ',' + str(self.speed)

    def get_latlon(self):
        return str(self.lat) + ',' + str(self.lon)

    def to_row(self):
        return [self.lat, self.lon, self.speed]

    def calc_neighbors_cost(self):
        for i in range(len(self.neighbors)):
            self.neighbors[i][1] = self.neighbors[i][2] / self.neighbors[i][1]
            del self.neighbors[i][-1]

    def get_neighbors(self):
        return [n[0] for n in self.neighbors]

    def update_neighbors(self):
        for neighbor in self.neighbors:
            if neighbor[0].cost_to == -1 or self.cost_to + neighbor[1] < neighbor[0].cost_to:
                neighbor[0].father = self
                neighbor[0].cost_to = self.cost_to + neighbor[1]
