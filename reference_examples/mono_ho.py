# -*- coding: utf-8 -*-

import textwrap
from biosim.simulation import BioSim

"""
Island with single lowland cell, first herbivores only, later carnivores.
"""

__author__ = 'Hans Ekkehard Plesser, NMBU'


geogr = """\
           WWW
           WLW
           WWW"""
geogr = textwrap.dedent(geogr)

ini_herbs = [{'loc': (2, 2),
              'pop': [{'species': 'Herbivore',
                       'age': 5,
                       'weight': 20}
                      for _ in range(50)]}]

my_img_dir = 'C:/Users/HP/Desktop/video'

for seed in range(100, 103):
    sim = BioSim(geogr, ini_herbs, seed=seed,  # img_dir='results'
                 img_dir=my_img_dir, img_base=f'mono_ho_{seed:05d}', img_years=300)
    sim.simulate(301)
