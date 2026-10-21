import yaml

import entities
from entities import Entity
import random


def run_simulation():
    seed_loader()

    harbs = [entities.Herbivore((2, 2), 10, 10, 5),
             entities.Herbivore((2, 2), 10, 10, 5)
             ]
    preds = [entities.Predator((2, 0), 10, 10)
             ]

    plants = [entities.Plant((1, 1), 10),
              entities.Plant((1, 2), 10),
              entities.Plant((2, 1), 10)
              ]
    grid = [[[] for _ in range(3)] for _ in range(3)]
    place_on_grid(grid, harbs)
    place_on_grid(grid, preds)
    place_on_grid(grid, plants)
    print_grid(grid)

    for i in range(30):
        print("step ", i)
        move_on_grid(grid, preds, harbs)
        move_on_grid(grid, harbs, plants)
        trampled_by(grid, plants)

        grid = [[[] for _ in range(3)] for _ in range(3)]

        place_on_grid(grid, harbs)
        place_on_grid(grid, preds)
        place_on_grid(grid, plants)

        print_grid(grid)
        #plant_random(grid,plants)


def plant_random(grid, plants):
    positions = [(x, y) for x in range(len(grid)) for y in range(len(grid[0]))]
    random.shuffle(positions)
    for position in positions:
        if len(grid[position[0]][position[1]]) == 0:
            plants.append(entities.Plant(position, 10))
            break


def place_on_grid(grid, entity_list):
    for entity in entity_list:
        entity.tick()
        if entity.t_steps <= 0:
            entity_list.remove(entity)
            continue
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
        if target is not None:
            entity.t_cooldown = 0
            target.t_cooldown = 0
            neighborhood = [(1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0)]
            random.shuffle(neighborhood)
            for neighbor in neighborhood:
                new_position = entities.add_cords(neighbor, entity.position)


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
    print(output)


if __name__ == '__main__':
    run_simulation()
