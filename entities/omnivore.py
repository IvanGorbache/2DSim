import entities


class Omnivore(entities.MobileEntity):
    def __init__(self, position, t_steps, r_range):
        super().__init__('🐻', position, t_steps, r_range, [entities.Herbivore, entities.Predator, entities.Plant])

    def move(self, grid):
        next_pos = self.get_next_pos(grid)
        self.position = next_pos