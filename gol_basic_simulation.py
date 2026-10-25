import sys

import imageio
import numpy as np

from consts import *


def grid_to_image_frame(grid: list[list[int]], scale:int):
    """
    Converts a grid frame into an image frame.
    :param scale: Scale factor for each pixel
    :param grid: The grid representing the current simulation state.
    :return: a frame of the current simulation state.
    """
    height = len(grid)
    width = len(grid[0])
    image = np.zeros((height, width), dtype=np.uint8)

    for i in range(height):
        for j in range(width):
            if grid[i][j] == ALIVE:
                image[i, j] = BLACK
            else:
                image[i, j] = WHITE
    scaled_image = np.repeat(np.repeat(image, scale, axis=0), scale, axis=1)
    return np.stack((scaled_image,) * COLOR_SPACE, axis=-1)


def start_sim(height: int, width: int, steps: int, x: int, y: int, input_file: str):
    """
    This function is responsible for the running of the simulation.
    :param input_file:
    :param height: The height of the simulation grid.
    :param width: The width of the simulation grid.
    :param steps: The number of simulation steps.
    :param x: The x coordinate of the initial position of the simulation seed
    :param y: The y coordinate of the initial position of the simulation seed
    :return:
    """
    grid = [[0 for _ in range(width)] for _ in range(height)]
    grid_seed(grid, x, y, input_file)
    print_grid(grid)
    frames = [grid_to_image_frame(grid, SCALE)]
    for i in range(steps):
        print("step: ", i)
        apply_update(grid, get_update(grid))
        print_grid(grid)
        frames.append(grid_to_image_frame(grid, SCALE))
    imageio.mimsave('simulation.gif', frames, fps=FPS, loop=0)


def get_update(grid: list[list[int]]) -> list[list[int]]:
    """
    This function is responsible for generating the update grid.
    :param grid: The grid representing the current simulation state.
    :return: update_grid: The grid used for updating the simulation state.
    """
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
    """
    Checks if a point within the grid bounds.
    :param grid: The grid representing the current simulation state.
    :param point: The point to check.
    :return: Whether the point is within the grid bounds.
    """
    return 0 <= point[0] < len(grid) and 0 <= point[1] < len(grid[0])


def apply_update(grid: list[list[int]], update_grid: list[list[int]]):
    """
    Applies the update grid to teh current grid to make the simulation step simultaneous across all grid cells.
    :param grid: The grid representing the current simulation state.
    :param update_grid: The grid used for updating the simulation state.
    :return:
    """
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            grid[i][j] += update_grid[i][j]


def print_grid(grid: list[list[int]]):
    """
    Prints the current grid state.
    :param grid: The grid representing the current simulation state.
    :return:
    """
    output = ""
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == ALIVE:
                output += "■"
            else:
                output += "□"
        output += "\n"
    print(output)


def grid_seed(grid: list[list[int]], x: int, y: int, input_file: str):
    """
    Places the seed within the grid bounds based on the x and y coordinates of the upper left corner of the seed.
    :param input_file: The file for the initial seed pattern
    :param grid: The grid representing the current simulation state.
    :param x: The x coordinate of the initial position of the simulation seed.
    :param y: The y coordinate of the initial position of the simulation seed.
    :raises: ValueError: If the seed cannot be placed within the grid bounds.
    """
    with open(input_file) as f:
        pattern = f.read().splitlines()

        if len(grid) < len(pattern) + x or len(grid[0]) < len(pattern[0]) + y:
            raise ValueError("Grid size too small for the chosen seed.")
        else:
            for i in range(len(pattern)):
                for j in range(len(pattern[i])):
                    if pattern[i][j] == LIVE_SEED_CELL:
                        grid[x][y + j] = ALIVE
                    else:
                        grid[x][y + j] = DEAD
                x += 1


if __name__ == '__main__':
    if len(sys.argv) == REQUIRED_ARGUMENTS:
        sim_height = int(sys.argv[HEIGHT_ARG])
        sim_width = int(sys.argv[WIDTH_ARG])
        sim_steps = int(sys.argv[STEPS_ARG])
        seed_x = int(sys.argv[SEED_X_ARG])
        seed_y = int(sys.argv[SEED_Y_ARG])
        file = str(sys.argv[FILE_ARG])
    else:
        print("Missing parameters. Using default parameters")
        sim_height = DEFAULT_GRID_HEIGHT
        sim_width = DEFAULT_GRID_WIDTH
        sim_steps = DEFAULT_STEPS
        seed_x = SEED_CORD_X
        seed_y = SEED_CORD_Y
        file = DEFAULT_FILE

    start_sim(sim_height, sim_width, sim_steps, seed_x, seed_y, file)
