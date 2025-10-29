from typing import List
import random
from custom_datatypes import MapNode, NodeStatus

def log(msg):
    DEBUG = True
    if DEBUG == True:
        print(f'\033[92m **',msg,f'**\033[0m')

def calculate_probability():
    probability = 3
    log("Probability calculated")

    return probability

def run_simulation_step(forest_map: List[List[MapNode]]) -> List[List[MapNode]]:
    prob = calculate_probability()

    for k in range(len(forest_map)):
        for l in range(len(forest_map[0])):
            if forest_map[k][l].status == NodeStatus.BURNING:
                if k != 0:
                    if forest_map[k - 1][l].status == NodeStatus.INTACT and random.randint(1, prob) == 1:
                        forest_map[k - 1][l].status = NodeStatus.BURNING
                if l != 0:
                    if forest_map[k][l - 1].status == NodeStatus.INTACT and random.randint(1, prob) == 1:
                        forest_map[k][l - 1].status = NodeStatus.BURNING
                if k != len(forest_map) - 1:
                    if forest_map[k + 1][l].status == NodeStatus.INTACT and random.randint(1, prob) == 1:
                        forest_map[k + 1][l].status = NodeStatus.BURNING
                if l != len(forest_map[0]) - 1:
                    if forest_map[k][l + 1].status == NodeStatus.INTACT and random.randint(1, prob) == 1:
                        forest_map[k][l + 1].status = NodeStatus.BURNING

    return forest_map

def print_map_2_console(forest_map: List[List[MapNode]]) -> None:
    for k in range(len(forest_map)):
        for l in range(len(forest_map[0])):
            print(forest_map[k][l].status)