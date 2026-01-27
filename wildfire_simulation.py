from pathlib import Path
import yaml
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from ctypes import windll
import tkinter as tk
from tkinter import filedialog, ttk,messagebox
import sv_ttk

from input import get_forest_map
from output import visualize_fire, simplified_visualize_fire, render_optimised_forward,render_optimised_backward
from process import run_simulation_step, log, calculate_probability, simplify_forest_map, count_cells, optimised_render
from custom_datatypes import NodeStatus

try:
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


class GuiHandler:
    def save_entries_to_config(self):
        config_data = {
            'path': str(self.path_entry.get()),
            't_max': int(self.t_max_entry.get()),
            'tick_speed': float(self.tick_speed_entry.get()),
            'max_axis_length': float(self.max_axis_length_entry.get()),
            'probability': float(self.probability_entry.get()),
            'wind_speed_x': float(self.wind_speed_x_entry.get()),
            'wind_speed_y': float(self.wind_speed_y_entry.get()),
            'fire_starting_position': [x for x in self.fire_starting_position_entry.get().split(';')]
        }
        # TODO: Select file path for yaml. Might use asksaveasfile method from tkinter.
        with open("config.yaml", 'w') as file:
            yaml.dump(config_data, file)
        log('Data saved to config.yaml')

    def slider_changed(self, event):
        self.slider_label.config(text = f'tick speed = {int(self.slider.get()):04} ms')
        self.tick_speed = int(self.slider.get())

    def plot(self):
        self.ax.clear()
        x = self.timeline[0,:]
        self.ax.set_ylabel("number of cells [1]")
        self.ax.set_xlabel("time steps [1]")
        self.ax.plot(x, self.timeline[1,:], color='green', label='Tree')
        self.ax.plot(x, self.timeline[2,:], color='red', label='Crown burning')
        self.ax.plot(x, self.timeline[3, :], color='black', label='Burned down')
        self.ax.plot(x, self. timeline[5, :], color='orange', label='Lower vegetation burning')
        self.ax.legend()
        self.ax.grid(True)
        self.ax.axvline(x=self.current_step, color='black', linestyle='--')
        self.canvas_plot.draw()

    def plot_position(self):
        self.ax.lines[len(self.ax.lines) -1].remove()
        self.ax.axvline(x=self.current_step,color='black',linestyle='--')
        self.canvas_plot.draw()

    def update_map_visualization(self):
        forest_map = get_forest_map(map_path=Path(self.path_entry.get()), max_axis_length=self.max_axis_length)
        #  visualize_fire(forest_map, canvas)

    def select_file(self):
        file_path = tk.filedialog.askopenfilename(
            title="Select a file",
            filetypes=(("PNG Files", "*.png"), ("All files", "*.*"))
        )
        if file_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, file_path)
        # update_map_visualization()

    def update_config_entries_from_config_path(self):
        with open(self.config_path, 'r') as file:
            config = yaml.safe_load(file)
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, config['path'])
        self.t_max_entry.delete(0, tk.END)
        self.t_max_entry.insert(0, config['t_max'])
        self.tick_speed_entry.delete(0, tk.END)
        self.tick_speed_entry.insert(0, config['tick_speed'])
        self.max_axis_length_entry.delete(0, tk.END)
        self.max_axis_length_entry.insert(0, config['max_axis_length'])
        self.probability_entry.delete(0, tk.END)
        self.probability_entry.insert(0, config['probability'])
        self.wind_speed_x_entry.delete(0, tk.END)
        self.wind_speed_x_entry.insert(0, config['wind_speed_x'])
        self.wind_speed_y_entry.delete(0, tk.END)
        self.wind_speed_y_entry.insert(0, config['wind_speed_y'])
        self.fire_starting_position_entry.delete(0, tk.END)
        self.fire_starting_position_entry.insert(0, ';'.join(config['fire_starting_position']))

    def read_config_variables_to_class_entries(self):
        self.map_picture_path = Path(self.path_entry.get())
        self.t_max = int(float(self.t_max_entry.get()))
        self.tick_speed = int(float(self.tick_speed_entry.get()))
        self.max_axis_length = int(float(self.max_axis_length_entry.get()))
        self.probability = self.probability_entry.get()
        self.wind_speed_x = self.wind_speed_x_entry.get()
        self.wind_speed_y = self.wind_speed_y_entry.get()
        self.fire_starting_position = [int(x) for x in self.fire_starting_position_entry.get().split(';')]

    def validate_config_entries(self):
        # TODO
        pass

    def load_config_from_file(self):
        file_path = tk.filedialog.askopenfilename(
            title="Select a file",
            filetypes=(("YAML Files", "*.yaml"), ("All files", "*.*"))
        )
        if file_path:
            self.config_path = Path(file_path)
            self.update_config_entries_from_config_path()
            self.update_map_visualization()

    def run_calculation(self):
        self.read_config_variables_to_class_entries()
        forest_map = get_forest_map(map_path=self.map_picture_path, max_axis_length=self.max_axis_length)
        prob_crown, prob_ground = calculate_probability()

        forest_map[self.fire_starting_position[0]][self.fire_starting_position[1]].status = NodeStatus.LOWER_BURNING

        precent_step = 50 / self.t_max

        self.forest_map_simplified = np.empty([len(forest_map), len(forest_map[0]), self.t_max + 1], dtype="S10")
        self.timeline = np.zeros([7, self.t_max + 1])

        self.forest_map_simplified[:, :, 0] = simplify_forest_map(forest_map)
        self.timeline[0, 0] = 0
        self.timeline[1:7, 0] = count_cells(self.forest_map_simplified[:, :, 0])[:, 0]
        for t in range(1, self.t_max + 1):
            log("Step: " + str(t))
            self.prog_label.config(text=f"Simulating {t}/{self.t_max}")
            forest_map = run_simulation_step(forest_map, prob_crown, prob_ground)
            self.forest_map_simplified[:, :, t] = simplify_forest_map(forest_map)
            self.timeline[0, t] = t
            self.timeline[1:7, t] = count_cells(self.forest_map_simplified[:, :, t])[:, 0]
            self.pbar['value'] += precent_step
            self.root.update_idletasks()
            self.root.update()

        for i in range(self.t_max):
            self.optimised_matrix.append(optimised_render(self.forest_map_simplified[:, :, i], self.forest_map_simplified[:, :, i + 1]))
            self.pbar['value'] += precent_step
            self.prog_label.config(text=f"Optimizing {i}/{self.t_max}")

        canvas_width = self.canvas_automat.winfo_reqwidth()
        canvas_height = self.canvas_automat.winfo_reqheight()

        number_of_nodes_width = len(forest_map)
        number_of_nodes_height = len(forest_map[0])

        self.cell_width = canvas_width / number_of_nodes_width
        self.cell_height = canvas_height / number_of_nodes_height
        self.prog_label.config(text="Done!")
        log("Simulation end")
        messagebox.showinfo("Calculation Results", "Calculation completed.")
        self.notebook.select(self.tab_post)


        self.canvas_plot.get_tk_widget().grid(row=0, column=21, columnspan=10, sticky='e')
        self.plot()
        simplified_visualize_fire(self.forest_map_simplified[:, :, 0], self.canvas_automat)

    def load_post_pros(self):
        # TODO: tbi
        print("platzhalter")

    ### button functions
    def next_button(self):
        if self.current_step == self.t_max :
            log("Last step reached")
        else:
            render_optimised_forward(self.optimised_matrix[self.current_step], self.canvas_automat, self.cell_width, self.cell_height)
            self.current_step += 1
            log("Step: " + str(self.current_step))
            self.plot_position()

    def previous_button(self):
        if self.current_step >=1:
            render_optimised_backward(self.optimised_matrix[self.current_step-1], self.canvas_automat, self.cell_width, self.cell_height)
            self.current_step -= 1
            log("Step: " + str(self.current_step))
            self.plot_position()
        else:
            log("First step reached")

    def first_button(self):
        self.current_step = 0
        log("Step: " + str(self.current_step))
        simplified_visualize_fire(self.forest_map_simplified[:,:,self.current_step], self.canvas_automat)
        self.plot_position()

    def last_button(self):
        self.current_step = self.t_max
        log("Step: " + str(self.current_step))
        simplified_visualize_fire(self.forest_map_simplified[:,:,self.current_step], self.canvas_automat)
        self.plot_position()

    def play_button(self):
        if self.playing:
            self.playing = False
            self.b3.config(text="▶")
        else:
            self.playing = True
            self.b3.config(text="⏸")
            self.run_animation()

    def run_animation(self):
        if self.playing:
            if self.current_step == self.t_max:
                self.playing = False
                self.b3.config(text="▶")
            else:
                render_optimised_forward(self.optimised_matrix[self.current_step], self. canvas_automat, self.cell_width, self.cell_height)
                self.current_step += 1
                log("Step: " + str(self.current_step))
                self.plot_position()
                self.root.after(self.tick_speed, lambda: self.run_animation())

    def __init__(self):
        # Variables
        self.timeline = None
        self.forest_map_simplified = None
        self.current_step = 0
        self.t_max = None
        self.playing = False
        self.tick_speed = 500
        self.optimised_matrix = []
        self.cell_width = 1
        self.cell_height = 1
        self.config_path = Path('config.yaml')
        self.max_axis_length = None
        self.probability = None
        self.wind_speed_x = None
        self.wind_speed_y = None
        self.map_picture_path = None
        self.fire_starting_position = None

        # Root window
        log("Init pre-processing GUI...")
        self.root = tk.Tk()
        self.root.title("Wildfire Simulation - Pre-Processing")
        self.root.geometry("2000x1200")
        self.notebook = ttk.Notebook(self.root)
        self.tab_pre = ttk.Frame(self.notebook)
        self.tab_post = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_pre, text="Pre-Processing")
        self.notebook.add(self.tab_post, text="Processing")
        self.notebook.pack(expand=1, fill='both')


        # First tab
        path_entry_label = tk.Label(self.tab_pre, text="Map picture path:")
        path_entry_label.grid(row=0, column=0, padx=10, pady=10)
        self.path_entry = tk.Entry(self.tab_pre, width=100)
        self.path_entry.grid(row=0, column=1, columnspan=1, padx=10, pady=10)


        self.select_file_button = tk.Button(self.tab_pre, text="Select File", command=self.select_file)
        self.select_file_button.grid(row=0, column=3, padx=10, pady=10)

        t_max_label = tk.Label(self.tab_pre, text="Simulation Time:")
        t_max_label.grid(row=1, column=0, padx=10, pady=10)
        self.t_max_entry = tk.Entry(self.tab_pre, width=10)
        self.t_max_entry.grid(row=1, column=1, columnspan=1, sticky="we", padx=10, pady=10)

        tick_speed_label = tk.Label(self.tab_pre, text="Tick speed:")
        tick_speed_label.grid(row=2, column=0, padx=10, pady=10)
        self.tick_speed_entry = tk.Entry(self.tab_pre, width=10)
        self.tick_speed_entry.grid(row=2, column=1, columnspan=1, sticky="we", padx=10, pady=10)

        max_axis_length_label = tk.Label(self.tab_pre, text="max_axis_length:")
        max_axis_length_label.grid(row=3, column=0, padx=10, pady=10)
        self.max_axis_length_entry = tk.Entry(self.tab_pre, width=10)
        self.max_axis_length_entry.grid(row=3, column=1, columnspan=1, sticky="we", padx=10, pady=10)

        probability_label = tk.Label(self.tab_pre, text="probability:")
        probability_label.grid(row=4, column=0, padx=10, pady=10)
        self.probability_entry = tk.Entry(self.tab_pre, width=10)
        self.probability_entry.grid(row=4, column=1, columnspan=1, sticky="we", padx=10, pady=10)

        wind_speed_x_label = tk.Label(self.tab_pre, text="wind_speed_x:")
        wind_speed_x_label.grid(row=5, column=0, padx=10, pady=10)
        self.wind_speed_x_entry = tk.Entry(self.tab_pre, width=10)
        self.wind_speed_x_entry.grid(row=5, column=1, columnspan=1, sticky="we", padx=10, pady=10)

        wind_speed_y_label = tk.Label(self.tab_pre, text="wind_speed_y:")
        wind_speed_y_label.grid(row=6, column=0, padx=10, pady=10)
        self.wind_speed_y_entry = tk.Entry(self.tab_pre, width=10)
        self.wind_speed_y_entry.grid(row=6, column=1, columnspan=1, sticky="we", padx=10, pady=10)

        fire_starting_position_label = tk.Label(self.tab_pre, text="Fire starting position 'xx;yy':")
        fire_starting_position_label.grid(row=7, column=0, padx=10, pady=10)
        self.fire_starting_position_entry = tk.Entry(self.tab_pre, width=10)
        self.fire_starting_position_entry.grid(row=7, column=1, padx=10, pady=10)
        self.update_config_entries_from_config_path()

        self.save_config_button = tk.Button(self.tab_pre, text="Save Config as...", command=self.save_entries_to_config)
        self.save_config_button.grid(row=8, column=0, padx=10, pady=10)

        self.load_config_button = tk.Button(self.tab_pre, text="Load Config", command=self.load_config_from_file)
        self.load_config_button.grid(row=8, column=1, padx=10, pady=10)

        self.calculate_button = tk.Button(self.tab_pre, text="Run calculation", command=self.run_calculation)
        self.calculate_button.grid(row=8, column=2, padx=10, pady=10)

        self.load_post_pros_button = tk.Button(self.tab_pre, text="Load calculation", command=self.load_post_pros)
        self.load_post_pros_button.grid(row=8, column=3, padx=10, pady=10)

        pbar_label = tk.Label(self.tab_pre, text="Progress:")
        pbar_label.grid(row=9, column=0, padx=10, pady=10)
        self.pbar = ttk.Progressbar(self.tab_pre, orient="horizontal", length=100, mode='determinate')
        self.pbar.grid(row=9, column=1, sticky="we", columnspan=3, padx=10, pady=10)
        self.prog_label = tk.Label(self.tab_pre, text="")
        self.prog_label.grid(row=10, column=1, columnspan=3, padx=10, pady=10)

        self.select_file_button = tk.Button(self.tab_pre, text="Select File", command=self.select_file)
        self.select_file_button.grid(row=0, column=3, padx=10, pady=10)

        t_max_label = tk.Label(self.tab_pre, text="Simulation Time:")
        t_max_label.grid(row=1, column=0, padx=10, pady=10)
        self.t_max_entry = tk.Entry(self.tab_pre, width=100)
        self.t_max_entry.grid(row=1, column=1, columnspan=3, sticky="we", padx=10, pady=10)

        tick_speed_label = tk.Label(self.tab_pre, text="Tick speed:")
        tick_speed_label.grid(row=2, column=0, padx=10, pady=10)
        self.tick_speed_entry = tk.Entry(self.tab_pre, width=100)
        self.tick_speed_entry.grid(row=2, column=1, columnspan=3, sticky="we", padx=10, pady=10)

        max_axis_length_label = tk.Label(self.tab_pre, text="max_axis_length:")
        max_axis_length_label.grid(row=3, column=0, padx=10, pady=10)
        self.max_axis_length_entry = tk.Entry(self.tab_pre, width=100)
        self.max_axis_length_entry.grid(row=3, column=1, columnspan=3, sticky="we", padx=10, pady=10)

        probability_label = tk.Label(self.tab_pre, text="probability:")
        probability_label.grid(row=4, column=0, padx=10, pady=10)
        self.probability_entry = tk.Entry(self.tab_pre, width=100)
        self.probability_entry.grid(row=4, column=1, columnspan=3, sticky="we", padx=10, pady=10)

        wind_speed_x_label = tk.Label(self.tab_pre, text="wind_speed_x:")
        wind_speed_x_label.grid(row=5, column=0, padx=10, pady=10)
        self.wind_speed_x_entry = tk.Entry(self.tab_pre, width=100)
        self.wind_speed_x_entry.grid(row=5, column=1, columnspan=3, sticky="we", padx=10, pady=10)

        wind_speed_y_label = tk.Label(self.tab_pre, text="wind_speed_y:")
        wind_speed_y_label.grid(row=6, column=0, padx=10, pady=10)
        self.wind_speed_y_entry = tk.Entry(self.tab_pre, width=100)
        self.wind_speed_y_entry.grid(row=6, column=1, columnspan=3, sticky="we", padx=10, pady=10)
        self.update_config_entries_from_config_path()
        # load post ops gui

        self.fig, self.ax = plt.subplots()

        self.canvas_automat = tk.Canvas(self.tab_post, width=730, height=730, bg="red")
        self.slider_label = ttk.Label(self.tab_post, text=f'tick speed = {int(self.tick_speed):04} ms')
        self.slider = ttk.Scale(self.tab_post, from_=1, to=1000, value=500, orient='horizontal', command=self.slider_changed)
        self.b1 = ttk.Button(self.tab_post, text="⏮", command=self.first_button)
        self.b1.grid(row=2, column=8)
        self.b2 = ttk.Button(self.tab_post, text="<", command=self.previous_button)
        self.b2.grid(row=2, column=9)
        self.b3 = ttk.Button(self.tab_post, text="▶", command=self.play_button)
        self.b3.grid(row=2, column=10)
        self.b4 = ttk.Button(self.tab_post, text=">", command=self.next_button)
        self.b4.grid(row=2, column=11)
        self.b5 = ttk.Button(self.tab_post, text="⏭", command=self.last_button)
        self.b5.grid(row=2, column=12)

        self.root.title("Wildfire - Post-processing")
        self.root.geometry("2000x1200")

        self.canvas_automat.grid(row=0, column=0, columnspan=20)
        self.slider_label.grid(row=1, column=0, sticky='w')
        self.slider.grid(row=1, column=1, columnspan=19, sticky='we')
        self.slider.config(value=self.tick_speed)
        self.slider_label.config(text=f'tick speed = {int(self.slider.get()):04} ms')

        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=self.tab_post)
        sv_ttk.set_theme("dark")
        log("GUI initialized")
        self.root.mainloop()

if __name__ == "__main__":
    gui_handler = GuiHandler()