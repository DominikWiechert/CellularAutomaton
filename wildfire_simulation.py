from pathlib import Path

from input import get_forest_map
from output import visualize_fire, append_frame
from process import run_simulation_step, log, print_map_2_console, calculate_probability
from custom_datatypes import NodeStatus
import time
from ctypes import windll
import tkinter as tk
from tkinter import filedialog, ttk

try:
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

def run_simulation(root: tk.Tk, canvas: tk.Canvas, map_path: Path):
    forest_map = get_forest_map(map_path=Path(map_path), max_axis_length=100)

    t_max = 20
    tick_speed = 0.1 #[s]

    prob = calculate_probability()

    forest_map[15][15].status = NodeStatus.BURNING

    frames = []
    for t in range(t_max):
        log("Step: " + str(t))
        time.sleep(tick_speed)
        forest_map = run_simulation_step(forest_map,prob)
        visualize_fire(forest_map, canvas)
        append_frame(canvas, frames)
        root.update_idletasks()
        root.update()

    log("Simulation end")
    frames[0].save("waldbrandausbreitung_testing.gif", save_all=True, append_images=frames[1:], duration=500, loop=0,
                   disposal=2)

def run_gui():
    # TODO: Load and save stuff from config.yaml
    # TODO: Layout!!!!
    # TODO: Feed values from entries into run_simulation, get_forest_map and other methods
    # TODO: Verify inputs (type, min, max)

    # Init root window
    root = tk.Tk()
    root.title("Wildfire Simulation")
    root.geometry("500x600")

    # Init tabs
    notebook = ttk.Notebook(root)
    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)
    notebook.add(tab1, text="Simulation")
    notebook.add(tab2, text="Settings")
    notebook.pack(expand=1, fill='both')

    # Init contents
    canvas = tk.Canvas(tab1, width=500, height=500)
    canvas.pack()

    path_entry = tk.Entry(tab2, width=100)
    path_entry.insert(0, str(Path.cwd() / 'map_pictures' / 'osm_map.png'))
    path_entry.pack()

    def select_file(entry: tk.Entry):
        file_path = tk.filedialog.askopenfilename(
            title="Select a file",
            filetypes=(("PNG Files", "*.png"), ("All files", "*.*"))
        )
        if file_path:
            entry.delete(0, tk.END)
            entry.insert(0, file_path)
        map = get_forest_map(map_path=Path(entry.get()), max_axis_length=100)
        visualize_fire(map, canvas)
    select_file_button = tk.Button(tab2, text="Select File", command=lambda: select_file(path_entry))
    select_file_button.pack()

    run_button = tk.Button(tab1, text="Run Simulation",
                       command=lambda: run_simulation(root, canvas, Path(path_entry.get())))
    run_button.pack()

    forest_map = get_forest_map(map_path=Path(path_entry.get()), max_axis_length=100)
    visualize_fire(forest_map, canvas)

    t_max_label = tk.Label(tab2, text="Simulation Time:")
    t_max_label.pack()
    t_max_entry = tk.Entry(tab2, width=100)
    t_max_entry.insert(0, '20')
    t_max_entry.pack()

    tick_speed_label = tk.Label(tab2, text="Tick speed:")
    tick_speed_label.pack()
    tick_speed_entry = tk.Entry(tab2, width=100)
    tick_speed_entry.insert(0, '0.1')
    tick_speed_entry.pack()

    max_axis_length_label = tk.Label(tab2, text="max_axis_length:")
    max_axis_length_label.pack()
    max_axis_length_entry = tk.Entry(tab2, width=100)
    max_axis_length_entry.insert(0, '100')
    max_axis_length_entry.pack()

    probability_label = tk.Label(tab2, text="probability:")
    probability_label.pack()
    probability_entry = tk.Entry(tab2, width=100)
    probability_entry.insert(0, '30')
    probability_entry.pack()

    wind_speed_x_label = tk.Label(tab2, text="wind_speed_x:")
    wind_speed_x_label.pack()
    wind_speed_x_entry = tk.Entry(tab2, width=100)
    wind_speed_x_entry.insert(0, '-80')
    wind_speed_x_entry.pack()

    wind_speed_y_label = tk.Label(tab2, text="wind_speed_y:")
    wind_speed_y_label.pack()
    wind_speed_y_entry = tk.Entry(tab2, width=100)
    wind_speed_y_entry.insert(0, '-50')
    wind_speed_y_entry.pack()

    log("GUI initialized")
    root.mainloop()

if __name__ == "__main__":
    run_gui()