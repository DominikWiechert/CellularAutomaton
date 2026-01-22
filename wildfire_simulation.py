from pathlib import Path

import yaml
from fsspec.asyn import running_async

from input import get_forest_map
from output import visualize_fire, append_frame, simplified_visualize_fire, render_optimised
from process import run_simulation_step, log, print_map_2_console, calculate_probability, simplify_forest_map, count_cells, optimised_render
from custom_datatypes import NodeStatus, OptimisedCell
import time
from ctypes import windll
import tkinter as tk
from tkinter import filedialog, ttk,messagebox
#import sv_ttk
from matplotlib import pyplot as plt

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
import numpy as np

try:
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

#global varables
fm = 0
current_step = 0
t_max = 0
playing = False
tick_speed = 500
optimised_matrix = []
###################

def run_simulation(root: tk.Tk, canvas: tk.Canvas, config_path: Path):
    # Hinweis: Parameter stehen jetzt alle in der yaml config path
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    forest_map = get_forest_map(map_path=Path(config['path']), max_axis_length=100)

    t_max = config['t_max']
    tick_speed = config['tick_speed'] #[s]

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
    # TODO: Feed values from entries into run_simulation, get_forest_map and other methods
    # TODO: Verify inputs (type, min, max)

    # Init root window
    log("Init pre-processing GUI...")
    root = tk.Tk()
    root.title("Wildfire Simulation - Pre-Processing")
    root.geometry("1800x800")

    # Init contents
    #canvas = tk.Canvas(tab1, width=1000, height=1000)
    #canvas.pack(fill= "both", expand=1)

    config_path = Path('config.yaml')
    path_entry_label = tk.Label(root, text="Map picture path:")
    path_entry_label.grid(row=0, column=0, padx=10, pady=10)
    path_entry = tk.Entry(root, width=100)
    path_entry.grid(row=0, column=1,columnspan=2, padx=10, pady=10)

    def update_map_visualization():
        forest_map = get_forest_map(map_path=Path(path_entry.get()), max_axis_length=100)
      #  visualize_fire(forest_map, canvas)

    def select_file(entry: tk.Entry):
        file_path = tk.filedialog.askopenfilename(
            title="Select a file",
            filetypes=(("PNG Files", "*.png"), ("All files", "*.*"))
        )
        if file_path:
            entry.delete(0, tk.END)
            entry.insert(0, file_path)
        update_map_visualization()

    select_file_button = tk.Button(root, text="Select File", command=lambda: select_file(path_entry))
    select_file_button.grid(row=0, column=3, padx=10, pady=10)

    t_max_label = tk.Label(root, text="Simulation Time:")
    t_max_label.grid(row=1, column=0, padx=10, pady=10)
    t_max_entry = tk.Entry(root, width=100)
    t_max_entry.grid(row=1, column=1,columnspan=3,sticky="we", padx=10, pady=10)

    tick_speed_label = tk.Label(root, text="Tick speed:")
    tick_speed_label.grid(row=2, column=0, padx=10, pady=10)
    tick_speed_entry = tk.Entry(root, width=100)
    tick_speed_entry.grid(row=2, column=1,columnspan=3,sticky="we", padx=10, pady=10)

    max_axis_length_label = tk.Label(root, text="max_axis_length:")
    max_axis_length_label.grid(row=3, column=0, padx=10, pady=10)
    max_axis_length_entry = tk.Entry(root, width=100)
    max_axis_length_entry.grid(row=3, column=1,columnspan=3,sticky="we", padx=10, pady=10)

    probability_label = tk.Label(root, text="probability:")
    probability_label.grid(row=4, column=0, padx=10, pady=10)
    probability_entry = tk.Entry(root, width=100)
    probability_entry.grid(row=4, column=1,columnspan=3,sticky="we", padx=10, pady=10)

    wind_speed_x_label = tk.Label(root, text="wind_speed_x:")
    wind_speed_x_label.grid(row=5, column=0, padx=10, pady=10)
    wind_speed_x_entry = tk.Entry(root, width=100)
    wind_speed_x_entry.grid(row=5, column=1,columnspan=3,sticky="we", padx=10, pady=10)

    wind_speed_y_label = tk.Label(root, text="wind_speed_y:")
    wind_speed_y_label.grid(row=6, column=0, padx=10, pady=10)
    wind_speed_y_entry = tk.Entry(root, width=100)
    wind_speed_y_entry.grid(row=6, column=1,columnspan=3,sticky="we", padx=10, pady=10)

    def update_config_values(config_path):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        path_entry.delete(0, tk.END)
        path_entry.insert(0, config['path'])
        t_max_entry.delete(0, tk.END)
        t_max_entry.insert(0, config['t_max'])
        tick_speed_entry.delete(0, tk.END)
        tick_speed_entry.insert(0, config['tick_speed'])
        max_axis_length_entry.delete(0, tk.END)
        max_axis_length_entry.insert(0, config['max_axis_length'])
        probability_entry.delete(0, tk.END)
        probability_entry.insert(0, config['probability'])
        wind_speed_x_entry.delete(0, tk.END)
        wind_speed_x_entry.insert(0, config['wind_speed_x'])
        wind_speed_y_entry.delete(0, tk.END)
        wind_speed_y_entry.insert(0, config['wind_speed_y'])
    update_config_values(config_path)

    def save_entries_to_config():
        config_data = {
            'path': str(path_entry.get()),
            't_max': int(t_max_entry.get()),
            'tick_speed': float(tick_speed_entry.get()),
            'max_axis_length': float(max_axis_length_entry.get()),
            'probability': float(probability_entry.get()),
            'wind_speed_x': float(wind_speed_x_entry.get()),
            'wind_speed_y': float(wind_speed_y_entry.get())
        }
        # TODO: Select file path for yaml. Might use asksaveasfile method from tkinter.
        with open("config.yaml", 'w') as file:
            yaml.dump(config_data, file)
        log('Data saved to config.yaml')
    save_config_button = tk.Button(root, text="Save Config as...", command=save_entries_to_config)
    save_config_button.grid(row=8, column=0, padx=10, pady=10)

    def load_config_from_file():
        file_path = tk.filedialog.askopenfilename(
            title="Select a file",
            filetypes=(("YAML Files", "*.yaml"), ("All files", "*.*"))
        )
        if file_path:
            config_path = Path(file_path)
            update_config_values(config_path)
            update_map_visualization()

    def run_calculation():
        #TODO: calculate -> only save needed var and delete the others -> change to new window
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        forest_map = get_forest_map(map_path=Path(config['path']), max_axis_length=100)
        global t_max
        t_max = config['t_max']
        global tick_speed
        tick_speed = config['tick_speed']  # [s]

        prob = calculate_probability()

        forest_map[15][15].status = NodeStatus.BURNING

        precent_step = t_max / 50
        progress = 0

        simplified_forest_matrix = np.empty([len(forest_map), len(forest_map[0]),t_max], dtype="S10")
        global fm
        fm = np.empty([len(forest_map), len(forest_map[0]),t_max], dtype="S10")
        opti = []
        timeline = np.zeros([6,t_max])
        for t in range(t_max):
            log("Step: " + str(t))
            time.sleep(tick_speed)
            forest_map = run_simulation_step(forest_map, prob)
            simplified_forest_matrix[:,:,t] = simplify_forest_map(forest_map)
            fm[:, :, t] = simplify_forest_map(forest_map)

            timeline[0,t] = t
            timeline[1:6,t] = count_cells(fm[:, :, t])[:,0]
            progress += precent_step
            pbar.step(progress)
            root.update_idletasks()
            root.update()
        global optimised_matrix
        for i in range(t_max-1):
            optimised_matrix.append(optimised_render(fm[:, :, i], fm[:, :, i+1]))

        log("Simulation end")
        messagebox.showinfo("Calculation Results", "Calculation completed.")

        pbar_label.grid_forget()
        probability_label.grid_forget()
        wind_speed_x_label.grid_forget()
        t_max_label.grid_forget()
        tick_speed_label.grid_forget()
        max_axis_length_label.grid_forget()
        path_entry_label.grid_forget()
        wind_speed_y_label.grid_forget()

        path_entry.grid_forget()
        t_max_entry.grid_forget()
        tick_speed_entry.grid_forget()
        max_axis_length_entry.grid_forget()
        probability_entry.grid_forget()
        wind_speed_x_entry.grid_forget()
        wind_speed_y_entry.grid_forget()

        pbar.grid_forget()
        select_file_button.grid_forget()
        save_config_button.grid_forget()
        load_config_button.grid_forget()
        calculate_button.grid_forget()
        load_post_pros_button.grid_forget()

        #load post ops gui
        root.title("Wildfire - Post-processing")
        root.geometry("2000x1200")
        #canvas_automat = tk.Canvas(root, width=730, height=730 )

        canvas_automat.grid(row=0, column=0, columnspan=20)
        slider_label.grid(row=1, column=0, sticky='w')
        slider.grid(row=1, column=1, columnspan=19, sticky='we')

        b1.grid(row=2, column=8)
        b2.grid(row=2, column=9)
        b3.grid(row=2, column=10)
        b4.grid(row=2, column=11)
        b5.grid(row=2, column=12)

        canvas_plot.get_tk_widget().grid(row=0, column=21, columnspan=10, sticky='e')

        b6.grid(row=2, column=24)
        b7.grid(row=2, column=25)
        b8.grid(row=2, column=26)
        plot(timeline)
        simplified_visualize_fire(simplified_forest_matrix[:,:,0],canvas_automat)
        return simplified_forest_matrix

    def load_post_pros():
        #TODO: tbi
        print("platzhalter")

    load_config_button = tk.Button(root, text="Load Config", command=load_config_from_file)
    load_config_button.grid(row=8, column=1, padx=10, pady=10)
    calculate_button = tk.Button(root, text="Run calculation", command=run_calculation)
    calculate_button.grid(row=8, column=2, padx=10, pady=10)
    load_post_pros_button = tk.Button(root, text="Load calculation", command=load_post_pros)
    load_post_pros_button.grid(row=8, column=3, padx=10, pady=10)

    pbar_label = tk.Label(root, text="Progress:")
    pbar_label.grid(row=9, column=0, padx=10, pady=10)
    pbar = ttk.Progressbar(root, orient="horizontal",length=100,mode='determinate')
    pbar.grid(row=9, column=1, sticky="we",columnspan=3,padx=10, pady=10)

    #Init Post process gui


    def plot(timeline):
        x = timeline[0,:]
        ax.set_ylabel("number of cells [1]")
        ax.set_xlabel("time steps [1]")
        ax.plot(x,timeline[1,:],color='green',label='Tree')
        ax.plot(x,timeline[2,:],color='red',label='Burning')
        ax.plot(x, timeline[3, :], color='black', label='Burned down')
        ax.plot(x, timeline[4, :], color='grey', label='Unburnable')
        ax.grid(True)
        canvas_plot.draw()


    def next_button():
        global current_step
        if current_step == t_max -1:
            log("Last step reached")
        else:
            current_step = current_step+  1
            log("Step: " + str(current_step))
        simplified_visualize_fire(fm[:,:,current_step],canvas_automat)

    def previous_button():
        global current_step
        if current_step >=1:
            current_step = current_step - 1
            log("Step: " + str(current_step))
        else:
            log("First step reached")
        simplified_visualize_fire(fm[:,:,current_step],canvas_automat)

    def first_button():
        global current_step
        current_step = 0
        log("Step: " + str(current_step))
        simplified_visualize_fire(fm[:,:,current_step],canvas_automat)

    def last_button():
        global current_step
        current_step = t_max-1
        log("Step: " + str(current_step))
        simplified_visualize_fire(fm[:,:,current_step],canvas_automat)

    def play_button():
        global current_step, playing
        if playing == True:
            playing = False
            b3.config(text="▶")
        else:
            playing = True
            b3.config(text="⏸")
            run_animation()

    def run_animation():
        global current_step,playing,tick_speed
        if playing == True:
            if current_step == t_max-2:
                playing = False
                b3.config(text="▶")
            else:
                current_step = current_step + 1
                log("Step: " + str(current_step))
              #  simplified_visualize_fire(fm[:, :, current_step], canvas_automat)
                render_optimised(optimised_matrix[current_step],canvas_automat,54,100)
                root.after(int(tick_speed), lambda: run_animation())


    def slider_changed(event):
        global tick_speed
        slider_label.config(text = f'tick speed = {int(slider.get()):04} ms')
        tick_speed = int(slider.get())

    fig, ax = plt.subplots()

    canvas_automat = tk.Canvas(root, width=730, height=730, bg="red")
    slider_label = ttk.Label(root, text = f'tick speed = {int(tick_speed):04} ms')
    slider = ttk.Scale(root, from_=1, to=1000,value=500, orient='horizontal', command=slider_changed)
    b1 = ttk.Button(root, text="⏮", command=first_button)
    b2 = ttk.Button(root, text="<", command=previous_button)
    b3 = ttk.Button(root, text="▶", command=play_button)
    b4 = ttk.Button(root, text=">",command=next_button)
    b5 = ttk.Button(root, text="⏭",command=last_button)

    canvas_plot = FigureCanvasTkAgg(fig, master=root)


    b6 = ttk.Button(root, text="Save")
    b7 = ttk.Button(root, text="Load")
    b8 = ttk.Button(root, text="New Simulation")


    #update_map_visualization()
    #TODO: Add style
    #sv_ttk.set_theme("dark")
    log("GUI initialized")
    root.mainloop()

if __name__ == "__main__":
    run_gui()