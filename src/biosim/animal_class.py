# -*- coding: utf-8 -*-

import random
from math import e

__author__ = 'Sindre Elias Hinderaker', 'Mathias Kristiansen'
__email__ = 'sindre.elias.hinderaker@nmbu.no' 'mathias.kristiansen0@nmbu.no'

"""
Contains an animal class with default parameters and methods
based on specifications in project description:
https://gitlab.com/nmbu.no/emner/inf200/h2021/inf200-course-materials/-/blob/main/january_block/INF200_H21_BioSimJan_v1.pdf
"""


class Animal:
    r"""
    Super class for with interface to handle custom species and various parameters set by user.

    Newborns are born with a weight drawn from the gaussian distribution

    :formulae: :math:`w \sim \mathcal{N}(w_{birth}, \sigma_{birth})`

    .. note::
            If weight is not provided it will default to None which leads to,
            a weight being drawn from the gaussian distribution.
    """

    def __init__(self, age=0, weight=None):
        # Initialization of common variables
        self.age = age
        self.weight = weight
        self.fitness = None
        self.a_half = 40.0
        self.zeta = 3.5
        self.phi_age = None
        self.phi_weight = None
        self.w_half = None
        self.mu = None
        self.omega = None
        self.eta = None

    def update_age(self):
        r"""
        Age increases by 1 at the end of each year cycle,
        leads to weight and fitness change.

        :formulae: :math:`w_{new} = w*\eta`
        """
        self.age += 1
        self.weight -= self.weight * self.eta
        self.calculate_fitness()

    def calculate_fitness(self):
        r"""
        Fitness is calculated for animal

        :formulae: :math:`\Phi = \cfrac{1}{1+e^{\phi_a({a - a_{1/2}})}} *
                   \cfrac{1}{1+e^{-\phi_w({w - w_{1/2}})}}`
        """

        if self.weight <= 0:
            self.fitness = 0
        else:
            self.fitness = (1 / (1 + e ** (self.phi_age * (self.age - self.a_half)))) * \
                           (1 / (1 + e ** (-self.phi_weight * (self.weight - self.w_half))))

    def migration_prob(self):
        r"""
        Calculates the probability of migration for the animal

        :return 0-1.0: float
        :formulae: :math:`p_{migrate} = \mu*\Phi`
        """
        return self.mu*self.fitness

    def weight_reduction(self, baby_weight):
        """
        Reduces weight of 'mother' based on baby birth-weight

        :param baby_weight: float
        """
        self.weight -= baby_weight
        self.calculate_fitness()

    def dies(self):
        r"""
        Checks if the animal dies

        :return True, False: bool

             True - if animal dies, False - if animal survives
        :formulae: :math:`p_{death} = \omega*(1-\Phi)`

        """
        death_prob = self.omega * (1 - self.fitness)
        if self.weight == 0 or death_prob > random.random():
            return True
        else:
            return False

    def set_animal_params(self, params):
        """
        Sets attributes/parameters of the animal based on a dictionary

        :param params: dict
        """
        for key, value in params.items():
            self.__setattr__(key, value)


# noinspection PyPep8Naming
class Herbivore(Animal):
    """Herbivores is a subclass of Animal"""

    def __init__(self, age=0, weight=None):
        super().__init__(age, weight)  # Inherit common parameters and methods
        # Specific parameters set according to Herbivore:
        self.sigma_birth = 1.5
        self.w_birth = 8.0
        self.beta = 0.9
        self.eta = 0.05
        self.phi_age = 0.6
        self.w_half = 10.0
        self.phi_weight = 0.1
        self.mu = 0.25
        self.gamma = 0.2
        self.xi = 1.2
        self.omega = 0.4
        self.F = 10.0

        if weight is None:
            self.weight = random.gauss(mu=self.w_birth, sigma=self.sigma_birth)

        self.calculate_fitness()  # calculate fitness on initialization, with default attributes

    def feed(self, available_fodder):
        """
        Herbivore feeding, leads to increased fitness and weight

        :param available_fodder: int
        :return F, available_fodder: int

            F - if animal eats until its full, available_fodder
            - if animal eats all remaining fodder
        :formulae: :math:`w = w + β * F`
        """
        # Increase weight of animal
        if available_fodder >= self.F:
            self.weight += self.beta * self.F
            self.calculate_fitness()  # weight change causes fitness change
            return self.F
        else:
            self.weight += self.beta * available_fodder
            self.calculate_fitness()  # weight change causes fitness change
            return available_fodder

    def gives_birth(self, N):
        r"""
        Checks if the animal gives birth

        :param N: int
        :return baby_herbivore: object, None

            object - if animal gives birth, None - if animal does not
        :formulae: :math:`p_{birth} = min(1, \gamma*\Phi*(N-1))`
        """
        birth_prob = min(1, self.gamma*self.fitness*(N - 1))
        if birth_prob > random.random() and \
                self.weight >= self.zeta * (self.w_birth + self.sigma_birth):
            baby_herbivore = Herbivore()  # new instance with birth weight and age=0
            if baby_herbivore.weight <= self.weight:
                self.weight_reduction(baby_herbivore.weight)
                return baby_herbivore
        else:
            return None


# noinspection PyPep8Naming
class Carnivore(Animal):
    """Carnivores is a subclass of Animal"""

    def __init__(self, age=0, weight=None):
        super().__init__(age, weight)  # Inherit common parameters and methods
        # Specific parameters set according to Carnivore:
        self.sigma_birth = 1.0
        self.w_birth = 6.0
        self.beta = 0.75
        self.eta = 0.125
        self.phi_age = 0.3
        self.w_half = 4.0
        self.phi_weight = 0.4
        self.mu = 0.4
        self.gamma = 0.8
        self.xi = 1.1
        self.omega = 0.8
        self.F = 50.0
        self.DeltaPhiMax = 10.0

        if self.weight is None:
            self.weight = random.gauss(mu=self.w_birth, sigma=self.sigma_birth)

        self.calculate_fitness()  # calculate fitness on initialization, with default attributes

    def hunt(self, herbivores):
        r"""
        Feeding method for carnivores.
        Goes through all the herbivores in the same cell as the carnivore
        and checks if the carnivore eats it or not. This depends on fitness of
        both carnivore and herbivore, the parameters 'DeltaPhiMax' and 'beta',
        and the appetite of the carnivore.
        Feeding leads to increased fitness and weight

        :param herbivores: list
        :return dead_herbivores: list
        :formulae: :math:`p_{kill} = 0`, if :math:`\Phi_{carn} \le \Phi_{herb}`

                   :math:`p_{kill} = \cfrac{\Phi_{herb}\Phi_{herb}}{\Delta\Phi_{max}}`,
                   if :math:`0 < \Phi_{carn}-\Phi_{herb} < \Delta\Phi_{max}`

                   :math:`p_{kill} = 1`, otherwise
        """
        dead_herbivores = []
        eaten_amount = 0
        for herbivore in herbivores:
            if eaten_amount >= self.F:
                return dead_herbivores
            if self.fitness <= herbivore.fitness:
                continue
            elif self.fitness - herbivore.fitness < self.DeltaPhiMax:
                if random.random() < (self.fitness - herbivore.fitness) / self.DeltaPhiMax:
                    dead_herbivores.append(herbivore)
                    eaten = min(self.F - eaten_amount, herbivore.weight)
                    self.weight += self.beta * eaten
                    self.calculate_fitness()  # fitness re-evaluation after kill
                    eaten_amount += eaten
            else:
                dead_herbivores.append(herbivore)
                eaten = min(self.F - eaten_amount, herbivore.weight)
                self.weight += self.beta * eaten
                self.calculate_fitness()  # fitness re-evaluation after kill
                eaten_amount += eaten

        return dead_herbivores

    def gives_birth(self, N):
        r"""
        Checks if the animal gives birth

        :param N: int
        :return baby_carnivore, None: object, None

            object - if animal gives birth, None - if animal does not give birth
        :formulae: :math:`p_{birth} = min(1, \gamma*\Phi*(N-1))`
        """
        birth_prob = min(1, self.gamma*self.fitness*(N - 1))
        if birth_prob > random.random() and \
                self.weight >= self.zeta * (self.w_birth + self.sigma_birth):
            baby_carnivore = Carnivore()  # new instance with birth weight and age=0
            if baby_carnivore.weight <= self.weight:
                self.weight_reduction(baby_carnivore.weight)
                return baby_carnivore
        else:
            return None
