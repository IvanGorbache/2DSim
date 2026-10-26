import random

import entities


class Herbivore(entities.MobileEntity):
    def __init__(self, position, t_steps, r_range, t_cooldown):
        super().__init__('🐔', position, t_steps, r_range, [entities.Plant])
        self.t_cooldown = t_cooldown
        self.max_cooldown = t_cooldown

    def simulate_step(self, grid, all_entities):
        self.t_cooldown += 1
        self.move(grid, all_entities)
        self.reproduce(grid, all_entities)

    def reproduce(self, grid, all_entities):
        has_reproduced = False
        target = next(
            (ent for ent in grid[self.position[0]][self.position[1]] if isinstance(ent, type(self))),
            None)
        if (target is not None and self.t_cooldown >= self.max_cooldown and target.t_cooldown >=
                target.max_cooldown and target is not self):
            self.t_cooldown = 0
            target.t_cooldown = 0
            neighborhood = [(1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0)]
            random.shuffle(neighborhood)
            for neighbor in neighborhood:

                new_position = entities.base.add_cords(neighbor, self.position)
                if (0 <= new_position[0] < len(grid) and 0 <= new_position[1] < len(grid[0])
                        and not grid[new_position[0]][new_position[1]] and not any(
                            isinstance(ent, entities.StaticEntity) for ent in
                            grid[new_position[0]][new_position[1]])):
                    new_entity = entities.Herbivore(new_position, self.max_t_steps, self.r_range,
                                                    self.max_cooldown)
                    grid[new_position[0]][new_position[1]].append(new_entity)
                    all_entities.append(new_entity)
                    has_reproduced = True
                    print("fuck")
                    break

        return has_reproduced
