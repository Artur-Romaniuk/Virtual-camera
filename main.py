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


def is_point_visible(point_3d: np.array, focal: int) -> bool:
    return point_3d[1] > focal


def translate_3d_to_2d(point_3d: np.array, view_width: int, view_heigh: int, focal: int) -> tuple[int, int]:
    # If the point is not in front of the camera, return None
    if not is_point_visible(point_3d, focal):
        return None

    # Calculate the scaling factor
    scale = focal / point_3d[1]

    # Translate the point
    return scale * point_3d[0] + view_width / 2, view_heigh / 2 - scale * point_3d[2]


def translation_matrix(dx: int, dy: int, dz: int) -> np.array:
    matrix = np.eye(4)
    matrix[-1][:3] = dx, dy, dz

    return matrix


def rotation_matrix(radians: int, axis: str) -> np.array:
    sin = np.sin(radians)
    cos = np.cos(radians)
    matrix = np.eye(4)
    if axis == 'x':
        matrix[1:3, 1:3] = np.array([cos, -sin, sin, cos]).reshape(2, 2)
    elif axis == 'y':
        matrix[0, 0] = cos
        matrix[2, 0] = sin
        matrix[2, 0] = -sin
        matrix[2, 2] = cos
    elif axis == 'z':
        matrix[0:2, 0:2] = np.array([cos, -sin, sin, cos]).reshape(2, 2)

    return matrix


def draw(canvas: tk.Canvas, models: list[Model], focal: int) -> None:
    canvas.delete("all")
    canvas.winfo_toplevel().update()
    for model in models:
        for node in model.nodes:
            if is_point_visible(node, focal):
                center = translate_3d_to_2d(
                    node, canvas.winfo_reqwidth(), canvas.winfo_reqheight(), focal)
                canvas.create_oval((center[0] - 1, center[1] -
                                    1, center[0] + 1, center[1] + 1))
        for edge in model.edges:
            a, b = model.nodes[edge[0]], model.nodes[edge[1]]
            if is_point_visible(a, focal) and is_point_visible(b, focal):
                ax, ay = translate_3d_to_2d(
                    a, canvas.winfo_reqwidth(), canvas.winfo_reqheight(), focal)
                bx, by = translate_3d_to_2d(
                    b, canvas.winfo_reqwidth(), canvas.winfo_reqheight(), focal)
                canvas.create_line((ax, ay, bx, by))


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
FORWARD_TRANSLATION = translation_matrix(0, -TRANSLATION_STEP, 0)
root.bind('w', lambda event: transform_and_draw(
    canvas, models, FORWARD_TRANSLATION, focal_length))
BACKWARD_TRANSLATION = translation_matrix(0, +TRANSLATION_STEP, 0)
root.bind('s', lambda event: transform_and_draw(
    canvas, models, BACKWARD_TRANSLATION, focal_length))
LEFT_TRANSLATION = translation_matrix(TRANSLATION_STEP, 0, 0)
root.bind('a', lambda event: transform_and_draw(
    canvas, models, LEFT_TRANSLATION, focal_length))
RIGHT_TRANSLATION = translation_matrix(-TRANSLATION_STEP, 0, 0)
root.bind('d', lambda event: transform_and_draw(
    canvas, models, RIGHT_TRANSLATION, focal_length))
UP_TRANSLATION = translation_matrix(0, 0, -TRANSLATION_STEP)
root.bind('<space>', lambda event: transform_and_draw(
    canvas, models, UP_TRANSLATION, focal_length))
DOWN_TRANSLATION = translation_matrix(0, 0, +TRANSLATION_STEP)
root.bind('<Shift_L>', lambda event: transform_and_draw(
    canvas, models, DOWN_TRANSLATION, focal_length))

ROTATION_STEP = np.radians(5)
COUNTER_CLOCKWISE_ROTATION = rotation_matrix(ROTATION_STEP, 'z')
CLOCKWISE_ROTATION = rotation_matrix(-ROTATION_STEP, 'z')
PITCH_UP_ROTATION = rotation_matrix(ROTATION_STEP, 'x')
PITCH_DOWN_ROTATION = rotation_matrix(-ROTATION_STEP, 'x')
LEFT_ROTATION = rotation_matrix(ROTATION_STEP, 'y')
RIGHT_ROTATION = rotation_matrix(-ROTATION_STEP, 'y')

root.bind('q', lambda event: transform_and_draw(
    canvas, models, COUNTER_CLOCKWISE_ROTATION, focal_length))
root.bind('e', lambda event: transform_and_draw(
    canvas, models, CLOCKWISE_ROTATION, focal_length))
root.bind('r', lambda event: transform_and_draw(
    canvas, models, PITCH_UP_ROTATION, focal_length))
root.bind('f', lambda event: transform_and_draw(
    canvas, models, PITCH_DOWN_ROTATION, focal_length))

root.mainloop()
