from typing import List
from tkinter import *
from custom_datatypes import *
from PIL import ImageGrab, Image

def visualize_fire(forest_map: List[List[MapNode]], canvas) -> None:
    for i in range(len(forest_map)):
        for j in range(len(forest_map[0])):
            mb = 500 / len(forest_map)
            mh = 500 / len(forest_map[0])
            if forest_map[i][j].status == NodeStatus.INTACT:
                canvas.create_rectangle(i * mb, j * mh, (i * mb) + 100, (j * mh) + 100, fill="green")
            elif forest_map[i][j].status == NodeStatus.BURNING:
                canvas.create_rectangle(i * mb, j * mh, (i * mb) + 100, (j * mh) + 100, fill="red")
            elif forest_map[i][j].status == NodeStatus.BURNT_DOWN:
                canvas.create_rectangle(i * mb, j * mh, (i * mb) + 100, (j * mh) + 100, fill="black")
            elif forest_map[i][j].status == NodeStatus.CANNOT_BURN:
                canvas.create_rectangle(i * mb, j * mh, (i * mb) + 100, (j * mh) + 100, fill="grey")


def append_frame(canvas, frames):
    canvas.update()
    x = canvas.winfo_rootx()
    y = canvas.winfo_rooty()
    dx = x + canvas.winfo_width()
    dy = y + canvas.winfo_height()
    img = ImageGrab.grab((x, y, dx, dy))
    frames.append(img.convert("P", palette=Image.ADAPTIVE))