import entities


class Herbivore(entities.MobileEntity):
    def __init__(self, position, t_steps, r_range, t_cooldown):
        super().__init__('🐔', position, t_steps, r_range, [entities.Plant])
        self.t_cooldown = t_cooldown
        self.max_cooldown = t_cooldown

    def move(self, grid):
        next_pos = self.get_next_pos(grid)
        self.position = next_pos
        self.t_cooldown += 1
