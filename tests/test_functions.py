# -*- coding: utf-8 -*-

from utils.functions import create_island
import textwrap
import pytest

"""
File containing unit-tests for functions utilized in the simulation program
"""

__author__ = 'Sindre Elias Hinderaker', 'Mathias Kristiansen'
__email__ = 'sindre.elias.hinderaker@nmbu.no' 'mathias.kristiansen0@nmbu.no'


def test_all_types_large():
    """Checks that all types of landscape can be created in large map"""
    geogr = """\
                   WWWWWWWWWWWWWWWWWWWWW
                   WWWWWLHDHWWWWLLLLLLLW
                   WHHHHHLLLLWWLLLLLLLWW
                   WHHHHHHHHHWWLLLLLLWWW
                   WHHHHHLLLLLLLLLLLLWWW
                   WHHHHHLLLDDLLLHLLLWWW
                   WHHLLLLLDDDLLLHHHHWWW
                   WWHHHHLLLDDLLLHWWWWWW
                   WHHHLLLLLDDLLLLLLLWWW
                   WHHHHLLLLDDLLLLWWWWWW
                   WWHHHHLLLLLLLLWWWWWWW
                   WWWHHHHLLLLLLLWWWWWWW
                   WWWWWWWWWWWWWWWWWWWWW"""
    geogr = textwrap.dedent(geogr)
    create_island(island_map=geogr)


@pytest.mark.parametrize('bad_boundary', ['L', 'H', 'D'])
def test_invalid_boundary_top(bad_boundary):
    """Non-ocean top boundary must raise error"""
    geogr = "WWWWWWWWWW{}WWWWWWWW\nWWWWWLHDHWWWWLLLLLW\nWWWWWWWWWWWWWWWWWWW".format(bad_boundary)
    with pytest.raises(ValueError):
        create_island(island_map=geogr)


@pytest.mark.parametrize('bad_boundary', ['L', 'H', 'D'])
def test_invalid_boundary_bottom(bad_boundary):
    """Non-ocean bottom boundary must raise error"""
    geogr = "WWWWWWWWWWWWWWWWWWW\nWWWWWWWWWDWWWWWWWWW\nWWWWWWWWW{}WWWWWWWWW".format(bad_boundary)
    with pytest.raises(ValueError):
        create_island(island_map=geogr)


@pytest.mark.parametrize('bad_boundary', ['L', 'H', 'D'])
def test_invalid_boundary_right(bad_boundary):
    """Non-ocean right boundary must raise error"""
    geogr = "WWWWWWWWWWWWWWWWWWW\nWWWWWLHDHWWWWLLLLL{}\nWWWWWWWWWWWWWWWWWWW".format(bad_boundary)
    with pytest.raises(ValueError):
        create_island(island_map=geogr)


@pytest.mark.parametrize('bad_boundary', ['L', 'H', 'D'])
def test_invalid_boundary_left(bad_boundary):
    """Non-ocean left boundary must raise error"""
    geogr = "WWWWWWWWWWWWWWWWWWW\n{}WWWWLHDHWWWWLLLLLW\nWWWWWWWWWWWWWWWWWWW".format(bad_boundary)
    with pytest.raises(ValueError):
        create_island(island_map=geogr)


@pytest.mark.parametrize('invalid_landscape', ['A', 'B', 'C', '1', '!', ':', '/', '+'])
def test_invalid_landscape(invalid_landscape):
    """Invalid landscape type must raise error"""
    geogr = "WWWWWWWWWWWWWWWWWWW\n" \
            "WWWWWLHD{}WWWWLLLLLW\n" \
            "WWWWWWWWWWWWWWWWWWW".format(invalid_landscape)
    with pytest.raises(ValueError):
        create_island(island_map=geogr)


@pytest.mark.parametrize('length_1, length_2, length_3', [('W', 'WW', 'WWW'),
                                                          ('WWW', 'W', 'WW'),
                                                          ('WW', 'WWW', 'W')])
def test_inconsistent_length(length_1, length_2, length_3):
    """Inconsistent line length must raise error"""
    geogr = "WWWWWWWWWWWW{}\nWWWWWWWWWWWW{}\nWWWWWWWWWWWW{}".format(length_1, length_2, length_3)
    with pytest.raises(ValueError):
        create_island(island_map=geogr)
