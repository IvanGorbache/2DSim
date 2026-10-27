import logging
import random
import sys

import copy
import os

import numpy as np
import yaml

import entities
from const import *
import random
import logging
from abc import ABC, abstractmethod
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class Observer:
    def update(self, event_type: str, data: dict):
        pass


class SimulationObserver(Observer):
    def update(self, event_type: str, data: dict):
        if event_type == EXTINCT:
            entity_class = data['entity_class']
            msg = f"All entities of class {entity_class} have gone extinct."
            logger.warning(msg)
        elif event_type == CONSUMPTION:
            msg = f"A predator has consumed a herbivore"
            logger.warning(msg)
        elif event_type == OVERGROWN:
            msg = f"The number of plants exceeds 90% of the grid space."
            logger.warning(msg)


class Simulation:
    def __init__(self, grid_size, steps, plant_lifespan=10):
        self.observers = []
        self.extinct_notified = set()
        self.notified_overgrown = False

        self.grid_size = grid_size
        self.steps = steps
        self.plant_lifespan = plant_lifespan

        self.all_entities = {
            entities.Herbivore: [],
            entities.Predator: [],
            entities.Plant: [],
            entities.StaticEntity: [],
            entities.Omnivore: []
        }

        self.grid = [[[] for _ in range(self.grid_size[1])] for _ in range(self.grid_size[0])]

    def add_observer(self, observer: SimulationObserver):
        self.observers.append(observer)

    def notify_observers(self, event_type: str, data: dict):
        for observer in self.observers:
            observer.update(event_type, data)

    def add_entity(self, entity_instance):
        entity_class = type(entity_instance)
        self.all_entities.setdefault(entity_class, []).append(entity_instance)
        self.grid[entity_instance.position[0]][entity_instance.position[1]].append(entity_instance)
        for observer in self.observers:
            entity_instance.add_observer(observer)

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

    def simulate_entities(self, entity_type):
        for entity in self.all_entities[entity_type]:
            entity.simulate_step(self.grid, self.all_entities)

    def plant_random(self):
        empty_cells = []
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                if len(self.grid[i][j]) == 0:
                    empty_cells.append((i, j))

        if empty_cells:
            pos = random.choice(empty_cells)
            new_plant = entities.Plant(pos, self.plant_lifespan)
            self.add_entity(new_plant)

    def check_alerts(self):
        tracked_classes = [entities.Herbivore, entities.Predator, entities.Omnivore, entities.Plant]
        for entity_type in tracked_classes:
            if len(self.all_entities.get(entity_type, [])) == 0:
                if entity_type not in self.extinct_notified:
                    self.notify_observers(EXTINCT, {"entity_class": entity_type})
                    self.extinct_notified.add(entity_type)
            elif entity_type in self.extinct_notified:
                self.extinct_notified.remove(entity_type)

        if self.grid_size[0] * self.grid_size[1] * 0.9 < len(self.all_entities[entities.Plant]):
            if not self.notified_overgrown:
                self.notify_observers(OVERGROWN, {})
                self.notified_overgrown = True
        else:
            self.notified_overgrown = False

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
        print(f"step {i}")

        simulator.simulate_entities(entities.Predator)
        simulator.simulate_entities(entities.Herbivore)
        simulator.simulate_entities(entities.Omnivore)
        simulator.simulate_entities(entities.Plant)
        simulator.plant_random()

        simulator.print_grid()

        simulator.check_alerts()

        simulator.log_entity_count()
        simulator.log_reproduction_count(num_reproductions)

    simulator.plot_entity_count()
    simulator.plot_reproduction_count()
    simulator.plot_consumption_count()
    simulator.plot_grid_heatmap()


def seed_loader():
    with open(sys.argv[1], 'r') as config_file:
        output = yaml.safe_load(config_file)

    g_size = output.get('grid_size', [40, 40])
    if isinstance(g_size, dict):
        grid_size = [int(g_size.get('rows', 40)), int(g_size.get('cols', 40))]
    elif isinstance(g_size, (list, tuple)) and len(g_size) >= 2:
        grid_size = [int(g_size[0]), int(g_size[1])]
    else:
        grid_size = [40, 40]

    steps = output.get('simulation_steps', 30)

    entities_data = output.get('entities', {})
    plant_args = entities_data.get('Plant', {}).get('args', {})
    plant_lifespan = plant_args.get('lifespan', 10)

    simulator = Simulation(grid_size, steps, plant_lifespan)
    simulator.add_observer(SimulationObserver())

    ENTITY_MAP = {
        'Herbivore': {
            'cls': entities.Herbivore,
            'arg_map': lambda args: (args.get('lifespan'), args.get('sight_range'), args.get('reproduction_cooldown'))
        },
        'Predator': {
            'cls': entities.Predator,
            'arg_map': lambda args: (args.get('lifespan'), args.get('sight_range'))
        },
        'Plant': {
            'cls': entities.Plant,
            'arg_map': lambda args: (args.get('lifespan'),)
        },
        'StaticEntity': {
            'cls': entities.StaticEntity,
            'arg_map': lambda args: ()
        },
        'Omnivore': {
            'cls': entities.Omnivore,
            'arg_map': lambda args: (args.get('lifespan'), args.get('sight_range'))
        }
    }

    for entity_name, data in entities_data.items():
        if entity_name not in ENTITY_MAP:
            continue

        config_info = ENTITY_MAP[entity_name]
        entity_class = config_info['cls']
        raw_args = data.get('args', {}) if data else {}
        constructor_args = config_info['arg_map'](raw_args)

        for pos in (data.get('initial_positions', []) if data else []):
            position = tuple(pos)
            instance = entity_class(position, *constructor_args)
            simulator.add_entity(instance)

    return simulator


if __name__ == '__main__':
    logging.basicConfig(filename='simulation.log', level=logging.INFO)
    logger.info('Started')
    run_simulation()
    logger.info('Finished')
