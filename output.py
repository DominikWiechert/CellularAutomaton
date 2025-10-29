from typing import List
from tkinter import *
from custom_datatypes import *
from process import log

def init_gui():
    window = Tk()
    window.geometry("500x500")
    canvas = Canvas(window, width=500, height=500)
    canvas.pack()
    log("GUI initialized")
    return window, canvas

def visualize_fire(forest_map: List[List[MapNode]], window, canvas) -> None:
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