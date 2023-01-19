# -*- coding: utf-8 -*-

from biosim.animal_class import Animal, Carnivore, Herbivore
import pytest

__author__ = 'Sindre Elias Hinderaker'
__email__ = 'sindre.elias.hinderaker@nmbu.no'

"""
Test set with additional unit-tests for methods and attributes in the Animal-class.
"""


class TestAnimalUnittest:

    @pytest.fixture(autouse=True)
    def create_animals(self):
        """Creates a dict containing all possible instances of the animal-class"""
        self.animals = {'animal': Animal(age=5, weight=50),
                        'herbivore': Herbivore(age=4, weight=45),
                        'carnivore': Carnivore(age=3, weight=40)}

    @pytest.mark.parametrize('animal_type, exp_res', [('animal', None),
                                                      ('herbivore', Herbivore),
                                                      ('carnivore', Carnivore)])
    def test_gives_birth_true(self, mocker, animal_type, exp_res):
        N = 11
        animal = self.animals[animal_type]
        # Manipulates animal attributes
        animal.fitness = 0.5
        animal.gamma = 0.5
        animal.zeta = 1
        animal.w_birth = 1
        animal.sigma_birth = 1
        # birth_prob: min(1, gamma * fitness * (N-1)) --> min(1, 0.25*(10)) = 1
        # knows that the gives_birth method uses random.random() compared against birth_prob
        mocker.patch('random.random', return_value=0.5)
        # also compared against: weight >= zeta * (w_birth + sigma_birth)
        # --> (50, 45, 40) >= 1 * (1+1) --> (50, 45, 40) >= 2:
        # gives birth should now return a new class instance:
        # if birth weight of baby is lower than 'mother'
        # knows that the when baby is 'born' random.gauss() is used to assign birth-weight
        mocker.patch('random.gauss', return_value=10)    # (50, 45, 40) > 10
        if animal_type == 'animal':
            with pytest.raises(AttributeError):
                # 'Animal' object has no attribute 'gives_birth'
                animal.gives_birth(N)
        else:
            baby = animal.gives_birth(N)
            assert isinstance(baby, exp_res)  # assuming isinstance is ok when writing tests

    @pytest.mark.parametrize('animal_type', ['animal', 'herbivore', 'carnivore'])
    def test_gives_birth_true_low_weight(self, mocker, animal_type):
        exp_res = None
        N = 11
        animal = self.animals[animal_type]
        # Manipulates animal attributes
        animal.fitness = 0.5
        animal.gamma = 0.5
        animal.zeta = 1
        animal.w_birth = 1
        animal.sigma_birth = 1
        # birth_prob: min(1, gamma * fitness * (N-1)) --> min(1, 0.25*(10)) = 1
        # knows that the gives_birth method uses random.random() compared against birth_prob
        mocker.patch('random.random', return_value=0.5)
        # same as for test_gives_birth_true, but manipulates birth-weight value
        # to be larger than 'mother' weight, and thus return None
        mocker.patch('random.gauss', return_value=60)  # (50, 45, 40) < 60
        if animal_type == 'animal':
            with pytest.raises(AttributeError):
                # 'Animal' object has no attribute 'gives_birth'
                animal.gives_birth(N)
        else:
            baby = animal.gives_birth(N)
            assert baby == exp_res

    @pytest.mark.parametrize('animal_type', ['animal', 'herbivore', 'carnivore'])
    def test_gives_birth_false(self, mocker, animal_type):
        exp_res = None
        N = 11
        animal = self.animals[animal_type]
        # Manipulates animal attributes
        animal.fitness = 0.1
        animal.gamma = 0.1
        # birth_prob: min(1, animal.gamma * animal.fitness * (N-1)) => min(1, 0.01*(10)) = 0.1
        # knows that the gives_birth method uses random.random() compared against birth_prob
        mocker.patch('random.random', return_value=1)
        # gives birth should now return None:
        if animal_type == 'animal':
            with pytest.raises(AttributeError):
                # 'Animal' object has no attribute 'gives_birth'
                animal.gives_birth(N)
        else:
            res = animal.gives_birth(N)
            assert res == exp_res

    @pytest.mark.parametrize('herb_fit, carn_fit, exp_res', [(1, 0.5, 0),
                                                             (0.5, 1, 5)])
    def test_hunt_herbivores_all_none_eaten(self, create_animals, mocker,
                                            herb_fit, carn_fit, exp_res):
        herbivores = [self.animals['herbivore'] for _ in range(5)]  # creating list of herbivores
        for herbivore in herbivores:
            herbivore.fitness = herb_fit
            herbivore.weight = 1
        carn = self.animals['carnivore']
        carn.fitness = carn_fit
        mocker.patch('random.random', return_value=0)
        dead_herbivores = carn.hunt(herbivores)
        assert len(dead_herbivores) == exp_res

    def test_hunt_herbivores(self, create_animals, mocker):
        herbivores = [self.animals['herbivore'] for _ in range(4)]  # creating list of herbivores
        for herbivore in herbivores:
            herbivore.fitness = 0
            herbivore.weight = 100
        carn = self.animals['carnivore']
        carn.fitness = 1
        carn.DeltaPhiMax = 0.5
        F_before_hunt = carn.F
        mocker.patch('random.random', return_value=0)
        dead_herbivores = carn.hunt(herbivores)
        assert len(dead_herbivores) == 1 and carn.F == F_before_hunt
