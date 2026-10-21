import yaml

import entities
from entities import Entity
import random


class Simulation:
    def __init__(self, grid_size, steps, T_plant, T_herbivore, R_herbivore_sight, T_cooldown, T_predator,
                 R_predator_sight):
        self.grid_size = grid_size
        self.steps = steps
        self.T_plant = T_plant
        self.T_herbivore = T_herbivore
        self.R_herbivore_sight = R_herbivore_sight
        self.T_cooldown = T_cooldown
        self.T_predator = T_predator
        self.R_predator_sight = R_predator_sight


def run_simulation():
    simulator = seed_loader()

    harbs = [entities.Herbivore((2, 2), simulator.T_herbivore, simulator.R_herbivore_sight, simulator.T_cooldown),

             ]
    preds = [entities.Predator((0, 0), simulator.T_predator, simulator.R_predator_sight),
             ]

    plants = [entities.Plant((1, 1), simulator.T_plant),
              entities.Plant((2, 1), simulator.T_plant),
              ]

    static_obj = [entities.StaticEntity((0, 2))]
    grid = [[[] for _ in range(simulator.grid_size[0])] for _ in range(simulator.grid_size[1])]
    place_on_grid(grid, harbs)
    place_on_grid(grid, preds)
    place_on_grid(grid, plants)
    place_on_grid(grid, static_obj)
    print_grid(grid)

    for i in range(simulator.steps):
        print("step ", i)
        move_on_grid(grid, preds, harbs)
        move_on_grid(grid, harbs, plants)
        trampled_by(grid, plants)
        reproduce(grid, harbs)
        tick_entity(grid, plants)
        tick_entity(grid, harbs)
        tick_entity(grid, preds)
        plant_random(grid, plants)
        grid = [[[] for _ in range(simulator.grid_size[0])] for _ in range(simulator.grid_size[0])]

        place_on_grid(grid, harbs)
        place_on_grid(grid, preds)
        place_on_grid(grid, plants)
        place_on_grid(grid, static_obj)

        print_grid(grid)


def plant_random(grid, plants):
    positions = [(x, y) for x in range(len(grid)) for y in range(len(grid[0]))]
    random.shuffle(positions)
    for position in positions:
        if len(grid[position[0]][position[1]]) == 0:
            plants.append(entities.Plant(position, 10))
            break


def tick_entity(grid, entity_list):
    for entity in entity_list:
        entity.tick()
        if entity.t_steps <= 0:
            entity_list.remove(entity)


def place_on_grid(grid, entity_list):
    for entity in entity_list:
        grid[entity.position[0]][entity.position[1]].append(entity)


def move_on_grid(grid, entity_list, target_entity_list):
    for entity in entity_list:
        entity.move(grid)

        target = list(
            ent for ent in grid[entity.position[0]][entity.position[1]] if isinstance(ent, entity.target_type))

        if len(target) > 0:
            target_entity_list.remove(target[0])
            grid[entity.position[0]][entity.position[1]].remove(target[0])
            entity.t_steps = entity.max_t_steps


def trampled_by(grid, plants):
    for plant in plants:
        pred = next((ent for ent in grid[plant.position[0]][plant.position[1]] if isinstance(ent, entities.Predator)),
                    None)
        if pred is not None:
            plants.remove(plant)


def reproduce(grid, entity_list):
    for entity in entity_list:
        target = next((ent for ent in grid[entity.position[0]][entity.position[1]] if isinstance(ent, type(entity))),
                      None)
        if (target is not None and entity.t_cooldown >= entity.max_cooldown and entity.t_cooldown >=
                target.max_cooldown):
            entity.t_cooldown = 0
            target.t_cooldown = 0
            neighborhood = [(1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0)]
            random.shuffle(neighborhood)
            for neighbor in neighborhood:

                new_position = entities.add_cords(neighbor, entity.position)
                if (0 <= new_position[0] < len(grid) and 0 <= new_position[1] < len(grid[0])
                        and not grid[new_position[0]][new_position[1]] and not any(
                            isinstance(ent, entities.StaticEntity) for ent in grid[new_position[0]][new_position[1]])):
                    new_entity = entities.Herbivore(new_position, 10, 10, 5)
                    grid[new_position[0]][new_position[1]].append(new_entity)
                    entity_list.append(new_entity)
                    break


def print_grid(grid):
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if len(grid[i][j]) > 0:
                print(grid[i][j][0].sprite, end="")
            else:
                print("🟫", end="")
        print("")


def seed_loader():
    with open(f'config.yaml', 'r') as config:
        output = yaml.safe_load(config)
    return Simulation([int(x) for x in output.get('grid_size', [1, 1])],
                      int(output.get('steps', 1)),
                      int(output.get('T_plant', 1)),
                      int(output.get('T_herbivore', 1)),
                      int(output.get('R_herbivore', 1)),
                      int(output.get('T_cooldown', 1)),
                      int(output.get('T_predator', 1)),
                      int(output.get('R_predator_sight', 2)))


if __name__ == '__main__':
    run_simulation()
