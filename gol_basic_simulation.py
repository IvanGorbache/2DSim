from consts import *


def start_sim(height: int, width: int, steps: int, x: int, y: int):
    grid = [[0 for _ in range(width)] for _ in range(height)]
    grid_seed(grid, x, y)
    print_grid(grid)
    for i in range(steps):
        print("step: ", i)
        apply_update(grid, get_update(grid))
        print_grid(grid)


def get_update(grid: list[list[int]]) -> list[list[int]]:
    update_grid = [[0 for _ in range(len(grid[0]))] for _ in range(len(grid))]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            counter = 0
            for neighbour in NEIGHBORS:
                point = (i + neighbour[0], j + neighbour[1])
                if point_within_bounds(grid, point):
                    if grid[point[0]][point[1]] == ALIVE:
                        counter += 1

            if grid[i][j] == ALIVE and (counter < MINIMUM_POPULATION or counter > OPTIMAL_POPULATION):
                update_grid[i][j] = DEAD_UPDATE

            elif grid[i][j] == DEAD and counter == OPTIMAL_POPULATION:
                update_grid[i][j] = REVIVE_UPDATE
    return update_grid


def point_within_bounds(grid: list[list[int]], point: tuple[int, int]) -> bool:
    return 0 <= point[0] < len(grid) and 0 <= point[1] < len(grid[0])


def apply_update(grid: list[list[int]], update_grid: list[list[int]]):
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            grid[i][j] += update_grid[i][j]


def print_grid(grid: list[list[int]]):
    output = ""
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == ALIVE:
                output += "■"
            else:
                output += "□"
        output += "\n"
    print(output)


def grid_seed(grid: list[list[int]], x: int, y: int):
    f = open("hammerhead.txt")
    pattern = f.read().splitlines()

    if len(grid) < len(pattern) + x or len(grid[0]) < len(pattern[0]) + y:
        print("Couldn't load chosen seed. Please increase grid size.")
    else:
        for i in range(len(pattern)):
            for j in range(len(pattern[i])):
                if pattern[i][j] == '1':
                    grid[x][y + j] = 1
                else:
                    grid[x][y + j] = 0
            x += 1


if __name__ == '__main__':
    start_sim(GRID_HEIGHT, GRID_WIDTH, STEPS, SEED_CORD_X, SEED_CORD_Y)
