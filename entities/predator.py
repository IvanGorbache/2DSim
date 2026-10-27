import entities
from const import *


class Predator(entities.MobileEntity):
    def __init__(self, position, t_steps, r_range):
        super().__init__('🦊', position, t_steps, r_range, [entities.Herbivore])
        self.consumption_observer = []

    def add_observer(self, observer):
        self.consumption_observer.append(observer)

    def simulate_step(self, grid, all_entities):
        self.move(grid)
        if self.consume(grid, all_entities):
            self.notify_observer()
        self.trample(grid, all_entities)
        self.tick(grid, all_entities)

    def notify_observer(self):
        for observer in self.consumption_observer:
            observer.update(CONSUMPTION, {})

    def trample(self, grid, all_entities):
        for entity in grid[self.position[0]][self.position[1]]:
            if isinstance(entity, entities.Plant):
                grid[self.position[0]][self.position[1]].remove(entity)
                all_entities[entities.Plant].remove(entity)
                break
