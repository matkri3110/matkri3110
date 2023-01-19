# -*- coding: utf-8 -*-

import random
import itertools
from biosim.animal_class import Herbivore, Carnivore

__author__ = 'Sindre Elias Hinderaker', 'Mathias Kristiansen'
__email__ = 'sindre.elias.hinderaker@nmbu.no' 'mathias.kristiansen0@nmbu.no'

"""
This script contains a super-class: Geography,
and associated sub-classes: Lowland, Highland, Desert and Water.
"""


# noinspection PyPep8Naming
class Geography:
    """
    Super class containing default attributes and methods for its subclasses:

    Lowland, Highland, Desert and Water.
    """
    def __init__(self):
        self.movable = True
        self.fodder = 0
        self.herbivores = []
        self.carnivores = []
        self.migrated_herbivores = []
        self.migrated_carnivores = []

    @property
    def get_weight_lists(self):
        """
        Creates 2 lists containing the weight of all herbivores and carnivores

        :return herbivore_weights, carnivore_weight: list
        """
        herbivore_weights = [herbivore.weight for herbivore in self.herbivores]
        carnivore_weights = [carnivore.weight for carnivore in self.carnivores]
        return herbivore_weights, carnivore_weights

    @property
    def get_fitness_lists(self):
        """
        Creates 2 lists containing the fitness of all herbivores and carnivores

        :return herbivore_fitness, carnivore_fitness: list
        """
        herbivore_fitness = [herbivore.fitness for herbivore in self.herbivores]
        carnivore_fitness = [carnivore.fitness for carnivore in self.carnivores]
        return herbivore_fitness, carnivore_fitness

    @property
    def get_age_lists(self):
        """
        Creates 2 lists containing the age of all herbivores and carnivores

        :return herbivore_ages, carnivore_age: list
        """
        herbivore_age = [herbivore.age for herbivore in self.herbivores]
        carnivore_age = [carnivore.age for carnivore in self.carnivores]
        return herbivore_age, carnivore_age

    def insert_population(self, animals):
        """
        Method for inserting population on the island.

        :param animals: list, list of objects with simple descriptions
                        of desired herbivores or carnivores

        Example of list: [{'species': 'Carnivore','age': 5, 'weight': 20}, ...]
        """

        for _animal in animals:
            try:
                if _animal['species'] == 'Herbivore':
                    self.herbivores.append(Herbivore(_animal['age'], _animal['weight']))
                elif _animal['species'] == 'Carnivore':
                    self.carnivores.append(Carnivore(_animal['age'], _animal['weight']))
            except AttributeError:
                raise AttributeError('Animals cannot be placed on this geography type, '
                                     'or unknown species')

    def sort_herbivores_by_fitness(self):
        """Sorts herbivores list by fitness: high - low"""

        self.herbivores.sort(key=lambda herbivore: herbivore.fitness, reverse=True)

    def random_carnivore_order(self):
        """Shuffles the carnivores list in random order"""

        random.shuffle(self.carnivores)

    def fodder_eaten(self, fodder_need):
        """
        Fodder eaten by herbivore removed from geography

        :param fodder_need: int
        """

        if self.fodder - fodder_need < 0:
            self.fodder = 0
        else:
            self.fodder -= fodder_need

    def herbivores_eaten(self, dead_herbivores):
        """
        Herbivores eaten by carnivores removed from geography

        :param dead_herbivores: int
        """
        for dead_herbivore in dead_herbivores:
            self.herbivores.remove(dead_herbivore)

    def procreation(self):
        """Initializing procreation of both species """

        # Herbivores
        filtered_herbivores = list(filter(lambda _herbivore: (_herbivore.age != 0),
                                          self.herbivores))
        N_h = len(filtered_herbivores)
        for _herbivore in filtered_herbivores:
            baby_herbivore = _herbivore.gives_birth(N_h)
            if baby_herbivore:
                self.herbivores.append(baby_herbivore)

        # Carnivores
        filtered_carnivores = list(filter(lambda _carnivore: (_carnivore.age != 0),
                                          self.carnivores))
        N_c = len(filtered_carnivores)
        for _carnivore in filtered_carnivores:
            baby_carnivore = _carnivore.gives_birth(N_c)
            if baby_carnivore:
                self.carnivores.append(baby_carnivore)

    def animal_migration(self, island, current_coordinate):
        """
        Migration of animals from geography

        :param island: dict
        :param current_coordinate: tuple
        """
        x, y = current_coordinate  # tuple unpacking of x and y coordinates
        _animals = self.herbivores.copy() + self.carnivores.copy()

        for _animal in _animals:  # Iteration over the copied list wil ensure no animal is skipped
            # random choice form adjacent coordinates:
            new_coordinate = random.choice([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])

            if island[new_coordinate].movable and _animal.migration_prob() > random.random():

                if _animal in self.herbivores:
                    island[new_coordinate].migrated_herbivores.append(_animal)
                    self.herbivores.remove(_animal)
                elif _animal in self.carnivores:
                    island[new_coordinate].migrated_carnivores.append(_animal)
                    self.carnivores.remove(_animal)

    def migration_finished(self):
        """Merges migration list into regular list of animals"""

        # Herbivores
        self.herbivores.extend(self.migrated_herbivores)
        self.migrated_herbivores.clear()
        # Carnivores
        self.carnivores.extend(self.migrated_carnivores)
        self.migrated_carnivores.clear()

    def animal_aging(self):
        """Initialize yearly animal death"""

        for animal in itertools.chain(self.herbivores, self.carnivores):
            animal.update_age()

    def animal_death(self):
        """Initialize yearly animal death"""

        dead_animals = [_animal for _animal in itertools.chain(self.herbivores, self.carnivores)
                        if _animal.dies()]

        for _dead_animal in dead_animals:
            if _dead_animal in self.herbivores:
                self.herbivores.remove(_dead_animal)
            elif _dead_animal in self.carnivores:
                self.carnivores.remove(_dead_animal)


class Lowland(Geography):
    """
    Lowland is a subclass of Geography with specific fodder-attribute and method.
    """
    geography = 'Lowland'

    def __init__(self):
        super().__init__()
        self.f_max = 800

    def grow_fodder(self):
        self.fodder = self.f_max


class Highland(Geography):
    """
    Highland is a subclass of Geography with specific fodder-attribute and method.
    """
    geography = 'Highland'

    def __init__(self):
        super().__init__()
        self.f_max = 500

    def grow_fodder(self):
        self.fodder = self.f_max


class Desert(Geography):
    """
    Desert is a subclass of Geography, no fodder is available here.
    """
    geography = 'Desert'

    def grow_fodder(self):
        """No fodder is grown in desert"""
        pass


class Water(Geography):
    """Water is a subclass of Geography, it is not possible for animals to be here."""
    def __init__(self):
        super().__init__()
        self.geography = 'Water'
        self.movable = False
        self.fodder = None
        self.herbivores = None
        self.carnivores = None
        self.migrated_herbivores = None
        self.migrated_carnivores = None
