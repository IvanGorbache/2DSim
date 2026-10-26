import itertools
import math
from abc import ABC, abstractmethod
import random

import entities


class Entity(ABC):
    def __init__(self, sprite, position, t_steps):
        self.sprite = sprite
        self.position = position
        self.t_steps = t_steps
        self.max_t_steps = t_steps

    def tick(self, grid, all_entities):
        self.t_steps -= 1
        if self.t_steps <= 0:
            grid[self.position[0]][self.position[1]].remove(self)
            all_entities.remove(self)

    @abstractmethod
    def simulate_step(self, grid, all_entities):
        pass


class MobileEntity(Entity, ABC):
    def __init__(self, sprite, position, t_steps, r_range, target_types):
        super().__init__(sprite, position, t_steps)
        self.r_range = r_range
        self.target_types = target_types
        self.has_moved_random = True

    def simulate_step(self, grid, all_entities):
        self.move(grid, all_entities)
        self.tick(grid, all_entities)

    def move(self, grid, all_entities):
        next_pos = self.position
        neighborhood = [(1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (0, 0)]
        target = self.find_target(grid)
        if target is not None:
            shortest_distance = math.inf
            closest_neighbor = None
            for neighbor in neighborhood:
                distance = math.dist(target, add_cords(neighbor, self.position))
                if distance < shortest_distance:
                    shortest_distance = distance
                    closest_neighbor = neighbor
            next_pos = add_cords(self.position, closest_neighbor)
            self.has_moved_random = False

        else:
            rand_neighborhood = neighborhood.copy()
            rand_neighborhood.remove((0, 0))
            random.shuffle(rand_neighborhood)
            for neighbor in rand_neighborhood:
                new_position = add_cords(neighbor, self.position)
                if (0 <= new_position[0] < len(grid) and 0 <= new_position[1] < len(grid[0])
                        and not any(
                            isinstance(ent, entities.StaticEntity) for ent in grid[new_position[0]][new_position[1]])):
                    next_pos = new_position
                    break
            self.has_moved_random = True
        grid[self.position[0]][self.position[1]].remove(self)
        self.position = next_pos
        grid[self.position[0]][self.position[1]].append(self)

        for target_type in self.target_types:
            target = list(
                ent for ent in grid[self.position[0]][self.position[1]] if isinstance(ent, target_type))

            if len(target) > 0:
                all_entities.remove(target[0])
                grid[self.position[0]][self.position[1]].remove(target[0])
                self.t_steps = self.max_t_steps
        return next_pos

    def find_target(self, grid):
        closest_target = None
        closest_distance = math.inf
        r = range(-self.r_range, self.r_range + 1)
        search_neighborhood = list(itertools.product(r, repeat=2))
        for neighbor in search_neighborhood:
            position = add_cords(neighbor, self.position)
            if 0 <= position[0] < len(grid) and 0 <= position[1] < len(grid[0]):
                for entity in grid[position[0]][position[1]]:
                    for target_type in self.target_types:
                        if isinstance(entity, target_type):
                            distance = math.dist(self.position, position)
                            if distance < closest_distance:
                                closest_distance = distance
                                closest_target = position
        return closest_target


def add_cords(cord1, cord2):
    return cord1[0] + cord2[0], cord1[1] + cord2[1]
