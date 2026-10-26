import entities


class Omnivore(entities.MobileEntity):
    def __init__(self, position, t_steps, r_range):
        super().__init__('🐻', position, t_steps, r_range, [entities.Herbivore, entities.Predator, entities.Plant])

