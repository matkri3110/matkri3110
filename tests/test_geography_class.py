# -*- coding: utf-8 -*-

from biosim.geography_class import Lowland, Highland, Desert, Water
from math import e
import random
import pytest

__author__ = 'Sindre Elias Hinderaker', 'Mathias Kristiansen'
__email__ = 'sindre.elias.hinderaker@nmbu.no' 'mathias.kristiansen0@nmbu.no'

"""
Tests that checks attributes and methods of the Geography class and its sub-classes.
"""


class TestGeographyClass:

    @pytest.fixture(autouse=True)
    def create_geography(self):
        """
        Creates a dictionary containing all geography types,
        to make them easily available for parametrize testing
        """

        self.geo = {
            'L': Lowland(),
            'H': Highland(),
            'D': Desert(),
            'W': Water(),
        }

    @pytest.fixture
    def grow_fodder(self):
        """Setup to grow fodder for relevant geography types before testing"""
        for key, value in self.geo.items():
            if key != 'W':
                value.grow_fodder()
        yield
        # do nothing after test

    @pytest.fixture
    def create_herbivores(self):
        """Setup to create a list of herbivores for relevant geography types before testing"""

        self.ini_herbs = [{'species': 'Herbivore', 'age': 40, 'weight': 50}
                          for _ in range(10)]
        yield
        # do nothing after test

    @pytest.fixture
    def create_animals(self):
        """Setup to create a list of herbivores for relevant geography types before testing"""

        self.ini_herbivores = [{'species': 'Herbivore', 'age': 40, 'weight': 50}
                               for _ in range(10)]
        self.ini_carnivores = [{'species': 'Carnivore', 'age': 40, 'weight': 50}
                               for _ in range(20)]
        self.ini_animals = self.ini_herbivores + self.ini_carnivores
        yield
        # do nothing after test

    @pytest.mark.parametrize('key', ['L', 'H', 'D', 'W'])
    def test_insert_population(self, key, create_animals):
        """
        Checks that the insert_population method works as expected for geography subclasses.
        A population should be inserted in a dictionary form and sorted in lists by species.

        :param key:
        :param create_animals: pytest.fixture()
        """
        exp_nr_herbs = 10
        exp_nr_carn = 20
        if key == 'W':
            with pytest.raises(AttributeError):
                # 'NoneType' object has no attribute 'append'
                self.geo[key].insert_population(self.ini_animals)
        else:
            self.geo[key].insert_population(self.ini_animals)
            nr_herbs = len(self.geo[key].herbivores)
            nr_carns = len(self.geo[key].carnivores)
            assert nr_herbs == exp_nr_herbs and nr_carns == exp_nr_carn

    @pytest.mark.parametrize('key, expected_fodder', [('L', 800),
                                                      ('H', 500),
                                                      ('D', 0),
                                                      ('W', None)])
    def test_grow_fodder(self, key, expected_fodder):
        """
        Checks that the grow_fodder method works as expected for geography subclasses.
        Fodder should be set to default value for specific subclass.

        :param key: str
        :param expected_fodder: int
        """
        if key != 'W':
            self.geo[key].fodder = 0  # manually manipulates fodder attribute
            self.geo[key].grow_fodder()   # set fodder to expected amount for geography type

        assert self.geo[key].fodder == expected_fodder

    @pytest.mark.parametrize('key', ['L', 'H', 'D'])
    def test_sort_by_fitness(self, key):
        """
        Checks that the sort_herbivores_by_fitness method works as expected for geography subclasses
        Should sort the herbivore list by descending fitness.

        :param key: str
        """
        # creates a herbivore population with varying fitness
        # (due to age and weight differences)
        ini_herbs = [{'species': 'Herbivore', 'age': 5+i, 'weight': 10+i}
                     for i in range(10)]

        self.geo[key].insert_population(ini_herbs)
        random.shuffle(self.geo[key].herbivores)   # ensures random order of herbivores
        self.geo[key].sort_herbivores_by_fitness()
        first_herb = self.geo[key].herbivores[0].fitness
        second_herb = self.geo[key].herbivores[1].fitness
        third_herb = self.geo[key].herbivores[2].fitness
        assert first_herb > second_herb > third_herb

    @pytest.mark.parametrize('key', ['L', 'H', 'D'])
    def test_random_carnivore_order(self, key, create_animals):
        """
        Checks that the random_carnivore_order method works as expected for geography subclasses.
        Carnivores should be shuffled in random order.

        :param key:
        :param create_animals:
        """
        self.geo[key].insert_population(self.ini_animals)
        ini_carnivore_order = self.geo[key].carnivores.copy()  # copy of carnivores order
        self.geo[key].random_carnivore_order()
        assert self.geo[key].carnivores != ini_carnivore_order

    @pytest.mark.parametrize('key, eaten_fodder', [('L', 810), ('H', 510), ('D', 10)])
    def test_fodder_eaten_not_negative(self, key, eaten_fodder, grow_fodder):
        """
        Checks that the fodder_eaten method works as expected for geography subclasses.
        Tests that fodder is not negative if herbivores tries to eat more than available.

        :param key:  str
        :param eaten_fodder: int
        """
        self.geo[key].fodder_eaten(eaten_fodder)
        assert self.geo[key].fodder == 0

    @pytest.mark.parametrize('key, eaten_fodder, remaining', [('L', 50, 750),
                                                              ('H', 10, 490),
                                                              ('D', 10, 0)])
    def test_fodder_eaten_reduction(self, key, eaten_fodder, remaining, grow_fodder):
        """
        Checks that the fodder_eaten method works as expected for geography subclasses.
        Tests that fodder is removed by the correct amount.

        :param key:  str
        :param eaten_fodder: int
        """
        self.geo[key].fodder_eaten(eaten_fodder)
        assert self.geo[key].fodder == remaining

    @pytest.mark.parametrize('key, eaten_herbs, pred_remaining', [('L', 5, 5),
                                                                  ('H', 1, 9),
                                                                  ('D', 10, 0)])
    def test_herbivores_eaten(self, key, eaten_herbs, pred_remaining, create_animals):
        """
        Checks that the herbivores_eaten method works as expected for geography subclasses.
        Tests that the correct herbivores are removed.

        :param key:  str
        :param eaten_herbs: int
        :param pred_remaining: int
        :param create_animals: pytest.fixture()
        """
        self.geo[key].insert_population(self.ini_animals)  # initially 10 herbivores
        eaten_herbs = self.geo[key].herbivores[:eaten_herbs]
        self.geo[key].herbivores_eaten(eaten_herbs)
        actual_remaining = len(self.geo[key].herbivores)
        assert eaten_herbs not in self.geo[key].herbivores \
               and actual_remaining == pred_remaining

    @pytest.mark.parametrize('key', ['L', 'H', 'D'])
    def test_procreation_no_birth(self, key, mocker):
        """
        Checks that the procreation method works as expected for geography subclasses.
        Tests that no animals are born when conditions are not met,
        due to animals attribute values.

        :param key: str
        :param mocker: patch
        """
        # fitness = (1 / (1 + e ** (phi_age * (age - a_half)))) *
        # (1 / (1 + e ** (-phi_weight * (weight - w_half))))
        # Requirement to give birth:
        # if min(1, gamma * fitness*(N - 1)) > random.random() and
        # weight >= zeta * (w_birth + sigma_birth):

        # creates a herbivore population of 10, with equal fitness:
        ini_herbs = [{'species': 'Herbivore', 'age': 40, 'weight': 10}
                     for _ in range(10)]
        # the population created has age equal to a_half, and weight equal w_half
        # the fitness of the animal will then be 1/4 (1/2*1/2), according to formulae.
        self.geo[key].insert_population(ini_herbs)
        # birth probability = min(1, gamma * fitness * (N - 1))
        # => 0.2 * 0.25 * (10 - 1) = 0.45
        # ensures the random value in the gives_birth method is higher
        # than the birth probability
        mocker.patch('random.random', return_value=1)
        # weight >= zeta * (w_birth + sigma_birth) = 10 >= 3.5 * (10 + 1.5)
        # => 10 >= 40.25
        # since both terms in if statement evaluates to false:
        # 0.45 > 1 and 10 >= 40.25
        # no herbivores shall be born, thus the length of the list with initial herbivores
        # and the list after procreation should be equal
        self.geo[key].procreation()
        assert len(self.geo[key].herbivores) == len(ini_herbs)

    @pytest.mark.parametrize('key', ['L', 'H', 'D'])
    def test_procreation_with_birth(self, key, mocker, create_animals):
        """
        Checks that the procreation method works as expected for
        carnivores. Tests that animals are born when conditions are met.

        :param key: str
        :param mocker: patch
        :param create_herbivores(): pytest.fixture()
        """
        # fitness = (1 / (1 + e ** (phi_age * (age - a_half)))) *
        # (1 / (1 + e ** (-phi_weight * (weight - w_half))))
        # herbivore fittness: (1 / 2 * (1 / (1 + e ** (-0.1 * (50 - 10))))) = 0.491
        # carnivore fittness: (1 / 2 * (1 / (1 + e ** (-0.4 * (50 - 4.0))))) = 0.499
        self.geo[key].insert_population(self.ini_animals)
        ini_herbs = self.geo[key].herbivores.copy()
        ini_carns = self.geo[key].carnivores.copy()
        # birth probability herbivore = min(1, gamma * fitness * (N - 1))
        # => 0.2 * 0.491 * (10 - 1) = min(1, 0.883)
        # birth probability varnivore = min(1, gamma * fitness * (N - 1))
        # => 0.8 * 0.499 * (20 - 1) = min(1, 7.58)
        # ensures the random value in the gives_birth method is higher than the birth probability
        mocker.patch('random.random', return_value=0.4)
        # herbivore: weight >= zeta * (w_birth + sigma_birth) = 50 >= 3.5 * (10 + 1.5)
        # => 50 >= 40.25
        # carnivore: weight >= zeta * (w_birth + sigma_birth) = 50 >= 3.5 * (6.0 + 1)
        # => 50 >= 24.5
        # both terms in if statement evaluates to true
        # now a babies will be born if birth-weight is lower or equal to weight of 'mother'.
        mocker.patch('random.gauss', return_value=10)  # mother weight: 50 baby weight: 10
        self.geo[key].procreation()
        # all animals in list should give birth, thus:
        assert len(self.geo[key].herbivores) == len(ini_herbs)*2 \
               and len(self.geo[key].carnivores) == len(ini_carns)*2

    @pytest.mark.parametrize('key_1, key_2', [('L', 'H'), ('D', 'H')])
    def test_animal_migration(self, key_1, key_2, mocker, create_animals):
        """
        Checks that the migration method works as expected for geography subclasses.
        Tests that animals are migrated correctly when conditions are met.

        :param key_1: str
        :param key_2: str
        :param mocker: patch
        :param create_animals: pytest.fixture()
        """
        self.geo[key_1].insert_population(self.ini_animals)
        ini_herbs = self.geo[key_1].herbivores.copy()
        ini_carns = self.geo[key_1].carnivores.copy()
        # Creates simple island dictionary
        island = {
            (1, 1): self.geo[key_1],
            (1, 2): self.geo[key_2]
        }
        # ensures the other random coordinate is selected
        mocker.patch('random.choice', return_value=(1, 2))
        # ensures migration will happen for movable geographies
        mocker.patch('random.random', return_value=0)
        self.geo[key_1].animal_migration(island, current_coordinate=(1, 1))
        migrated_herbs = self.geo[key_2].migrated_herbivores
        migrated_carns = self.geo[key_2].migrated_carnivores
        assert ini_herbs == migrated_herbs and ini_carns == migrated_carns

    @pytest.mark.parametrize('key_1, key_2', [('L', 'W'), ('H', 'W'), ('D', 'W')])
    def test_animal_migration_non_movable(self, key_1, key_2, mocker, create_animals):
        """
        Checks that the migration method works as expected for geography subclasses.
        Tests that animals are not migrated when conditions are not met.

        :param key_1: str
        :param key_2: str
        :param mocker: patch
        :param create_animals: pytest.fixture()
        """
        self.geo[key_1].insert_population(self.ini_animals)
        ini_herbs = self.geo[key_1].herbivores.copy()
        ini_carns = self.geo[key_1].carnivores.copy()
        # Simple island dictionary
        island = {
            (1, 1): self.geo[key_1],
            (1, 2): self.geo[key_2]
        }
        # ensures the other random coordinate is selected
        mocker.patch('random.choice', return_value=(1, 2))
        # ensures migration will happen for movable geographies
        mocker.patch('random.random', return_value=0)
        self.geo[key_1].animal_migration(island, current_coordinate=(1, 1))
        migrated_herbs = self.geo[key_2].migrated_herbivores
        migrated_carns = self.geo[key_2].migrated_carnivores
        # No animals should migrate to water coordinates despite sufficient migration probability
        assert ini_herbs == self.geo[key_1].herbivores \
               and ini_carns == self.geo[key_1].carnivores \
               and migrated_herbs is None \
               and migrated_carns is None

    @pytest.mark.parametrize('key', ['L', 'H', 'D'])
    def test_migration_finished(self, key, create_animals):
        """
        Checks that the migration_finished method works as expected for geography subclasses.
        Tests that the lists of animal species are merged with migration-list and cleared after.

        :param key: str
        :param create_animals: pytest.fixture()
        """
        self.geo[key].insert_population(self.ini_animals)
        ini_herbs = self.geo[key].herbivores.copy()
        ini_carns = self.geo[key].carnivores.copy()
        some_herbs = self.geo[key].herbivores[:5]
        some_carns = self.geo[key].carnivores[:10]
        self.geo[key].migrated_herbivores = some_herbs.copy()
        self.geo[key].migrated_carnivores = some_carns.copy()
        self.geo[key].migration_finished()
        assert self.geo[key].herbivores == ini_herbs + some_herbs \
               and self.geo[key].carnivores == ini_carns + some_carns \
               and len(self.geo[key].migrated_herbivores) == 0 \
               and len(self.geo[key].migrated_carnivores) == 0

    @pytest.mark.parametrize('key', ['L', 'H', 'D'])
    def test_animal_aging_increased(self, key, create_animals):
        """
        Checks that the animal aging method works as expected for geography subclasses.
        Tests that all animals are aged.

        :param key: str
        :param create_animals: pytest.fixture()
        """
        self.geo[key].insert_population(self.ini_animals)
        age_before_herb = self.geo[key].herbivores[0].age
        age_before_carn = self.geo[key].carnivores[0].age
        self.geo[key].animal_aging()
        assert age_before_herb not in self.geo[key].herbivores \
               and age_before_carn not in self.geo[key].carnivores

    @pytest.mark.parametrize('key, years', [('L', 1), ('H', 10), ('D', 15)])
    def test_animal_aging_exp_age(self, key, years, create_animals):
        """
        Checks that the animal aging method works as expected for geography subclasses.
        Tests that animals are aged by the correct number of years.

        :param key: str
        :param years: int
        :param create_animals: pytest.fixture()
        """
        self.geo[key].insert_population(self.ini_animals)
        exp_age_herb = self.geo[key].herbivores[0].age + years
        exp_age_carn = self.geo[key].carnivores[0].age + years
        for _ in range(years):
            self.geo[key].animal_aging()
        new_herb_age = self.geo[key].herbivores[0].age
        new_carn_age = self.geo[key].carnivores[0].age
        assert exp_age_herb == new_herb_age and exp_age_carn == new_carn_age

    @pytest.mark.parametrize('key', ['L', 'H', 'D'])
    def test_animal_death_all_dies(self, key, mocker, create_herbivores):
        """
        Checks that the animal_death method works as expected for geography
        subclasses. Tests that animals die when conditions are met.

        :param key: str
        :param mocker: patch
        :param create_herbivores: pytest.fixture()
        """
        # fitness = (1 / (1 + e ** (phi_age * (age - a_half)))) *
        # (1 / (1 + e ** (-phi_weight * (weight - w_half))))
        # fitness = (1/2 * (1 / (1 + e ** (-0.1 * (50 - 10)))) = 0.491

        self.geo[key].insert_population(self.ini_herbs)
        # fitness = (1 / (1 + e ** (phi_age * (age - a_half)))) *
        # (1 / (1 + e ** (-phi_weight * (weight - w_half))))
        # fitness = (1/2 * (1 / (1 + e ** (-0.1 * (50 - 10)))) = 0.491
        # death_prob = omega * (1 - fitness) = 0.4 * (1-0.491) = 0.2036
        # Death condition: if self.weight == 0 or death_prob > random.random()
        mocker.patch('random.random', return_value=0.15)
        self.geo[key].animal_death()
        # all animals in list should die, thus:
        assert len(self.geo[key].herbivores) == 0

    @pytest.mark.parametrize('key', ['L', 'H', 'D'])
    def test_animal_death_some_dies(self, key, mocker, create_herbivores):
        """
        Checks that the animal_death method works as expected for
        geography subclasses. Tests that some animals die when conditions
        are met, and other survive.

        :param key: str
        :param mocker: patch
        :param create_herbivores: pytest.fixture()
        """
        # fitness of herbivores: 0.491
        self.geo[key].insert_population(self.ini_herbs)
        ini_carns = [{'species': 'Carnivore', 'age': 40, 'weight': 0}
                     for _ in range(10)]
        self.geo[key].insert_population(ini_carns)
        # fitness = (1 / (1 + e ** (phi_age * (age - a_half)))) *
        # (1 / (1 + e ** (-phi_weight * (weight - w_half))))
        # fitness carnivores = (1/2 * (1 / (1 + e ** (-0.4 * (0 - 4.0)))) = 0.0839
        # death_prob herb = omega * (1 - fitness) = 0.4 * (1-0.491) = 0.2036
        # death_prob carn = omega * (1 - fitness) = 0.8 * (1-0.0839) = 0.7329
        # Death condition: if self.weight == 0 or death_prob > random.random()
        mocker.patch('random.random', return_value=0.75)
        self.geo[key].animal_death()
        # all carnivores should die as they have 0 weight, and no herbivores should, thus:
        assert len(self.geo[key].carnivores) == 0 \
               and len(self.geo[key].herbivores) == 10

    # Testing of properties

    @pytest.mark.parametrize('key', ['L', 'H', 'D'])
    def test_get_weight_lists(self, key, create_animals):
        """
        Checks that the get_weight_lists property works as expected for geography subclasses.
        Tests that the expected lists are provided.

        :param key: str
        :param create_animals: pytest.fixture()
        """
        self.geo[key].insert_population(self.ini_animals)
        herbivore_weights, carnivore_weights = self.geo[key].get_weight_lists
        herb_exp_weights = [50 for _ in range(len(self.geo[key].herbivores))]
        carn_exp_weights = [50 for _ in range(len(self.geo[key].carnivores))]
        assert herbivore_weights == herb_exp_weights \
               and carnivore_weights == carn_exp_weights

    @pytest.mark.parametrize('key', ['L', 'H', 'D'])
    def test_get_fitness_lists(self, key, create_animals):
        """
        Checks that the get_fitness_lists property works as expected
        for geography subclasses. Tests that the expected lists are provided.

        :param key: str
        :param create_animals: pytest.fixture()
        """
        self.geo[key].insert_population(self.ini_animals)
        herbivore_fitness, carnivore_fitness = self.geo[key].get_fitness_lists
        # fitness = (1 / (1 + e ** (phi_age * (age - a_half)))) *
        # (1 / (1 + e ** (-phi_weight * (weight - w_half))))
        herb_fit_calc = (1/2 * (1 / (1 + e ** (-0.1 * (50 - 10)))))
        carn_fit_calc = (1/2 * (1 / (1 + e ** (-0.4 * (50 - 4.0)))))
        herb_fitness = self.geo[key].herbivores[0].fitness
        carn_fitness = self.geo[key].carnivores[0].fitness
        herb_exp_fitness = [herb_fitness for _ in range(len(self.geo[key].herbivores))]
        carn_exp_fitness = [carn_fitness for _ in range(len(self.geo[key].carnivores))]
        assert herbivore_fitness == herb_exp_fitness \
               and carnivore_fitness == carn_exp_fitness \
               and herb_fitness == pytest.approx(herb_fit_calc) \
               and carn_fitness == pytest.approx(carn_fit_calc)

    @pytest.mark.parametrize('key', ['L', 'H', 'D'])
    def test_get_age_lists(self, key, create_animals):
        """
        Checks that the get_age_lists property works as expected for geography subclasses.
        Tests that the expected lists are provided.

        :param key: str
        :param create_animals: pytest.fixture()
        """
        self.geo[key].insert_population(self.ini_animals)
        herbivore_age, carnivore_age = self.geo[key].get_age_lists
        herb_exp_age = [40 for _ in range(len(self.geo[key].herbivores))]
        carn_exp_age = [40 for _ in range(len(self.geo[key].carnivores))]
        assert herbivore_age == herb_exp_age and carnivore_age == carn_exp_age
