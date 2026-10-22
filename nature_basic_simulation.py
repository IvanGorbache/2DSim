import copy
import os

import numpy as np
import yaml
import entities
import random
import logging
from abc import ABC, abstractmethod
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class SimulatorObserver(ABC):
    @abstractmethod
    def update(self, data):
        pass


class SimulationAlertSystem(SimulatorObserver):
    def update(self, data):
        logger.info(data)


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
        self.observers = []
        self.entity_count = []
        self.reproduction_count = []
        self.consumption_count = {
            entities.Predator: [],
            entities.Herbivore: [],
            entities.Omnivore: []
        }
        self.grid_history = []

    def log_entity_count(self):
        self.entity_count.append({
            entities.Predator: len(self.predator_entities),
            entities.Herbivore: len(self.herbivore_entities),
            entities.Plant: len(self.plant_entities),
            entities.Omnivore: len(self.omnivore_entities)
        })

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, data):
        for observer in self.observers:
            observer.update(data)

    def place_entities(self):
        for entity_list in self.all_entities.values():
            for entity in entity_list:
                self.grid[entity.position[0]][entity.position[1]].append(entity)

    def clear_grid(self):
        self.log_grid_traffic()
        self.grid = [[[] for _ in range(self.grid_size[0])] for _ in range(self.grid_size[1])]

    def log_grid_traffic(self):
        self.grid_history.append([[len(self.grid[i][j]) for i in range(self.grid_size[0])]
                                  for j in range(self.grid_size[1])])

    def print_grid(self):
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                if len(self.grid[i][j]) > 0:
                    print(self.grid[i][j][0].sprite, end="")
                else:
                    print("🟫", end="")
            print("")

    def move_entities(self, entity_type):
        current_consumption = 0
        for entity in self.all_entities[entity_type]:
            for target_type in entity.target_types:
                entity.move(self.grid)

                target = list(
                    ent for ent in self.grid[entity.position[0]][entity.position[1]] if isinstance(ent, target_type))

                if len(target) > 0:
                    if len(self.all_entities[target_type]) == 1:
                        self.notify_observers("The last of the " + type(target[0]).__name__ + " has been consumed")
                    self.all_entities[target_type].remove(target[0])
                    self.grid[entity.position[0]][entity.position[1]].remove(target[0])
                    entity.t_steps = entity.max_t_steps
                    if isinstance(entity, entities.Predator):
                        self.notify_observers("A predator has eaten a herbivore")
                    current_consumption += 1
        self.consumption_count[entity_type].append(current_consumption)

    def tick_entity(self, entity_type):
        for entity in self.all_entities[entity_type]:
            entity.tick()
            if entity.t_steps <= 0:
                if len(self.all_entities[entity_type]) == 1:
                    self.notify_observers("The last of the " + type(entity).__name__ + " has been died of old age")
                self.all_entities[entity_type].remove(entity)

    def plant_random(self):
        positions = [(x, y) for x in range(len(self.grid)) for y in range(len(self.grid[0]))]
        random.shuffle(positions)
        for position in positions:
            if len(self.grid[position[0]][position[1]]) == 0:
                self.all_entities[entities.Plant].append(entities.Plant(position, self.T_plant))
                break
        if len(self.plant_entities) > self.grid_size[0] * self.grid_size[1] * 0.9:
            self.notify_observers("number of plants exceeds 90% of the grid space.")

    def reproduce(self):
        reproduction_count = 0
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
                        reproduction_count += 1
                        break
        return reproduction_count

    def trampled_by(self):
        for plant in self.plant_entities:
            pred = next(
                (ent for ent in self.grid[plant.position[0]][plant.position[1]] if isinstance(ent, entities.Predator)),
                None)
            if pred is not None:
                self.plant_entities.remove(plant)

    def log_reproduction_count(self, num_reproductions):
        self.reproduction_count.append(num_reproductions)

    def plot_entity_count(self):
        plt.figure(figsize=(10, 6))
        entity_classes = self.entity_count[0].keys()
        for entity_class in entity_classes:
            count = [step_dict.get(entity_class, 0) for step_dict in self.entity_count]
            plt.plot(count, label=entity_class.__name__)
        plt.tight_layout()
        plt.legend(loc='upper right')
        plt.xlabel('Simulation Steps', fontsize=12)
        plt.title('Population over time', fontsize=10)
        output_dir = "plots"
        plt.savefig(os.path.join(output_dir, "population.png"), dpi=300)

        plt.show()

    def plot_reproduction_count(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.reproduction_count)
        plt.tight_layout()
        plt.xlabel('Simulation Steps', fontsize=12)
        plt.title('reproduction over time', fontsize=10)
        output_dir = "plots"
        plt.savefig(os.path.join(output_dir, "reproduction.png"), dpi=300)

        plt.show()

    def plot_consumption_count(self):
        plt.figure(figsize=(10, 6))
        entity_classes = self.consumption_count.keys()
        for entity_class in entity_classes:
            count = self.consumption_count[entity_class]
            plt.plot(count, label=entity_class.__name__)
        plt.tight_layout()
        plt.legend(loc='upper right')
        plt.xlabel('Simulation steps', fontsize=12)
        output_dir = "plots"
        plt.savefig(os.path.join(output_dir, "consumption.png"), dpi=300)

        plt.show()

    def plot_grid_heatmap(self):
        heatmap_data = np.zeros(self.grid_size)
        for grid in self.grid_history:
            for i in range(self.grid_size[0]):
                for j in range(self.grid_size[1]):
                    heatmap_data[i][j] += grid[i][j]
        plt.figure(figsize=(8, 6))
        plt.imshow(heatmap_data, cmap='hot', origin='lower', interpolation='nearest')
        plt.colorbar(label='Traffic')
        plt.title('Grid traffic', fontsize=10)
        output_dir = "plots"
        plt.savefig(os.path.join(output_dir, "traffic_heat.png"), dpi=300)
        plt.show()


def run_simulation():
    simulator = seed_loader()

    alert_system = SimulationAlertSystem()
    simulator.add_observer(alert_system)

    simulator.place_entities()
    simulator.print_grid()
    for i in range(simulator.steps):
        print("step ", i)

        simulator.move_entities(entities.Predator)
        simulator.move_entities(entities.Herbivore)
        simulator.move_entities(entities.Omnivore)
        num_reproductions = simulator.reproduce()
        simulator.trampled_by()

        simulator.tick_entity(entities.Predator)
        simulator.tick_entity(entities.Herbivore)
        simulator.tick_entity(entities.Omnivore)
        simulator.tick_entity(entities.Plant)

        simulator.plant_random()

        simulator.clear_grid()

        simulator.place_entities()

        simulator.print_grid()

        simulator.log_entity_count()
        simulator.log_reproduction_count(num_reproductions)

    simulator.plot_entity_count()
    simulator.plot_reproduction_count()
    simulator.plot_consumption_count()
    simulator.plot_grid_heatmap()


def seed_loader():
    with open(f'config.yaml', 'r') as config:
        output = yaml.safe_load(config)
    simulator = Simulation([int(x) for x in output.get('grid_size', [1, 1])],
                           int(output.get('steps', 1)),
                           int(output.get('T_plant', 1)),
                           int(output.get('T_herbivore', 1)),
                           int(output.get('R_herbivore', 1)),
                           int(output.get('T_cooldown', 1)),
                           int(output.get('T_predator', 1)),
                           int(output.get('R_predator_sight', 2)),
                           int(output.get('T_omnivore', 1)),
                           int(output.get('R_omnivore_sight', 1)))
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
    logging.basicConfig(filename='simulation.log', level=logging.INFO)
    logger.info('Started')
    run_simulation()
    logger.info('Finished')
