import random

import entities


class StaticEntity(entities.Entity):
    def __init__(self, position):
        super().__init__(('🌲', '🗿', '⛰️')[random.randint(0, 2)], position, 0)