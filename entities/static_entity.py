import random

import entities


class StaticEntity(entities.Entity):
    def __init__(self, position):
        super().__init__(('🌲', '🗿', '⛰️')[random.randint(0, 2)], position, 0)

    def simulate_step(self, grid, all_entities):
        pass

    def add_observer(self, observer):
        pass

    def notify_observer(self):
        pass
