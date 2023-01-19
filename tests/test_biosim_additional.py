# -*- coding: utf-8 -*-

from biosim.simulation import BioSim
import matplotlib.pyplot as plt
import pytest
import os

__author__ = 'Sindre Elias Hinderaker'
__email__ = 'sindre.elias.hinderaker@nmbu.no'

"""
Test set with additional unit-tests and integration-tests for BioSim class interface.
"""


@pytest.fixture(autouse=True)
def close_figures():
    # no setup before tests
    yield
    # close figures after each test
    plt.close("all")


@pytest.fixture()
def delete_log_file():
    # no setup before tests
    yield
    # delete log_file after test is finished
    if os.path.exists("log_file.csv"):
        os.remove("log_file.csv")
    else:
        raise FileNotFoundError("The file was not found or does not exist")


def test_log_file_naming(delete_log_file):
    """Test that naming of log file according to input"""
    sim = BioSim(island_map="WW\nWW", ini_pop=[], seed=1, log_file='log_file')
    assert sim.log_file == 'log_file'


def test_log_file_init(delete_log_file):
    """Test that  initial content of log-file according to specifications"""
    sim = BioSim(island_map="WW\nWW", ini_pop=[], seed=1, log_file='log_file')
    exp_first_line = "This file contains animal counts from the BioSim package"
    exp_last_line = "Year,Herbivores,Carnivores,Total animals"
    with open(f'{sim.log_file}.csv', 'r') as file:
        lines = file.readlines()
    first_line = lines[0].strip()  # strip cleans off \n on last line
    last_line = lines[-1].strip()  # strip cleans off \n on last line
    assert exp_first_line == first_line and exp_last_line == last_line


def test_log_file_sim(delete_log_file):
    """Test that data appended to log file matches simulation status"""
    ini_pop = [{'loc': (2, 2),
                'pop': [{'species': 'Herbivore', 'age': 0, 'weight': 0},
                        {'species': 'Carnivore', 'age': 0, 'weight': 0},
                        {'species': 'Carnivore', 'age': 0, 'weight': 0}]
                }]
    sim = BioSim(island_map="WWW\nWDW\nWWW", ini_pop=ini_pop, seed=1, log_file='log_file')
    sim.simulate(1)
    exp_last_line = "1,1,2,3"
    with open(f'{sim.log_file}.csv', 'r') as file:
        lines = file.readlines()
    last_line = lines[-1].strip()  # strip cleans off \n on last line
    assert exp_last_line == last_line


@pytest.mark.parametrize('species', ['Herbivore', 'Carnivore'])
def test_set_animal_parameters(species):
    """Test that animal parameters are set according to specification and behaves accordingly"""
    ini_pop = [{'loc': (2, 2),
                'pop': [{'species': f'{species}',
                         'age': 5,
                         'weight': 20}]
                }]
    sim = BioSim(island_map="WWW\nWLW\nWWW", ini_pop=ini_pop, seed=1)
    species = f'{species}'
    params = {'phi_age': 0.2, 'DeltaPhiMax': 15}
    sim.set_animal_parameters(species=species, params=params)
    if species == 'Herbivore':
        animals = sim.island[(2, 2)].herbivores
    elif species == 'Carnivore':
        animals = sim.island[(2, 2)].carnivores
    else:
        raise ValueError('Unknown species')
    animal = animals[0]
    assert animal.DeltaPhiMax == params['DeltaPhiMax'] and animal.phi_age == params['phi_age']


@pytest.mark.parametrize('vis_years, img_years', [(2, 3), (3, 10), (4, 19)])
def test_img_years_vis_years(vis_years, img_years):
    """Test that checks if a value error is raised when img_years is not a multiple of vis_years"""
    sim = BioSim(island_map="WWW\nWWW\nWWW", ini_pop=[], seed=1,
                 vis_years=vis_years, img_years=img_years)
    with pytest.raises(ValueError):
        # since img_years % vis_years != 0 a value error should be raised when trying to simulate
        sim.simulate(num_years=1)


@pytest.mark.parametrize('lscape, params', [('L', {'f_max': 2.}), ('H', {'f_max': 30.})])
def test_set_landscape_parameters_known(lscape, params):
    """Test that parameters are set correctly and accessible on geography classes"""

    sim = BioSim(island_map="WWW\nW{}W\nWWW".format(lscape), ini_pop=[], seed=1, vis_years=0)
    sim.set_landscape_parameters(lscape, params)
    geography = sim.island[(2, 2)]
    exp_f_max = params['f_max']
    geography.grow_fodder()
    assert geography.f_max == exp_f_max and geography.fodder == exp_f_max


@pytest.mark.parametrize('lscape, params', [('W', {'f_max': 0}), ('D', {'f_max': 0})])
def test_set_landscape_parameters_unknown(lscape, params):
    """
    Test that parameters are not set when unknown or
    unsupported geography classes are provided
    """

    sim = BioSim(island_map="WWW\nW{}W\nWWW".format(lscape), ini_pop=[], seed=1, vis_years=0)
    with pytest.raises(ValueError):
        # expects value error because of unknown or unsupported landscape type
        sim.set_landscape_parameters(lscape, params)


@pytest.mark.parametrize('xy_1, xy_2', [((2, 2), (2, 3)),
                                        ((2, 3), (2, 4)),
                                        ((2, 4), (2, 2))])
def test_initial_population(xy_1, xy_2):
    """Test that populations are placed correctly on island"""

    ini_pop = [{'loc': xy_1,
                'pop': [{'species': 'Carnivore', 'age': 50, 'weight': 50},
                        {'species': 'Carnivore', 'age': 2, 'weight': 20}]},
               {'loc': xy_2,
                'pop': [{'species': 'Herbivore', 'age': 1, 'weight': 10},
                        {'species': 'Herbivore', 'age': 3, 'weight': 30}]}]
    exp_carn_age = ini_pop[0]['pop'][0]['age']
    exp_herb_age = ini_pop[1]['pop'][1]['age']
    sim = BioSim(island_map="WWWWWW\nWDLHDW\nWWWWWW", ini_pop=ini_pop,
                 seed=1, vis_years=0)
    carn_age = sim.island[xy_1].carnivores[0].age
    herb_age = sim.island[xy_2].herbivores[1].age
    assert carn_age == exp_carn_age and herb_age == exp_herb_age


def test_make_movie_runtime_error():
    """Test that make movie method is functional"""
    sim = BioSim(island_map="WW\nWW", ini_pop=[], seed=1)
    with pytest.raises(RuntimeError):
        # a runtime error should be raised, since no filename is defined
        sim.make_movie(movie_fmt='ffmpg')
