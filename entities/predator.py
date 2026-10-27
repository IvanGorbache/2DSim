import entities


class Predator(entities.MobileEntity):
    def __init__(self, position, t_steps, r_range):
        super().__init__('🦊', position, t_steps, r_range, [entities.Herbivore])

    def simulate_step(self, grid, all_entities):
        self.move(grid, all_entities)
        self.trample(grid, all_entities)
        self.tick(grid, all_entities)

    def trample(self, grid, all_entities):
        for entity in grid[self.position[0]][self.position[1]]:
            if isinstance(entity, entities.Plant):
                grid[self.position[0]][self.position[1]].remove(entity)
                all_entities[entities.Plant].remove(entity)
                break



