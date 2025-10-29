from input import get_forest_map
from output import visualize_fire, init_gui
from process import run_simulation_step, log, print_map_2_console, calculate_probability
from custom_datatypes import NodeStatus
import time

# Feel free to edit the structure :)
forest_map = get_forest_map(grid_height=30,grid_width=30)

t_max = 20
tick_speed = 0.1 #[s]
window, canvas = init_gui()
prob = calculate_probability()

## -- Create Test Map - to be removed later --
for row in range(len(forest_map)):
    for col in range(len(forest_map[0])):
        forest_map[row][col].status = NodeStatus.INTACT


forest_map[2][1].status = NodeStatus.BURNING
#----------------------------------------------


for t in range(t_max):
    log("Step: " + str(t))
    time.sleep(tick_speed)
    forest_map = run_simulation_step(forest_map,prob)
    visualize_fire(forest_map,window,canvas)

    window.update_idletasks()
    window.update()
log("Simulation end")
window.mainloop()


