from typing import List
from tkinter import *
from custom_datatypes import *
from PIL import ImageGrab, Image

def visualize_fire(forest_map: List[List[MapNode]], canvas) -> None:
    #calculate pixel size
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()

    number_of_nodes_width = len(forest_map)
    number_of_nodes_height = len(forest_map[0])
    print(number_of_nodes_width, number_of_nodes_height)

    cell_width = canvas_width / number_of_nodes_width
    cell_height = canvas_height / number_of_nodes_height
    for i in range(len(forest_map)):
        for j in range(len(forest_map[0])):
            if forest_map[i][j].status == NodeStatus.INTACT:
                canvas.create_rectangle(i * cell_width, j * cell_height, (i+1) * cell_width, (j+1) * cell_height, fill="green")
            elif forest_map[i][j].status == NodeStatus.CROWN_BURNING:
                canvas.create_rectangle(i * cell_width, j * cell_height, (i+1) * cell_width, (j+1) * cell_height, fill="red")
            elif forest_map[i][j].status == NodeStatus.BURNT_DOWN:
                canvas.create_rectangle(i * cell_width, j * cell_height, (i+1) * cell_width, (j+1) * cell_height, fill="black")
            elif forest_map[i][j].status == NodeStatus.CANNOT_BURN:
                canvas.create_rectangle(i * cell_width, j * cell_height, (i+1) * cell_width, (j+1) * cell_height, fill="grey")
            elif forest_map[i][j].status == NodeStatus.LOWER_BURNING:
                canvas.create_rectangle(i * cell_width, j * cell_height, (i+1) * cell_width, (j+1) * cell_height, fill="orange")


def simplified_visualize_fire(forest_map, canvas) -> None:
    #calculate pixel size
    canvas_width = canvas.winfo_reqwidth()
    canvas_height = canvas.winfo_reqheight()

    number_of_nodes_width = len(forest_map)
    number_of_nodes_height = len(forest_map[0])

    cell_width = canvas_width / number_of_nodes_width
    cell_height = canvas_height / number_of_nodes_height
    for i in range(len(forest_map)):
        for j in range(len(forest_map[0])):
          #  print(forest_map[i][j])
       #     print(i,j)
            canvas.create_rectangle(i * cell_width, j * cell_height, (i+1) * cell_width, (j+1) * cell_height, fill=forest_map[i,j])

#TODO: Unterscheidung bodenfeuer->orange, Kronenfeuer->rot
#TODO: Surface_Burning -> yellow
#TODO: Ladder_Burning -> orange
#TODO: Crown_Burning -> red

#TODO: Ändern das vorgerechnet wird, gespeichert in 3d matrix mit 2d farben und 1d zeitleiste


def append_frame(canvas, frames):
    canvas.update()
    x = canvas.winfo_rootx()
    y = canvas.winfo_rooty()
    dx = x + canvas.winfo_width()
    dy = y + canvas.winfo_height()
    img = ImageGrab.grab((x, y, dx, dy))
    frames.append(img.convert("P", palette=Image.ADAPTIVE))

def render_optimised_forward(map,canvas,cell_width,cell_height):
    for i in range(len(map)):
            canvas.create_rectangle(map[i].x * cell_width, map[i].y * cell_height, (map[i].x+1) * cell_width, (map[i].y+1) * cell_height, fill=map[i].color)

def render_optimised_backward(map,canvas,cell_width,cell_height):
    for i in range(len(map)):
            canvas.create_rectangle(map[i].x * cell_width, map[i].y * cell_height, (map[i].x+1) * cell_width, (map[i].y+1) * cell_height, fill=map[i].old_color)