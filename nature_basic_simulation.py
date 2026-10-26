import sys

import yaml
import entities
import random


class Simulation:
    def __init__(self, grid_size, steps, T_plant, T_herbivore, R_herbivore_sight, T_cooldown, T_predator,
                 R_predator_sight, T_omnivore, R_omnivore_sight):
        self.grid_size = grid_size
        self.steps = steps
        self.T_plant = T_plant
        self.T_herbivore = T_herbivore
        self.R_herbivore_sight = R_herbivore_sight
        self.T_cooldown = T_cooldown
        self.T_predator = T_predator
        self.R_predator_sight = R_predator_sight
        self.T_omnivore = T_omnivore
        self.R_omnivore_sight = R_omnivore_sight
        self.predator_entities = []
        self.herbivore_entities = []
        self.plant_entities = []
        self.static_entities = []
        self.omnivore_entities = []
        self.all_entities = {entities.StaticEntity: self.static_entities,
                             entities.Predator: self.predator_entities,
                             entities.Herbivore: self.herbivore_entities,
                             entities.Plant: self.plant_entities,
                             entities.Omnivore: self.omnivore_entities
                             }
        self.grid = [[[] for _ in range(self.grid_size[0])] for _ in range(self.grid_size[1])]

    def place_entities(self):
        for entity_list in self.all_entities.values():
            for entity in entity_list:
                self.grid[entity.position[0]][entity.position[1]].append(entity)

    def clear_grid(self):
        self.grid = [[[] for _ in range(self.grid_size[0])] for _ in range(self.grid_size[1])]

    def print_grid(self):
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                if len(self.grid[i][j]) > 0:
                    print(self.grid[i][j][0].sprite, end="")
                else:
                    print("🟫", end="")
            print("")

    def move_entities(self, entity_type):
        for entity in self.all_entities[entity_type]:
            for target_type in entity.target_types:
                entity.move(self.grid)

                target = list(
                    ent for ent in self.grid[entity.position[0]][entity.position[1]] if isinstance(ent, target_type))

                if len(target) > 0:
                    self.all_entities[target_type].remove(target[0])
                    self.grid[entity.position[0]][entity.position[1]].remove(target[0])
                    entity.t_steps = entity.max_t_steps

    def tick_entity(self, entity_type):
        for entity in self.all_entities[entity_type]:
            entity.tick()
            if entity.t_steps <= 0:
                self.all_entities[entity_type].remove(entity)

    def plant_random(self):
        positions = [(x, y) for x in range(len(self.grid)) for y in range(len(self.grid[0]))]
        random.shuffle(positions)
        for position in positions:
            if len(self.grid[position[0]][position[1]]) == 0:
                self.all_entities[entities.Plant].append(entities.Plant(position, self.T_plant))
                break

    def reproduce(self):
        has_reproduced = False
        for entity in self.herbivore_entities:
            target = next(
                (ent for ent in self.grid[entity.position[0]][entity.position[1]] if isinstance(ent, type(entity))),
                None)
            if (target is not None and entity.t_cooldown >= entity.max_cooldown and entity.t_cooldown >=
                    target.max_cooldown and target is not entity):
                entity.t_cooldown = 0
                target.t_cooldown = 0
                neighborhood = [(1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0)]
                random.shuffle(neighborhood)
                for neighbor in neighborhood:

                    new_position = entities.add_cords(neighbor, entity.position)
                    if (0 <= new_position[0] < len(self.grid) and 0 <= new_position[1] < len(self.grid[0])
                            and not self.grid[new_position[0]][new_position[1]] and not any(
                                isinstance(ent, entities.StaticEntity) for ent in
                                self.grid[new_position[0]][new_position[1]])):
                        new_entity = entities.Herbivore(new_position, self.T_herbivore, self.R_herbivore_sight,
                                                        self.T_cooldown)
                        self.grid[new_position[0]][new_position[1]].append(new_entity)
                        self.herbivore_entities.append(new_entity)
                        has_reproduced = True
                        break
        return has_reproduced

    def trampled_by(self):
        for plant in self.plant_entities:
            pred = next(
                (ent for ent in self.grid[plant.position[0]][plant.position[1]] if isinstance(ent, entities.Predator)),
                None)
            if pred is not None:
                self.plant_entities.remove(plant)


def run_simulation():
    simulator = seed_loader()

    simulator.place_entities()
    simulator.print_grid()
    for i in range(simulator.steps):
        print("step ", i)

        simulator.move_entities(entities.Predator)
        simulator.move_entities(entities.Herbivore)
        simulator.move_entities(entities.Omnivore)
        simulator.reproduce()
        simulator.trampled_by()

        simulator.tick_entity(entities.Predator)
        simulator.tick_entity(entities.Herbivore)
        simulator.tick_entity(entities.Omnivore)
        simulator.tick_entity(entities.Plant)

        simulator.plant_random()

        simulator.clear_grid()

        simulator.place_entities()

        simulator.print_grid()


def seed_loader():
    with open(sys.argv[1], 'r') as config:
        output = yaml.safe_load(config)
    simulator = Simulation([x for x in output.get('grid_size', [1, 1])],
                           output.get('steps', 1),
                           output.get('T_plant', 1),
                           output.get('T_herbivore', 1),
                           output.get('R_herbivore', 1),
                           output.get('T_cooldown', 1),
                           output.get('T_predator', 1),
                           output.get('R_predator_sight', 2),
                           output.get('T_omnivore', 1),
                           output.get('R_omnivore_sight', 1))
    for entry in output.get('entities', []):
        entry_type = entry['type'].lower()
        position = tuple(int(cord) for cord in entry['position'])
        if entry_type == 'static':
            simulator.static_entities.append(entities.StaticEntity(position))
        elif entry_type == 'predator':
            simulator.predator_entities.append(
                entities.Predator(position, simulator.T_predator, simulator.R_predator_sight))
        elif entry_type == 'herbivore':
            simulator.herbivore_entities.append(
                entities.Herbivore(position, simulator.T_herbivore, simulator.R_herbivore_sight, simulator.T_cooldown))
        elif entry_type == 'plant':
            simulator.plant_entities.append(entities.Plant(position, simulator.T_plant))
        elif entry_type == 'omnivore':
            simulator.omnivore_entities.append(
                entities.Omnivore(position, simulator.T_omnivore, simulator.R_omnivore_sight))

    return simulator


if __name__ == '__main__':
    run_simulation()
