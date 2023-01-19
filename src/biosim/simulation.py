# -*- coding: utf-8 -*-

from utils.functions import create_island
from vizualisation.graphics import Graphics
from datetime import datetime
import numpy as np
import random
import csv

__author__ = 'Sindre Elias Hinderaker', 'Mathias Kristiansen'
__email__ = 'sindre.elias.hinderaker@nmbu.no' 'mathias.kristiansen0@nmbu.no'

"""
BioSim class based on template from:
https://gitlab.com/nmbu.no/emner/inf200/h2021/inf200-course-materials/-/blob/main/january_block/biosim_template/src/biosim/simulation.py
"""

# The initial class structure in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2021 Hans Ekkehard Plesser / NMBU


class BioSim:
    """Define and perform a simulation."""

    def __init__(self, island_map, ini_pop, seed,
                 vis_years=1, ymax_animals=None, cmax_animals=None, hist_specs=None,
                 img_dir=None, img_base=None, img_fmt='png', img_years=None,
                 log_file=None):

        """
        :param island_map: Multi-line string specifying island geography
        :param ini_pop: List of dictionaries specifying initial population
        :param seed: Integer used as random number seed
        :param ymax_animals: Number specifying y-axis limit for graph showing animal numbers
        :param cmax_animals: Dict specifying color-code limits for animal densities
        :param hist_specs: Specifications for histograms, see below
        :param vis_years: years between visualization updates (if 0, disable graphics)
        :param img_dir: String with path to directory for figures
        :param img_base: String with beginning of file name for figures
        :param img_fmt: String with file type for figures, e.g. 'png'
        :param img_years: years between visualizations saved to file (default: vis_years)
        :param log_file: If given, write animal counts to this file

        .. note::
            If img_dir is None, no figures are written to file. Filenames are formed as:
            f'{os.path.join(img_dir, img_base)}_{img_number:05d}.{img_fmt}'\n
            where img_number are consecutive image numbers starting from 0.\n
            img_dir and img_base must either be both None or both strings.
        """
        random.seed(seed)
        self.ini_pop = ini_pop
        self.island_map = island_map
        self.island = create_island(island_map=self.island_map)
        self.add_population(population=self.ini_pop)

        # Graphics
        self.ymax_animals = ymax_animals
        self.cmax_animals = cmax_animals
        self.vis_years = vis_years
        self.img_years = img_years
        if self.img_years is None:
            self.img_years = self.vis_years
        # Disable graphics when vis_years is 0
        if self.vis_years != 0:
            self._graphics = Graphics(img_base=img_base, img_dir=img_dir, img_fmt=img_fmt,
                                      hist_specs=hist_specs, geogr=self.island_map)

        self.current_year = 0
        self._final_step = None

        # Log file
        self.log_file = log_file
        if self.log_file is not None:
            creation_time = datetime.now()
            with open(f'{self.log_file}.csv', 'w', newline='') as file:
                self.writer = csv.writer(file)
                self.writer.writerow(["This file contains animal counts from the BioSim package"])
                self.writer.writerow([f"Created: {creation_time}"])
                self.writer.writerow(["Year", "Herbivores", "Carnivores", "Total animals"])

    def set_animal_parameters(self, species, params):
        """
        Set parameters for animal species.\n

        :param species: String, name of animal species\n
        :param params: Dict with valid parameter specification for species
        """
        for coord, geography in self.island.items():
            if geography.movable and species == 'Herbivore':
                for herbivore in geography.herbivores:
                    herbivore.set_animal_params(params)
            elif geography.movable and species == 'Carnivore':
                for carnivore in geography.carnivores:
                    carnivore.set_animal_params(params)

    def set_landscape_parameters(self, landscape, params):
        """
        Set parameters for landscape type.

        :param landscape: String, code letter for landscape
        :param params: Dict with valid parameter specification for landscape
        """
        for coord, geography in self.island.items():
            if landscape == 'L':
                geography.f_max = params['f_max']
            elif landscape == 'H':
                geography.f_max = params['f_max']
            else:
                raise ValueError('Unknown or unsupported landscape type')

    def simulate(self, num_years):
        """
        Run simulation while visualizing the result.\n

        :param num_years: number of years to simulate
        """

        for year in range(num_years):
            self.current_year += 1
            # Lists for storing yearly data for visualization
            herb_pop = []
            carn_pop = []
            herb_weights = []
            carn_weights = []
            herb_fitness = []
            carn_fitness = []
            herb_age = []
            carn_age = []

            # Write to log file
            if self.log_file is not None:
                herb_count, carn_count = self.num_animals_per_species.values()
                with open(f'{self.log_file}.csv', 'a', newline='') as file:
                    self.writer = csv.writer(file)
                    self.writer.writerow([f"{self.current_year}", f"{herb_count}",
                                          f"{carn_count}", f"{self.num_animals}"])
                    # without use of num_animals property
                    # self.writer.writerow([f"{self.current_year}", f"{herb_count}",
                    #                      f"{carn_count}", f"{herb_count+carn_count}"])

            for coordinate, geography in self.island.items():

                try:
                    herb_pop.append(len(geography.herbivores))
                    carn_pop.append(len(geography.carnivores))
                except TypeError:
                    # for water coordinates
                    herb_pop.append(0)
                    carn_pop.append(0)

                if geography.movable:
                    # Adds the weights of all animals in a list
                    herb_w, carn_w = geography.get_weight_lists
                    herb_weights.extend(herb_w)
                    carn_weights.extend(carn_w)
                    # Adds the fitness of all animals in a list
                    herb_f, carn_f = geography.get_fitness_lists
                    herb_fitness.extend(herb_f)
                    carn_fitness.extend(carn_f)
                    # Adds the age of all animals in a list
                    herb_a, carn_a = geography.get_age_lists
                    herb_age.extend(herb_a)
                    carn_age.extend(carn_a)

                    # 1 --- Regrowth and feeding
                    geography.grow_fodder()
                    # Herbivores eat
                    geography.sort_herbivores_by_fitness()
                    for herbivore in geography.herbivores:
                        eaten_fodder = herbivore.feed(geography.fodder)
                        # fodder eaten by herbivore removed from available fodder
                        geography.fodder_eaten(eaten_fodder)

                    # Carnivores eat
                    # Shuffles the list of carnivores to get a random eating order
                    geography.random_carnivore_order()
                    for carnivore in geography.carnivores:
                        eaten_herbivores_list = carnivore.hunt(geography.herbivores)
                        # Herbivores eaten by carnivores removed from available fodder:
                        geography.herbivores_eaten(eaten_herbivores_list)

                    # 2 --- Procreation
                    geography.procreation()

                    # 3 --- Migration loop/stage
                    geography.animal_migration(island=self.island, current_coordinate=coordinate)

            # # Merge migrated_list into regular list
            for coordinate, geography in self.island.items():
                if geography.movable:
                    geography.migration_finished()

                    # 4/5 --- Aging / weight loss
                    geography.animal_aging()

                    # 6 --- Death
                    geography.animal_death()

            # End of year
            # Graphics stuff
            # Converts list to 1D numpy arrays
            herb_pop_ar = np.array(herb_pop)
            carn_pop_ar = np.array(carn_pop)
            # Reshape arrays to 2D arrays according to island map dimensions
            herb_pop_ar = herb_pop_ar.reshape(max(list(self.island.keys())))
            carn_pop_ar = carn_pop_ar.reshape(max(list(self.island.keys())))

            # Disable graphics when vis_years is 0
            if self.vis_years != 0:
                if self.img_years % self.vis_years != 0:
                    raise ValueError('img_steps must be multiple of vis_steps')

                self._final_step = self.current_year + num_years
                self._graphics.setup(self._final_step, self.img_years,
                                     self.ymax_animals, self.cmax_animals)

                # Update graphics with correct frequency
                if self.current_year % self.vis_years == 0:
                    self._graphics.update(self.current_year, herb_pop_ar, carn_pop_ar,
                                          np.sum(herb_pop_ar), np.sum(carn_pop_ar),
                                          max(list(self.island.keys())),
                                          (herb_weights, carn_weights),
                                          (herb_fitness, carn_fitness),
                                          (herb_age, carn_age))

    def add_population(self, population):
        """
        Add a population to the island\n

        :param population: List of dictionaries specifying population
        """
        for element in population:
            # print('Element loc: ', self.island[element['loc']])
            # #print('Element pop: ', element['pop'])
            geography = self.island[element['loc']]  # locates geography to place animal
            geography.insert_population(element['pop'])

    @property
    def year(self):
        """Last year simulated."""
        return self.current_year

    @property
    def num_animals(self):
        """Total number of animals on island."""
        num_animals = 0
        for coordinate, geography in self.island.items():
            if geography.movable:
                num_animals += len(geography.herbivores) + len(geography.carnivores)
        return num_animals

    @property
    def num_animals_per_species(self):
        animals_per_species = {'Herbivore': 0, 'Carnivore': 0}
        for coordinate, geography in self.island.items():
            if geography.movable:
                animals_per_species['Herbivore'] += len(geography.herbivores)
                animals_per_species['Carnivore'] += len(geography.carnivores)
        return animals_per_species

    def make_movie(self, movie_fmt=None):
        """Create MPEG4 movie from visualization images saved."""
        self._graphics.make_movie(movie_fmt)
