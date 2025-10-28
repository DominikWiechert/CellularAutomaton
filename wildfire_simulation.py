from input import get_forest_map
from output import visualize_fire
from process import run_simulation_step

# Feel free to edit the structure :)
forest_map = get_forest_map()

t_max = 100
for t in range(t_max):
    # Just an idea: Instead of calling simulation step function,
    # we might as well generate a class for forest map, which then has
    # a method to run the simulation step
    forest_map = run_simulation_step(forest_map)
    visualize_fire(forest_map)