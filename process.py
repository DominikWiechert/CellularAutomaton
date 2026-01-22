from typing import List
import random
import yaml
import os.path
from custom_datatypes import MapNode, NodeStatus, Probability, OptimisedCell
import numpy as np


def log(msg):
    DEBUG = True
    if DEBUG == True:
        print(f'\033[92m **',msg,f'**\033[0m')

def calculate_probability() -> Probability:
    wind_v_max = 100
    if os.path.isfile("config.yaml"):
        with open("config.yaml", 'r') as file:
            config = yaml.safe_load(file)
        log("Probability config loaded")
    else:
        config = {
            "probability": 30,
            "wind_speed_x": -80,
            "wind_speed_y": -30
        }
        with open("config.yaml", 'w') as file:
            yaml.dump(config, file,default_flow_style=False)
        log("Probability config not existing")
        log("Standard probability config file created")
    probability = Probability(config["probability"])

    probability.east = probability.base * (1 + config["wind_speed_x"]/wind_v_max)
    probability.west = probability.base * (1 - config["wind_speed_x"]/wind_v_max)
    probability.north = probability.base * (1 + config["wind_speed_y"]/wind_v_max)
    probability.south = probability.base * (1 - config["wind_speed_y"]/wind_v_max)

    log("Probability calculated")
    log("Spread prob. east: " + str(probability.east))
    log("Spread prob. west: " + str(probability.west))
    log("Spread prob. north: " + str(probability.north))
    log("Spread prob. south: " + str(probability.south))
    return probability

def run_simulation_step(forest_map: List[List[MapNode]], probability: Probability) -> List[List[MapNode]]:
    forest_map_temp = forest_map.copy()
    for k in range(len(forest_map)):
        for l in range(len(forest_map[0])):
            if forest_map[k][l].status == NodeStatus.BURNING:
                #-- Spread due to closeness --
                if k != 0:
                    if forest_map[k - 1][l].status == NodeStatus.INTACT and random.randint(1, 100) <= probability.west: #west
                        forest_map_temp[k - 1][l].status = NodeStatus.BURNING
                if l != 0:
                    if forest_map[k][l - 1].status == NodeStatus.INTACT and random.randint(1, 100) <= probability.south: #south
                        forest_map_temp[k][l - 1].status = NodeStatus.BURNING
                if k != len(forest_map) - 1:
                    if forest_map[k + 1][l].status == NodeStatus.INTACT and random.randint(1, 100) <= probability.east: #east
                        forest_map_temp[k + 1][l].status = NodeStatus.BURNING
                if l != len(forest_map[0]) - 1:
                    if forest_map[k][l + 1].status == NodeStatus.INTACT and random.randint(1, 100) <= probability.north: #north
                        forest_map_temp[k][l + 1].status = NodeStatus.BURNING

                #-- Burning down --
                if forest_map[k][l].burning_duration >= 5:
                    forest_map_temp[k][l].status = NodeStatus.BURNT_DOWN
                else:
                    forest_map_temp[k][l].burning_duration += 1

    return forest_map_temp

def print_map_2_console(forest_map: List[List[MapNode]]) -> None:
    for k in range(len(forest_map)):
        for l in range(len(forest_map[0])):
            print(forest_map[k][l].status)


def simplify_forest_map(forest_map: List[List[MapNode]]) -> List[List[str]]:
    simplified_forest_map  = [["cyan" for x in range(len(forest_map[0]))] for y in range(len(forest_map))] #cyan indicates error
    for i in range(len(forest_map)):
        for j in range(len(forest_map[0])):
            if forest_map[i][j].status == NodeStatus.INTACT:
                simplified_forest_map[i][j] = "green"
            elif forest_map[i][j].status == NodeStatus.BURNING:
                simplified_forest_map[i][j] = "red"
            elif forest_map[i][j].status == NodeStatus.BURNT_DOWN:
                simplified_forest_map[i][j] = "black"
            elif forest_map[i][j].status == NodeStatus.CANNOT_BURN:
                simplified_forest_map[i][j] = "grey"

    return simplified_forest_map

def count_cells(forest_map):
    g_count=0
    r_count=0
    b_count=0
    gr_count=0
    unk_count = 0
    for i in range(len(forest_map)):
        for j in range(len(forest_map[0])):
            if forest_map[i,j] == b'green':
                g_count += 1
            elif forest_map[i,j] == b'red':
                r_count += 1
            elif forest_map[i,j] == b'black':
                b_count += 1
            elif forest_map[i,j] == b'grey':
                gr_count += 1
            else:
                unk_count += 1
    return np.array([[g_count],[r_count],[b_count],[gr_count],[unk_count]])

def optimised_render(map,next_map):
    optimised_rendered = []

    for i in range(len(map)):
        for j in range(len(map[0])):
            if map[i][j] != next_map[i][j]:
                cell = OptimisedCell(next_map[i][j], i,j)
                optimised_rendered.append(cell)
                log(OptimisedCell(next_map[i][j], i,j).x)
                log(OptimisedCell(next_map[i][j], i,j).y)
    return optimised_rendered