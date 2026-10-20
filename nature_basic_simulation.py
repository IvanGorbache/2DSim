import yaml

import entities
from entities import Entity


def run_simulation():
    seed_loader()
    grid = [[[0] for _ in range(20)] for _ in range(20)]
    harbs = [entities.Herbivore((2,4),10,5,5),
             entities.Herbivore((6, 3), 10, 5, 5),
             entities.Herbivore((12, 9), 10, 5, 5),
             entities.Herbivore((11, 1), 10, 5, 5)
             ]
    preds = [entities.Predator((4,8),5,8),
             entities.Predator((5, 6), 5, 8),
             entities.Predator((6, 4), 5, 8),
             entities.Predator((2, 7), 5, 8)
             ]

    plants = [entities.Plant((6,2),10),
              entities.Plant((0, 4), 10),
              entities.Plant((7, 1), 10),
              entities.Plant((3, 6), 10)
              ]
    for i in range(10):
        print("step ",i)
        for plant in plants:
            plant.tick()
            if plant.t_steps>=0:
                grid[plant.position[0]][plant.position[1]].append(plant)
        for plant in harbs:
            plant.tick()
            if plant.t_steps>=0:
                grid[plant.position[0]][plant.position[1]].append(plant)
        for plant in preds:
            plant.tick()
            if plant.t_steps>=0:
                grid[plant.position[0]][plant.position[1]].append(plant)

        for plant in harbs:
            plant.move(grid)
        for plant in preds:
            plant.move(grid)

        print_grid(grid)

def print_grid(grid):
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if len(grid[i][j])>1:
                print(grid[i][j][1].sprite,end="")
            else:
                print("🟫",end="")
        print("")

def seed_loader():
    with open(f'config.yaml', 'r') as config:
        output = yaml.safe_load(config)
    print(output)


if __name__ == '__main__':
    run_simulation()