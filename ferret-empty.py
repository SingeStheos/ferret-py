#       FERRET-PY
#    by Singe Stheos
#      MIT License
# https://github.com/SingeStheos/ferret-py

import math
import tkinter as tk
import base64
import random

# window dimensions and settings
WIDTH = 600
HEIGHT = WIDTH
PIXEL_SIZE = 1
FOV = 30
VIEWER_DISTANCE = 10 # !! you may need to change this.

label = [
    "Put things in here",
    "That you want",
    "The script to say",
    "At the top."
]

# default face color (missing material debug color)
DEFAULT_COLOR = "#FF5733"

# OBJ and MTL data as strings
OBJ_DATA = """

"""

MTL_DATA = """

"""

# this is the png data of the icon of the script, in base64 format
ICON_DATA = """

"""

# perspective projection function without aspect ratio distortion
def project_vertex(vertex, fov, viewer_distance):
    x, y, z = vertex
    factor = fov / (viewer_distance + z + 1e-5)
    x_proj = x * factor
    y_proj = y * factor
    return x_proj, y_proj, z

# rotate vertices around X, Y, Z axes
def rotate_vertex(vertex, angle_x, angle_y, angle_z):
    x, y, z = vertex
    y, z = y * math.cos(angle_x) - z * math.sin(angle_x), y * math.sin(angle_x) + z * math.cos(angle_x)
    x, z = x * math.cos(angle_y) + z * math.sin(angle_y), -x * math.sin(angle_y) + z * math.cos(angle_y)
    x, y = x * math.cos(angle_z) - y * math.sin(angle_z), x * math.sin(angle_z) + y * math.cos(angle_z)
    return x, y, z

# compute average Z for a face
def average_z(face_vertices):
    return sum(vertex[2] for vertex in face_vertices) / len(face_vertices)

# parse OBJ data from the OBJ_DATA string
def load_obj_data():
    vertices = []
    faces = []
    materials = load_mtl_data()  # load materials from MTL_DATA
    current_material = DEFAULT_COLOR

    for line in OBJ_DATA.splitlines():
        if line.startswith("v "):  # vertex data
            _, x, y, z = line.split()
            vertices.append((float(x), float(y), float(z)))
        elif line.startswith("f "):  # face data
            face = [int(idx.split('/')[0]) - 1 for idx in line.split()[1:]]
            faces.append((face, current_material))
        elif line.startswith("usemtl "):  # use material
            material_name = line.split()[1]
            current_material = materials.get(material_name, DEFAULT_COLOR)

    return vertices, faces

# parse MTL data from the MTL_DATA string
def load_mtl_data():
    materials = {}
    current_material = None

    for line in MTL_DATA.splitlines():
        if line.startswith("newmtl "):  # start new material
            current_material = line.split()[1]
        elif line.startswith("Kd ") and current_material:  # diffuse color
            r, g, b = map(float, line.split()[1:])
            hex_color = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
            materials[current_material] = hex_color

    return materials

def render_object(canvas, vertices, faces, angle_x, angle_y, angle_z, fov, viewer_distance):
    canvas.delete("all")  # clear previous frame
    face_data = []

    for face, color in faces:
        face_rotated = [rotate_vertex(vertices[i], angle_x, angle_y, angle_z) for i in face]
        avg_z = average_z(face_rotated)
        projected_vertices = [project_vertex(v, fov, viewer_distance) for v in face_rotated]
        face_data.append((projected_vertices, avg_z, color))

    # sort faces by average Z, farthest first
    face_data.sort(key=lambda item: item[1], reverse=True)

    for projected_vertices, _, color in face_data:
        screen_coords = [
            (int(WIDTH / 2 + vx * WIDTH / 2), int(HEIGHT / 2 - vy * HEIGHT / 2))
            for vx, vy, vz in projected_vertices
        ]
        canvas.create_polygon(screen_coords, fill=color, outline="")

    canvas.update()

# main animation loop
def animate():
    global angle_x, angle_y, angle_z
    render_object(canvas, vertices, faces, angle_x, angle_y, angle_z, fov=FOV, viewer_distance=VIEWER_DISTANCE)
    angle_x += 0.02
    angle_y += 0.015
    angle_z += 0.01
    root.after(16, animate)  # ~60 FPS

# initialize tkinter window
root = tk.Tk()

icon_image = tk.PhotoImage(data=ICON_DATA)
root.iconphoto(True, icon_image)
root.title("ferret.exe - " + random.choice(label))
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
canvas.pack()

# set initial rotation angles
angle_x = angle_y = angle_z = 0

# load OBJ and MTL data
vertices, faces = load_obj_data()

# start animation
animate()
root.mainloop()