# -*- coding: utf-8 -*-

from biosim.geography_class import Lowland, Highland, Desert, Water

"""
File containing functions utilized by the simulation program
"""
__author__ = 'Sindre Elias Hinderaker', 'Mathias Kristiansen'
__email__ = 'sindre.elias.hinderaker@nmbu.no' 'mathias.kristiansen0@nmbu.no'


def create_island(island_map):
    """
    Creates a dictionary where the keys are coordinates and
    the value is the corresponding geography.

    :param island_map: string
    :return island: dict
    """
    # Want the following dict: {Coordinate: Landscape(loc, pop)/Terrain()/Geography()}
    valid_letters = ['L', 'H', 'D', 'W']
    invalid_border = ['L', 'H', 'D']
    lines = island_map.split()
    exp_line_length = len(lines[0])   # stores the length of first line to compare with
    # Inserts all coordinates as keys into dict, with terrain-letter as temporary value
    island = {}
    for x, line in enumerate(lines):

        # Checks for inconsistent line length
        if len(line) != exp_line_length:
            raise ValueError(f'Inconsistent line length for: {line}, '
                             f'expected length: {exp_line_length}')

        x += 1
        for y, letter in enumerate(line):
            y += 1

            # Checks that all letters used in the island string are valid
            if letter not in valid_letters:
                raise ValueError(f'Unknown geography type, only use the following letters: '
                                 f'{valid_letters}')
            # Checks that the top and left border only contains water coordinates
            if x == 1 and letter in invalid_border or y == 1 and letter in invalid_border:
                raise ValueError('The border must be only water')
            # Checks that the bottom and right border only contains water coordinates
            if x == len(lines) and letter in invalid_border or \
                    y == len(line) and letter in invalid_border:
                raise ValueError('The border must be only water')

            geography_types = {'L': Lowland(),
                               'H': Highland(),
                               'D': Desert(),
                               'W': Water()}
            island[(x, y)] = geography_types[letter]

    return island
