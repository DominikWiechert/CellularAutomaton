from typing import List
import random
import yaml
import os.path
from custom_datatypes import MapNode, NodeStatus

def log(msg):
    DEBUG = True
    if DEBUG == True:
        print(f'\033[92m **',msg,f'**\033[0m')

def calculate_probability():
    if os.path.isfile("config.yaml"):
        with open("config.yaml", 'r') as file:
            config = yaml.safe_load(file)
        log("Probability config loaded")
    else:
        config = {
            "probability": 30,
            "wind_speed_x": -2,
            "wind_speed_y": -1
        }
        with open("config.yaml", 'w') as file:
            yaml.dump(config, file,default_flow_style=False)
        log("Probability config not existing")
        log("Standard probability config file created")
    probability = config["probability"]

    log("Probability calculated")

    return probability

def run_simulation_step(forest_map: List[List[MapNode]], probability) -> List[List[MapNode]]:
    forest_map_temp = forest_map.copy()
    for k in range(len(forest_map)):
        for l in range(len(forest_map[0])):
            if forest_map[k][l].status == NodeStatus.BURNING:
                #-- Spread due to closeness --
                if k != 0:
                    if forest_map[k - 1][l].status == NodeStatus.INTACT and random.randint(1, 100) <= probability:
                        forest_map_temp[k - 1][l].status = NodeStatus.BURNING
                if l != 0:
                    if forest_map[k][l - 1].status == NodeStatus.INTACT and random.randint(1, 100) <= probability:
                        forest_map_temp[k][l - 1].status = NodeStatus.BURNING
                if k != len(forest_map) - 1:
                    if forest_map[k + 1][l].status == NodeStatus.INTACT and random.randint(1, 100) <= probability:
                        forest_map_temp[k + 1][l].status = NodeStatus.BURNING
                if l != len(forest_map[0]) - 1:
                    if forest_map[k][l + 1].status == NodeStatus.INTACT and random.randint(1, 100) <= probability:
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