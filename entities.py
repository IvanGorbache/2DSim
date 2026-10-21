import itertools
import math
from abc import ABC, abstractmethod
import random

class Entity(ABC):
    def __init__(self, sprite, position, t_steps):
        self.sprite = sprite
        self.position = position
        self.t_steps = t_steps
        self.max_t_steps = t_steps
    def tick(self):
        self.t_steps-=1

class MobileEntity(Entity):
    def __init__(self, sprite, position, t_steps, r_range, target_type):
        super().__init__(sprite, position, t_steps)
        self.r_range = r_range
        self.target_type = target_type

    @abstractmethod
    def move(self,grid):
        pass

    def get_next_pos(self, grid):
        next_pos = self.position
        neighborhood = [(1,1),(1,0),(1,-1),(0,1),(0,-1),(-1,1),(-1,0)]
        target = self.find_target(grid)
        if target is not None:
            shortest_distance = math.inf
            closest_neighbor = None
            for neighbor in neighborhood:
                distance = math.dist(target,add_cords(neighbor,self.position))
                if distance < shortest_distance:
                    shortest_distance = distance
                    closest_neighbor = neighbor
            next_pos = add_cords(self.position,closest_neighbor)

        else:
            rand_neighborhood = neighborhood.copy()
            random.shuffle(rand_neighborhood)
            for neighbor in rand_neighborhood:
                new_position = add_cords(neighbor,self.position)
                if 0 <= new_position[0] < len(grid) and 0 <= new_position[1] < len(grid[0]):
                    next_pos = new_position
                    break
        return next_pos

    def find_target(self, grid):
        closest_target = None
        closest_distance = math.inf
        r = range(-self.r_range, self.r_range+1)
        search_neighborhood = list(itertools.product(r,repeat=2))
        for neighbor in search_neighborhood:
            position = add_cords(neighbor,self.position)
            if 0<=position[0]<len(grid) and 0<=position[1]<len(grid[0]):
                for entity in grid[position[0]][position[1]]:
                    if isinstance(entity, self.target_type):
                        distance = math.dist(self.position, position)
                        if distance < closest_distance:
                            closest_distance = distance
                            closest_target = position
        return closest_target

class Plant(Entity):
    def __init__(self, position, t_steps):
        super().__init__('🌱', position, t_steps)
        self.trampled_by = Predator


class Herbivore(MobileEntity):
    def __init__(self, position, t_steps, r_range, t_cooldown):
        super().__init__('🐔', position, t_steps, r_range, Plant)
        self.t_cooldown = t_cooldown
        self.max_cooldown = t_cooldown

    def move(self,grid):
        next_pos = self.get_next_pos(grid)
        self.position = next_pos

class Predator(MobileEntity):
    def __init__(self, position, t_steps, r_range):
        super().__init__('🦊', position, t_steps, r_range,Herbivore)

    def move(self,grid):
        next_pos = self.get_next_pos(grid)
        self.position = next_pos







def add_cords(cord1,cord2):
    return cord1[0] + cord2[0], cord1[1] + cord2[1]