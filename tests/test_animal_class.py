
from biosim.animal_class import Carnivore, Herbivore
from biosim.geography_class import Lowland
import random
from math import e

__author__ = 'Sindre Elias Hinderaker', 'Mathias Kristiansen'
__email__ = 'sindre.elias.hinderaker@nmbu.no' 'mathias.kristiansen0@nmbu.no'

"""
Tests that checks attributes and methods of the Animal class and its sub-classes.
"""


class TestAnimalClass:
    """Tests for Herbivore_sub-class"""

    def test_update_age(self):
        """
        Test that checks if age is updated by one each year cycle.\n
        :return:  function expects 6, anything else, returns false.\n
        """
        herbivore = Herbivore(age=5, weight=20)
        herbivore.update_age()
        assert herbivore.age == 5+1

    def test_weight_herbivore(self):
        """
        Test that checks if weight is equal to input\n
        :return
        """
        herbivore = Herbivore(age=5, weight=20)
        assert herbivore.weight == 20

    def test_weight_reduction(self):
        """
        Test that checks if baby_weight is equal to 10.\n
        :return:
        """
        herbivore = Herbivore(age=5, weight=20)
        baby_weight = 10
        herbivore.weight_reduction(baby_weight)
        assert herbivore.weight == 10

    def test_weight_reduction_update_fitness(self):
        """
        Test checks that baby_weight is removed from mother and fitness is updated.\n
        :return:
        """
        herbivore = Herbivore(age=5, weight=20)
        baby_weight = 10
        herbivore.weight_reduction(baby_weight)
        phi_age = 0.6
        a_half = 40.0
        phi_weight = 0.1
        w_half = 10.0
        fitness = (1 / (1 + e ** (phi_age * (herbivore.age - a_half)))) * (
                1 / (1 + e ** (- phi_weight * (herbivore.weight - w_half))))
        assert herbivore.fitness == fitness

    def test_feed_1(self):
        """
        Test that checks if the herbivore weight is updated when feeding. \n
        :return:
        """
        available_fodder = 10
        beta = 0.9
        # noinspection PyPep8Naming
        F = 10
        herbivore = Herbivore(age=5, weight=20)
        herbivore.feed(available_fodder)
        assert herbivore.weight == 20 + beta * F

    def test_feed_2(self):
        """
        Test that checks if the herbivore weight is updated when feeding on available fodder. \n
        :return:
        """
        available_fodder = 10
        beta = 0.9
        # noinspection PyPep8Naming
        herbivore = Herbivore(age=5, weight=20)
        herbivore.feed(available_fodder)
        assert herbivore.weight == 20 + beta * available_fodder

    def test_feed_3_update_fitness(self):
        """
        Test that checks that fitness is updated when a herbivore eats. \n
        :return:
        """
        available_fodder = 10
        # noinspection PyPep8Naming
        phi_age = 0.6
        a_half = 40.0
        phi_weight = 0.1
        w_half = 10.0
        herbivore = Herbivore(age=5, weight=20)
        herbivore.feed(available_fodder)
        fitness = (1/(1 + e**(phi_age*(herbivore.age - a_half)))) * \
                  (1/(1 + e**(- phi_weight*(herbivore.weight - w_half))))
        assert herbivore.fitness == fitness

    # Tests for Carnivore_sub-class

    def test_weight_carnivore(self):
        """
        Check that weight is equal to input\n
        :return:
        """
        carnivore = Carnivore(age=5, weight=20)
        assert carnivore.weight == 20

    def test_fitness_carnivore(self):
        """
        Checks that carnivore.fitness() is equal to fitness\n
        :return:
        """
        carnivore = Carnivore(age=5, weight=20)
        age = 5
        phi_age = 0.3
        a_half = 40.0
        phi_weight = 0.4
        weight = 20
        w_half = 4.0
        fitness = (1 / (1 + e ** (phi_age * (age - a_half)))) * \
                  (1 / (1 + e ** (- phi_weight * (weight - w_half))))
        assert carnivore.fitness == fitness

    def test_update_age_carnivore(self):
        """
        Checks that the carnivores can age properly.\n
        At the end of each year, they should grow one year older.\n
        :return:
        """
        carnivore = Carnivore(age=5, weight=20)
        carnivore.update_age()
        assert carnivore.age == 5+1

    def test_weight_reduction_carnivore(self):
        """
        Checks that the weight_reduction function works properly.\n
        Checks that the weight of the newborn baby is being subtracted
        from the mothers weight at point of birth
        """
        carnivore = Carnivore(age=5, weight=20)
        baby_weight = 10
        carnivore.weight_reduction(baby_weight)
        assert carnivore.weight == 10

    def test_weight_reduction_update_fitness_carnivore(self):
        """
        Test checks that the weight_reduction works. \n
        Also checks that fitness is updated after weight reduction.
        :return:
        """
        carnivore = Carnivore(age=5, weight=20)
        baby_weight = 10
        carnivore.weight_reduction(baby_weight)
        phi_age = 0.3
        a_half = 40.0
        phi_weight = 0.4
        w_half = 4.0
        fitness = (1 / (1 + e ** (phi_age * (carnivore.age - a_half)))) * (
                    1 / (1 + e ** (- phi_weight * (carnivore.weight - w_half))))
        assert carnivore.fitness == fitness

    def test_hunt_carnivore_fit(self):
        """
        Test for carnivore feeding/ hunt method with a fit carnivore.
        :return:
        """
        carnivore1 = Carnivore(1, 300)
        carnivore1.set_animal_params({'DeltaPhiMax': 1.00001})
        lowland1 = Lowland()
        lowland1.insert_population([{'species': 'Herbivore', 'age': 5, 'weight': 20}])
        lowland1.herbivores[0].fitness = 0

        boolean = carnivore1.hunt(lowland1.herbivores)

        carnivore1.set_animal_params({'DeltaPhiMax': 10.0})
        assert carnivore1.weight == 315 or boolean is False

    def test_hunt_carnivore_not_fit(self):
        """
        Test for carnivore hunt/feeding method, with a not fit carnivore. \n
        :return:
        """
        carnivore1 = Carnivore(1, 20)
        carnivore1.fitness = 0.0001
        carnivore1.set_animal_params({'DeltaPhiMax': 1.00001})
        lowland1 = Lowland()
        lowland1.insert_population([{'species': 'Herbivore', 'age': 5, 'weight': 20}])
        lowland1.herbivores[0].fitness = 1

        boolean = carnivore1.hunt(lowland1.herbivores)

        carnivore1.set_animal_params({'DeltaPhiMax': 10.0})
        assert carnivore1.weight == 20 or boolean is False

    def test_dies_herbivore(self, mocker):
        """
        Test checks that method for herbivore death works as expected.\n
        if weight == 0 or death_prob > random.random():
        :return: herbivore.dies() is True
            elif weight == 0 or death_prob =< random.random():
                 herbivore.dies() is False
        """
        herbivore = Herbivore(age=5, weight=20)
        omega = 0.4
        phi_age = 0.6
        a_half = 40.0
        phi_weight = 0.1
        weight = 20
        w_half = 10.0
        fitness = (1 / (1 + e ** (phi_age * (herbivore.age - a_half)))) * (
                1 / (1 + e ** (- phi_weight * (herbivore.weight - w_half))))
        death_prob = omega * (1 - fitness)
        random_prob = random.random()
        mocker.patch('random.random', return_value=random_prob)
        if weight == 0 or death_prob > random_prob:
            assert herbivore.dies() is True
        elif weight == 0 or death_prob <= random_prob:
            assert herbivore.dies() is False

    def test_dies_carnivore(self, mocker):
        """
        Test checks that method for carnivore death works as expected.\n
        if weight == 0 or death_prob > random.random():
        :return: carnivore.dies() is True
            elif weight == 0 or death_prob =< random.random():
                 carnivore.dies() is False
        """
        carnivore = Carnivore(age=5, weight=20)
        omega = 0.8
        phi_age = 0.3
        a_half = 40.0
        phi_weight = 0.4
        weight = 20
        w_half = 4.0
        fitness = (1 / (1 + e ** (phi_age * (carnivore.age - a_half)))) * (
                1 / (1 + e ** (- phi_weight * (carnivore.weight - w_half))))
        death_prob = omega * (1 - fitness)
        random_prob = random.random()
        mocker.patch('random.random', return_value=random_prob)
        if weight == 0 or death_prob > random.random():
            assert carnivore.dies() is True
        elif weight == 0 or death_prob <= random.random():
            assert carnivore.dies() is False

    def test_migration_prob_herbivore(self):
        """
        Test that checks the method for migration probability with herbivores works as expected.\n
        :return:
        """
        herbivore = Herbivore(age=5, weight=20)
        mu = 0.25
        phi_age = 0.6
        a_half = 40.0
        phi_weight = 0.1
        w_half = 10.0
        fitness = (1 / (1 + e ** (phi_age * (herbivore.age - a_half)))) * (
                1 / (1 + e ** (- phi_weight * (herbivore.weight - w_half))))
        migration_prob = mu * fitness
        expected_prob = herbivore.migration_prob()
        assert migration_prob == expected_prob

    def test_migration_prob_carnivore(self):
        """
        Test that checks the method for migration probability with carnivores works as expected.\n
        :return:
        """
        carnivore = Carnivore(age=5, weight=20)
        mu = 0.4
        phi_age = 0.3
        a_half = 40.0
        phi_weight = 0.4
        w_half = 4.0
        fitness = (1 / (1 + e ** (phi_age * (carnivore.age - a_half)))) * (
                     1 / (1 + e ** (- phi_weight * (carnivore.weight - w_half))))
        migration_prob = mu * fitness
        expected_prob = carnivore.migration_prob()
        assert migration_prob == expected_prob

    def test_calculate_fitness_herbivore(self):
        """
        Test checks that method for calculating fitness with herbivores works as expected.\n
        :return:
        """
        herbivore = Herbivore(age=5, weight=20)
        phi_age = 0.6
        a_half = 40.0
        phi_weight = 0.1
        w_half = 10.0
        expected_fitness = (1 / (1 + e ** (phi_age * (herbivore.age - a_half)))) * (
                1 / (1 + e ** (- phi_weight * (herbivore.weight - w_half))))
        herbivore.calculate_fitness()
        assert herbivore.fitness == expected_fitness

    def test_calculate_fitness_carnivore(self):
        """
        Test checks that method for calculating fitness with carnivores works as expected.\n
        :return:
        """
        carnivore = Carnivore(age=5, weight=20)
        phi_age = 0.3
        a_half = 40.0
        phi_weight = 0.4
        w_half = 4.0
        expected_fitness = (1 / (1 + e ** (phi_age * (carnivore.age - a_half)))) * (
                1 / (1 + e ** (- phi_weight * (carnivore.weight - w_half))))
        carnivore.calculate_fitness()
        assert carnivore.fitness == expected_fitness
