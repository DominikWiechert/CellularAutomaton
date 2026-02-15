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
from output import simplified_visualize_fire, render_optimised_forward,render_optimised_backward
from process import run_simulation_step, log, calculate_probability, simplify_forest_map, count_cells, optimised_render
from custom_datatypes import NodeStatus

try:
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

class HeightEntry(tk.Frame):
    def __init__(self, root, remove_command):
        super().__init__(root)
        x_label = tk.Label(self, text="x [m]:")
        x_label.grid(row=0, column=0, padx=2)
        self.x_entry = tk.Entry(self)
        self.x_entry.grid(row=0, column=1, padx=2)

        y_label = tk.Label(self, text="y [m]:")
        y_label.grid(row=1, column=0, padx=2)
        self.y_entry = tk.Entry(self)
        self.y_entry.grid(row=1, column=1, padx=2)

        h_label = tk.Label(self, text="height [m]:")
        h_label.grid(row=2, column=0, padx=2)
        self.h_entry = tk.Entry(self)
        self.h_entry.grid(row=2, column=1, padx=2)
        remove_button = tk.Button(self, text="Remove entry", command=self.remove_entry)
        remove_button.grid(row=0, column=2, padx=2)
        self.remove_command = remove_command

    def remove_entry(self):
        self.remove_command(self)

class GuiHandler:
    def save_entries_to_config(self):
        """
        Saves all user defined data in GUI entries to a selected config file.
        """
        if not self.are_all_entries_correct():
            return
        config_path = filedialog.asksaveasfilename(
            defaultextension=".yaml",
            filetypes = (("YAML File", "*.yaml"), ("All files", "*.*"))
        )
        if not config_path:
            return

        config_data = {
            'path': str(self.path_entry.get()),
            't_max': int(float(self.t_max_entry.get())),
            'tick_speed': int(float(self.tick_speed_entry.get())),
            'nodes_per_axis': float(self.nodes_per_axis_entry.get()),
            'axis_length': float(self.axis_length_entry.get()),
            'probability': float(self.probability_entry.get()),
            'wind_speed_x': float(self.wind_speed_x_entry.get()),
            'wind_speed_y': float(self.wind_speed_y_entry.get()),
            'fire_starting_position': [x for x in self.fire_starting_position_entry.get().split(';')],
            'heights': self.get_height_entries()
        }

        with open(config_path, 'w') as file:
            yaml.dump(config_data, file)
        log(f'Data saved to {config_path}')

    def update_config_entries_from_config_path(self):
        """
         Given a path to a config file, this function updates all GUI entries with data from the config file.
        """
        # All entries shall be given in the config file.
        with open(self.config_path, 'r') as file:
            config = yaml.safe_load(file)

        def insert_value_in_entry(value, entry: tk.Entry):
            entry.delete(0, tk.END)
            entry.insert(0, value)

        insert_value_in_entry(config['path'], self.path_entry)
        insert_value_in_entry(config['t_max'], self.t_max_entry)
        insert_value_in_entry(config['tick_speed'], self.tick_speed_entry)
        insert_value_in_entry(int(config['nodes_per_axis']), self.nodes_per_axis_entry)
        insert_value_in_entry(config['axis_length'], self.axis_length_entry)
        insert_value_in_entry(config['probability'], self.probability_entry)
        insert_value_in_entry(config['wind_speed_x'], self.wind_speed_x_entry)
        insert_value_in_entry(config['wind_speed_y'], self.wind_speed_y_entry)
        insert_value_in_entry(';'.join(config['fire_starting_position']), self.fire_starting_position_entry)

        for i in range(1, len(self.height_entries)):
            self.height_entries[-1].remove_entry()

        for height_entry in config['heights']:
            self.add_height_entry()
            insert_value_in_entry(height_entry[0], self.height_entries[-1].x_entry)
            insert_value_in_entry(height_entry[1], self.height_entries[-1].y_entry)
            insert_value_in_entry(height_entry[2], self.height_entries[-1].h_entry)

    def read_config_variables_to_class_entries(self):
        """
        Reads all entries from GUI to attributes of the class GuiHandler. Datatypes are cast accordingly, although
        no value validation is done.
        """
        self.map_picture_path = Path(self.path_entry.get())
        self.t_max = int(float(self.t_max_entry.get()))
        self.tick_speed = int(float(self.tick_speed_entry.get()))
        self.nodes_per_axis = int(float(self.nodes_per_axis_entry.get()))
        self.axis_length = int(float(self.axis_length_entry.get()))
        self.probability = self.probability_entry.get()
        self.wind_speed_x = self.wind_speed_x_entry.get()
        self.wind_speed_y = self.wind_speed_y_entry.get()
        self.fire_starting_position = [int(x) for x in self.fire_starting_position_entry.get().split(';')]
        self.heights = self.get_height_entries()

    def load_config_from_file(self):
        """
        Ask user for a config file with dialog window and set all values in GUI.
        """
        file_path = tk.filedialog.askopenfilename(
            title="Select a file",
            filetypes=(("YAML Files", "*.yaml"), ("All files", "*.*"))
        )
        if file_path:
            self.config_path = Path(file_path)
            self.update_config_entries_from_config_path()

    def are_all_entries_correct(self):
        """
        Validate all entries set by the user at once. Returns true if all values are correct and false if not.
        """
        # Function requires refactoring but works for now.
        def is_float(value):
            # Check if string value from entry can be cast to float. No regex needed.
            try:
                float(value)
                return True
            except ValueError:
                return False

        def is_int(value):
            # Check if string value from entry can be cast to an integer. No regex needed.
            try:
                int(float(value))
                return True
            except ValueError:
                return False

        def is_float_greater_than_zero(value, name):
            # Check if function can be cast to float and is greater than zero and return useful error message if not.
            if is_float(value):
                if float(value) <= 0:
                    messagebox.showerror("Error", f"{name} must be greater than 0")
                    return False
            else:
                messagebox.showerror("Error", f"{name} is invalid. Make sure it can be cast to float.")
                return False
            return True

        def is_int_greater_than_zero(value, name):
            # Check if function can be cast to integer and is greater than zero and return useful error message if not.
            if is_int(value):
                if int(float(value)) <= 0:
                    messagebox.showerror("Error", f"{name} must be greater than 0")
                    return False
            else:
                messagebox.showerror("Error", f"{name} is invalid. Make sure it can be cast to integer.")
                return False
            return True

        if not is_int_greater_than_zero(self.t_max_entry.get(), 'Simulation Time'): return False
        if not is_int_greater_than_zero(self.tick_speed_entry.get(), 'Tick speed'): return False
        if not is_int_greater_than_zero(self.nodes_per_axis_entry.get(), 'Number of cells per row'): return False
        if not is_int_greater_than_zero(self.axis_length_entry.get(), 'Width of map'): return False
        if not is_float_greater_than_zero(self.probability_entry.get(), 'probability'): return False

        if not is_float(self.wind_speed_x_entry.get()):
            messagebox.showerror("Error", "wind_speed_x is invalid. Make sure it can be cast to float.")
            return False

        if not is_float(self.wind_speed_y_entry.get()):
            messagebox.showerror("Error", "wind_speed_y is invalid. Make sure it can be cast to float.")
            return False

        if len(self.fire_starting_position_entry.get().split(';')) != 2:
            messagebox.showerror("Error", "Fire starting position is invalid. Make sure you have two values, that are separated by a semicolon ';'.")
            return False

        for position in self.fire_starting_position_entry.get().split(';'):
            if not is_int_greater_than_zero(position, 'fire_starting_position'): return False
            if int(float(position)) > int(float(self.axis_length_entry.get())):
                messagebox.showerror("Error", f"Fire starting position {position} cannot be greater than axis length. This data is given in meter.")
                return False

        height_entries = self.get_height_entries()
        if len(height_entries) < 2:
            messagebox.showerror("Error", "Atleast two height entries are needed.")
            return False
        for heights in self.get_height_entries():
            for value in heights:
                if not is_float_greater_than_zero(value, 'height value'): return False
            for position in [heights[0], heights[1]]:
                if float(position) >= float(self.axis_length_entry.get()):
                    messagebox.showerror("Error",f"Height position {position} cannot be greater than axis length. This data is given in meter.")
                    return False

        # All values are valid
        return True

    def slider_changed(self, event):
        self.slider_label.config(text = f'tick speed = {int(self.slider.get()):04} ms')
        self.tick_speed = int(self.slider.get())

    def plot(self):
        """
        Plot the timeline of the simulation.
        """
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
        """
        Plot the current step in the timeline plot.
        """
        self.ax.lines[len(self.ax.lines) -1].remove()
        self.ax.axvline(x=self.current_step,color='black',linestyle='--')
        self.canvas_plot.draw()

    def select_file(self):
        """
        Select a file in a filedialog and set the path as value self.path_entry if it is valid.
        """
        file_path = tk.filedialog.askopenfilename(
            title="Select a file",
            filetypes=(("PNG Files", "*.png"), ("All files", "*.*"))
        )
        if file_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, file_path)

    def run_calculation(self):
        """
        Run the whole calculation of the simulation and update the visualization in the Post-Processing tab.
        """
        if not self.are_all_entries_correct(): return
        self.read_config_variables_to_class_entries()
        forest_map = get_forest_map(map_path=self.map_picture_path, nodes_per_axis=self.nodes_per_axis, axis_length=self.axis_length, heights=self.heights)
        prob_crown, prob_ground = calculate_probability()

        cell_size = self.axis_length / self.nodes_per_axis
        fire_start_x = int(self.fire_starting_position[0] / cell_size) - 1
        fire_start_y = int(self.fire_starting_position[1] / cell_size) - 1
        forest_map[fire_start_x][fire_start_y].status = NodeStatus.LOWER_BURNING

        precent_step = 50 / self.t_max

        self.forest_map_simplified = np.empty([len(forest_map), len(forest_map[0]), self.t_max + 1], dtype="S10")
        self.timeline = np.zeros([7, self.t_max + 1])

        self.forest_map_simplified[:, :, 0] = simplify_forest_map(forest_map)
        self.timeline[0, 0] = 0
        self.timeline[1:7, 0] = count_cells(self.forest_map_simplified[:, :, 0])[:, 0]
        for t in range(1, self.t_max + 1):
            log("Step: " + str(t))
            self.prog_label.config(text=f"Simulating {t}/{self.t_max}")
            cell_size = self.axis_length / self.nodes_per_axis
            forest_map = run_simulation_step(forest_map, prob_crown, prob_ground, cell_size)
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
        simplified_visualize_fire(np.transpose(self.forest_map_simplified[:, :, 0]), self.canvas_automat)

    def next_button(self):
        """
        Function for the next button. Steps the visualization one step forward if possible.
        """
        if self.current_step == self.t_max :
            log("Last step reached")
        else:
            render_optimised_forward(self.optimised_matrix[self.current_step], self.canvas_automat, self.cell_width, self.cell_height)
            self.current_step += 1
            log("Step: " + str(self.current_step))
            self.plot_position()

    def previous_button(self):
        """
        Function for the previous button. Steps the visualization one step back if possible.
        """
        if self.current_step >=1:
            render_optimised_backward(self.optimised_matrix[self.current_step-1], self.canvas_automat, self.cell_width, self.cell_height)
            self.current_step -= 1
            log("Step: " + str(self.current_step))
            self.plot_position()
        else:
            log("First step reached")

    def first_button(self):
        """
        Function for the first button. Skips the visualization to the first step of the simulation.
        """
        self.current_step = 0
        log("Step: " + str(self.current_step))
        simplified_visualize_fire(np.transpose(self.forest_map_simplified[:,:,self.current_step]), self.canvas_automat)
        self.plot_position()

    def last_button(self):
        """
        Function for the last button. Skips the visualization to the last step of the simulation.
        """
        self.current_step = self.t_max
        log("Step: " + str(self.current_step))
        simplified_visualize_fire(np.transpose(self.forest_map_simplified[:,:,self.current_step]), self.canvas_automat)
        self.plot_position()

    def play_button(self):
        """
        Function for the play animation button. Runs the simulation animation if it is not at the end.
        """
        if self.playing:
            self.playing = False
            self.b3.config(text="▶")
        else:
            self.playing = True
            self.b3.config(text="⏸")
            self.run_animation()

    def run_animation(self):
        """
        Run the animation of the simulation.
        """
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

    def add_height_entry(self):
        """
        Add height entry and add it as the last element in the grid
        """
        entry = HeightEntry(self.heights_frame, self.remove_height_entry)
        i_new_entry = len(self.height_entries)
        i_row = i_new_entry // self.max_height_entries_per_row
        i_col = i_new_entry % self.max_height_entries_per_row
        entry.grid(row=i_row, column=i_col)
        self.height_entries.append(entry)

    def remove_height_entry(self, entry):
        """
        Remove a height entry element from GUI and rearrange all other elements in the grid
        """
        # At least two datapoints are needed
        if len(self.height_entries) == 2:
            messagebox.showinfo("Information", "Failed to remove last entry. At least two entries are needed.")
            return

        # Destroy and remove entry
        entry.destroy()
        self.height_entries.remove(entry)

        # Rearrange all other entries
        i_entry=0
        for entry in self.height_entries:
            i_row = i_entry // self.max_height_entries_per_row
            i_col = i_entry % self.max_height_entries_per_row
            entry.grid_forget()
            entry.grid(row=i_row, column=i_col)
            i_entry+=1

    def get_height_entries(self):
        """
        Get height datasets from GUI as a list of list[x,y,height].
        """
        return [[entry.x_entry.get(), entry.y_entry.get(), entry.h_entry.get()] for entry in self.height_entries]

    def show_forest_map_preview(self):
        """ Show a preview of the forest map height interpolation."""
        # Utilize the show_height_graph functionality in get_forest_map to plot the heights
        if not self.are_all_entries_correct(): return
        self.read_config_variables_to_class_entries()

        get_forest_map(map_path=self.map_picture_path, nodes_per_axis=self.nodes_per_axis,
                       axis_length=self.axis_length, heights=self.heights, show_height_graph=True)
    
    def __init__(self):
        """
        Initiate the whole GUI.
        """
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
        self.nodes_per_axis = None
        self.axis_length = None
        self.probability = None
        self.wind_speed_x = None
        self.wind_speed_y = None
        self.map_picture_path = None
        self.fire_starting_position = None
        self.heights = None

        # Root window
        log("Init pre-processing GUI...")
        self.root = tk.Tk()
        self.root.title("Wildfire Simulation")
        self.root.state("zoomed")
        self.notebook = ttk.Notebook(self.root)

        tab_preprocessing = ttk.Frame(self.notebook)
        self.tab_height = ttk.Frame(self.notebook)
        self.tab_post = ttk.Frame(self.notebook)

        self.notebook.add(tab_preprocessing, text="Pre-Processing")
        self.notebook.add(self.tab_height, text="Heights")
        self.notebook.add(self.tab_post, text="Processing")
        self.notebook.pack(expand=1, fill='both')

        # Preprocessing tab
        path_entry_label = tk.Label(tab_preprocessing, text="Map picture path:")
        path_entry_label.grid(row=0, column=0, padx=10, pady=10)
        self.path_entry = tk.Entry(tab_preprocessing, width=100)
        self.path_entry.grid(row=0, column=1, columnspan=1, padx=10, pady=10)

        self.select_file_button = tk.Button(tab_preprocessing, text="Select File", command=self.select_file)
        self.select_file_button.grid(row=0, column=3, padx=10, pady=10)

        t_max_label = tk.Label(tab_preprocessing, text="Simulation Time:")
        t_max_label.grid(row=1, column=0, padx=10, pady=10)
        self.t_max_entry = tk.Entry(tab_preprocessing, width=10)
        self.t_max_entry.grid(row=1, column=1, columnspan=1, sticky="we", padx=10, pady=10)

        tick_speed_label = tk.Label(tab_preprocessing, text="Tick speed:")
        tick_speed_label.grid(row=2, column=0, padx=10, pady=10)
        self.tick_speed_entry = tk.Entry(tab_preprocessing, width=10)
        self.tick_speed_entry.grid(row=2, column=1, columnspan=1, sticky="we", padx=10, pady=10)

        nodes_per_axis_label = tk.Label(tab_preprocessing, text="Number of cells per row [n]:")
        nodes_per_axis_label.grid(row=3, column=0, padx=10, pady=10)
        self.nodes_per_axis_entry = tk.Entry(tab_preprocessing, width=10)
        self.nodes_per_axis_entry.grid(row=3, column=1, columnspan=1, sticky="we", padx=10, pady=10)

        axis_length_label = tk.Label(tab_preprocessing, text="Width of map [m]:")
        axis_length_label.grid(row=4, column=0, padx=10, pady=10)
        self.axis_length_entry = tk.Entry(tab_preprocessing, width=10)
        self.axis_length_entry.grid(row=4, column=1, columnspan=1, sticky="we", padx=10, pady=10)

        probability_label = tk.Label(tab_preprocessing, text="probability:")
        probability_label.grid(row=5, column=0, padx=10, pady=10)
        self.probability_entry = tk.Entry(tab_preprocessing, width=10)
        self.probability_entry.grid(row=5, column=1, columnspan=1, sticky="we", padx=10, pady=10)

        wind_speed_x_label = tk.Label(tab_preprocessing, text="Wind speed x-direction [m/s]:")
        wind_speed_x_label.grid(row=6, column=0, padx=10, pady=10)
        self.wind_speed_x_entry = tk.Entry(tab_preprocessing, width=10)
        self.wind_speed_x_entry.grid(row=6, column=1, columnspan=1, sticky="we", padx=10, pady=10)

        wind_speed_y_label = tk.Label(tab_preprocessing, text="Wind speed y-direction [m/s]::")
        wind_speed_y_label.grid(row=7, column=0, padx=10, pady=10)
        self.wind_speed_y_entry = tk.Entry(tab_preprocessing, width=10)
        self.wind_speed_y_entry.grid(row=7, column=1, columnspan=1, sticky="we", padx=10, pady=10)

        fire_starting_position_label = tk.Label(tab_preprocessing, text="Fire starting position 'xx;yy' [m]:")
        fire_starting_position_label.grid(row=8, column=0, padx=10, pady=10)
        self.fire_starting_position_entry = tk.Entry(tab_preprocessing, width=10)
        self.fire_starting_position_entry.grid(row=8, column=1, padx=10, pady=10)

        save_config_button = tk.Button(tab_preprocessing, text="Save Config as...", command=self.save_entries_to_config)
        save_config_button.grid(row=9, column=0, padx=10, pady=10)

        load_config_button = tk.Button(tab_preprocessing, text="Load Config", command=self.load_config_from_file)
        load_config_button.grid(row=9, column=1, padx=10, pady=10)

        calculate_button = tk.Button(tab_preprocessing, text="Run calculation", command=self.run_calculation)
        calculate_button.grid(row=9, column=2, padx=10, pady=10)

        pbar_label = tk.Label(tab_preprocessing, text="Progress:")
        pbar_label.grid(row=10, column=0, padx=10, pady=10)
        self.pbar = ttk.Progressbar(tab_preprocessing, orient="horizontal", length=100, mode='determinate')
        self.pbar.grid(row=10, column=1, sticky="we", columnspan=3, padx=10, pady=10)
        self.prog_label = tk.Label(tab_preprocessing, text="")
        self.prog_label.grid(row=11, column=1, columnspan=3, padx=10, pady=10)

        # Heights tab
        self.height_entries = []
        self.add_height_entry_button = tk.Button(self.tab_height, text="Add height entry", command=self.add_height_entry)
        self.add_height_entry_button.pack()
        show_preview_button = tk.Button(self.tab_height, text="Show map preview", command=self.show_forest_map_preview)
        show_preview_button.pack()
        self.max_height_entries_per_row = 5
        self.heights_frame = tk.Frame(self.tab_height)
        self.heights_frame.pack()

        self.update_config_entries_from_config_path()

        # Postprocessing tab
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