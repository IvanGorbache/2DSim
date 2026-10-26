import entities


class Plant(entities.Entity):
    def __init__(self, position, t_steps):
        super().__init__('🌱', position, t_steps)
        self.trampled_by = entities.Predator