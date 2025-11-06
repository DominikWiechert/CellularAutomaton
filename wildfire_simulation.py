from pathlib import Path

from input import get_forest_map
from output import visualize_fire, init_gui, append_frame
from process import run_simulation_step, log, print_map_2_console, calculate_probability
from custom_datatypes import NodeStatus
import time
from ctypes import windll

try:
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

def run_simulation():
    forest_map = get_forest_map(map_path=Path().cwd() / 'map_pictures' / 'osm_map.png', max_axis_length=100)

    t_max = 20
    tick_speed = 0.1 #[s]
    window, canvas = init_gui()
    prob = calculate_probability()

    forest_map[15][15].status = NodeStatus.BURNING

    frames = []
    for t in range(t_max):
        log("Step: " + str(t))
        time.sleep(tick_speed)
        forest_map = run_simulation_step(forest_map,prob)
        visualize_fire(forest_map,window,canvas)
        append_frame(canvas, frames)

        window.update_idletasks()
        window.update()
    log("Simulation end")
    frames[0].save("waldbrandausbreitung_testing.gif", save_all=True, append_images=frames[1:], duration=500, loop=0,
                   disposal=2)
    window.mainloop()

if __name__ == "__main__":
    run_simulation()