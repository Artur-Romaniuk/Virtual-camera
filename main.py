from enum import Enum
from os import listdir
from os.path import isfile, join
import tkinter as tk
import numpy as np
from model import Model


def load_models(dir: str) -> list[Model]:
    # Get all files in the directory
    files = [f for f in listdir(dir) if isfile(join(dir, f))]
    # Load each file in the directory as a model
    models = []
    for f in files:
        try:
            models.append(Model.load_from_file(join(dir, f)))
        except Exception as e:
            print(f"Failed to load {f}: {e}")
    return models


def project_point_to_2d(point_3d: np.array, view_width: int, view_heigh: int, focal: int) -> tuple[int, int]:
    # If the point is not in front of the camera, return None
    if point_3d[2] <= focal:
        return None

    # Calculate the scaling factor
    scale = focal / point_3d[2]

    # Translate the point
    return scale * point_3d[0] + view_width / 2, view_heigh / 2 - scale * point_3d[1]
    # return point_3d[0] * focal / point_3d[1] + view_width / 2, view_heigh / 2 - focal * point_3d[2] / point_3d[2]


def translation_matrix(dx: int, dy: int, dz: int) -> np.array:
    matrix = np.eye(4)
    matrix[-1][:3] = dx, dy, dz

    return matrix


class RotationAxis(Enum):
    X = 0
    Y = 1
    Z = 2


def rotation_matrix(radians: int, axis: RotationAxis) -> np.array:
    sin = np.sin(radians)
    cos = np.cos(radians)
    matrix = np.eye(4)
    if axis == RotationAxis.X:
        matrix[1][1] = cos
        matrix[1][2] = -sin
        matrix[2][1] = sin
        matrix[2][2] = cos
    elif axis == RotationAxis.Y:
        matrix[0][0] = cos
        matrix[0][2] = sin
        matrix[2][0] = -sin
        matrix[2][2] = cos
    elif axis == RotationAxis.Z:
        matrix[0][0] = cos
        matrix[0][1] = -sin
        matrix[1][0] = sin
        matrix[1][1] = cos

    return matrix


def draw(canvas: tk.Canvas, models: list[Model], focal: int) -> None:
    canvas.delete("all")
    canvas.winfo_toplevel().update()
    for model in models:
        for node in model.nodes:
            center = project_point_to_2d(
                node, canvas.winfo_reqwidth(), canvas.winfo_reqheight(), focal)
            if center is not None:
                canvas.create_oval((center[0] - 1, center[1] -
                                    1, center[0] + 1, center[1] + 1))
        for edge in model.edges:
            node1, node2 = model.nodes[edge[0]], model.nodes[edge[1]]
            node1 = project_point_to_2d(
                node1, canvas.winfo_reqwidth(), canvas.winfo_reqheight(), focal)
            node2 = project_point_to_2d(
                node2, canvas.winfo_reqwidth(), canvas.winfo_reqheight(), focal)
            if node1 is not None and node2 is not None:
                canvas.create_line((node1[0], node1[1], node2[0], node2[1]))


def transform_and_draw(canvas: tk.Canvas, models: list[Model], matrix: np.array, focal: int) -> None:
    for model in models:
        model.transform(matrix)
    draw(canvas, models, focal)


focal_length = 500


def change_focal_and_draw(canvas: tk.Canvas, models: list[Model], delta: int) -> None:
    global focal_length
    FOCAL_LENGTH_MAX = 1000
    FOCAL_LENGTH_MIN = 100
    if FOCAL_LENGTH_MIN <= focal_length + delta <= FOCAL_LENGTH_MAX:
        focal_length += delta
        draw(canvas, models, focal_length)


root = tk.Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
INIT_SCREEN_SIZE = (500, 500)
canvas = tk.Canvas(
    root, width=INIT_SCREEN_SIZE[0], height=INIT_SCREEN_SIZE[1], bg="white")
canvas.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
canvas.pack(fill="both", expand=True)

models = load_models('models')
draw(canvas, models, focal_length)

root.bind('<Escape>', lambda event: root.destroy())

FOCAL_STEP = 10
root.bind('=', lambda event: change_focal_and_draw(canvas, models, FOCAL_STEP))
root.bind('-', lambda event: change_focal_and_draw(canvas, models, -FOCAL_STEP))

TRANSLATION_STEP = 50
FORWARD_TRANSLATION = translation_matrix(0, 0, -TRANSLATION_STEP)
root.bind('w', lambda event: transform_and_draw(
    canvas, models, FORWARD_TRANSLATION, focal_length))
BACKWARD_TRANSLATION = translation_matrix(0, 0, TRANSLATION_STEP)
root.bind('s', lambda event: transform_and_draw(
    canvas, models, BACKWARD_TRANSLATION, focal_length))
LEFT_TRANSLATION = translation_matrix(TRANSLATION_STEP, 0, 0)
root.bind('a', lambda event: transform_and_draw(
    canvas, models, LEFT_TRANSLATION, focal_length))
RIGHT_TRANSLATION = translation_matrix(-TRANSLATION_STEP, 0, 0)
root.bind('d', lambda event: transform_and_draw(
    canvas, models, RIGHT_TRANSLATION, focal_length))
UP_TRANSLATION = translation_matrix(0, -TRANSLATION_STEP, 0)
root.bind('<space>', lambda event: transform_and_draw(
    canvas, models, UP_TRANSLATION, focal_length))
DOWN_TRANSLATION = translation_matrix(0, TRANSLATION_STEP, 0)
root.bind('<Shift_L>', lambda event: transform_and_draw(
    canvas, models, DOWN_TRANSLATION, focal_length))

ROTATION_STEP = np.radians(5)
COUNTER_CLOCKWISE_ROTATION = rotation_matrix(ROTATION_STEP, RotationAxis.Z)
root.bind('z', lambda event: transform_and_draw(
    canvas, models, COUNTER_CLOCKWISE_ROTATION, focal_length))
CLOCKWISE_ROTATION = rotation_matrix(-ROTATION_STEP, RotationAxis.Z)
root.bind('x', lambda event: transform_and_draw(
    canvas, models, CLOCKWISE_ROTATION, focal_length))
PITCH_UP_ROTATION = rotation_matrix(ROTATION_STEP, RotationAxis.X)
root.bind('r', lambda event: transform_and_draw(
    canvas, models, PITCH_UP_ROTATION, focal_length))
PITCH_DOWN_ROTATION = rotation_matrix(-ROTATION_STEP, RotationAxis.X)
root.bind('f', lambda event: transform_and_draw(
    canvas, models, PITCH_DOWN_ROTATION, focal_length))
LEFT_ROTATION = rotation_matrix(ROTATION_STEP, RotationAxis.Y)
root.bind('e', lambda event: transform_and_draw(
    canvas, models, LEFT_ROTATION, focal_length))
RIGHT_ROTATION = rotation_matrix(-ROTATION_STEP, RotationAxis.Y)
root.bind('q', lambda event: transform_and_draw(
    canvas, models, RIGHT_ROTATION, focal_length))

root.mainloop()
