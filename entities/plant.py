import random

import entities


class Plant(entities.Entity):
    def __init__(self, position, t_steps):
        super().__init__('🌱', position, t_steps)

    def simulate_step(self, grid, all_entities):
        self.tick(grid, all_entities)


