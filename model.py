import numpy as np


class Model:

    def __init__(self):
        super().__init__()
        self.nodes = np.zeros([0, 4])  # x, y, z, 1
        self.edges = []  # tuples of node indexes

    def transform(self, matrix: np.array) -> None:
        self.nodes = self.nodes @ matrix

    @staticmethod
    def load_from_file(file_name: str):
        model = Model()
        loaded_points = {}

        with open(file_name, 'r') as file:
            i = 0
            for line in file.readlines():
                edge = [float(p) for p in line.split(', ')]
                p1 = tuple(edge[:3])
                p2 = tuple(edge[3:])

                if not p1 in loaded_points:
                    loaded_points[p1] = i
                    i += 1
                if not p2 in loaded_points:
                    loaded_points[p2] = i
                    i += 1

                model.edges.append((loaded_points[p1], loaded_points[p2]))

        points = np.array(list(zip(*loaded_points.items()))[0])
        model.nodes = np.hstack([points,
                                 np.ones([points.shape[0], 1])])

        return model
