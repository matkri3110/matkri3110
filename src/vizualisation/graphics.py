# -*- coding: utf-8 -*-

"""
This script is based on the template from:
https://gitlab.com/nmbu.no/emner/inf200/h2021/inf200-course-materials/-/blob/main/january_block/examples/randvis_project/src/randvis/graphics.py

:mod:`biosim.graphics` provides graphics support for BioSim.

.. note::
   * This module requires the program ``ffmpeg`` or ``convert``
     available from `<https://ffmpeg.org>` and `<https://imagemagick.org>`.
   * You can also install ``ffmpeg`` using ``conda install ffmpeg``
   * You need to set the  :const:`_FFMPEG_BINARY` and :const:`_CONVERT_BINARY`
     constants below to the command required to invoke the programs
   * You need to set the :const:`_DEFAULT_FILEBASE` constant below to the
     directory and file-name start you want to use for the graphics output
     files.

"""

import matplotlib.pyplot as plt
import numpy as np
import subprocess
import os
from vizualisation.figures import create_map

__author__ = 'Sindre Elias Hinderaker', 'Mathias Kristiansen'
__email__ = 'sindre.elias.hinderaker@nmbu.no' 'mathias.kristiansen0@nmbu.no'

# Update these variables to point to your ffmpeg and convert binaries
# If you installed ffmpeg using conda or installed both software in
# standard ways on your computer, no changes should be required.
_FFMPEG_BINARY = 'ffmpeg'
_MAGICK_BINARY = 'magick'

# update this to the directory and file-name beginning
# for the graphics files
_DEFAULT_GRAPHICS_DIR = os.path.join('../..', 'data')
_DEFAULT_GRAPHICS_NAME = 'dv'
_DEFAULT_IMG_FORMAT = 'png'
_DEFAULT_MOVIE_FORMAT = 'mp4'   # alternatives: mp4, gif


class Graphics:
    """Provides graphics support for BioSim."""

    def __init__(self, img_dir=None, img_base=None, img_fmt=None, hist_specs=None, geogr=None):
        """
        :param img_dir: directory for image files; no images if None
        :type img_dir: str
        :param img_base: beginning of name for image files
        :type img_base: str
        :param img_fmt: image file format suffix
        :type img_fmt: str
        :param hist_specs: entry per property for which a histogram shall be shown
        :type img_fmt: dict
        :param geogr: string description of island
        """

        if img_base is None:
            img_base = _DEFAULT_GRAPHICS_NAME

        if img_dir is not None:
            self._img_base = os.path.join(img_dir, img_base)
        else:
            self._img_base = None

        self._img_fmt = img_fmt if img_fmt is not None else _DEFAULT_IMG_FORMAT

        self._img_ctr = 0
        self._img_step = 1

        # the following will be initialized by _setup_graphics
        self._fig = None
        self.island_map = None
        self.geogr = geogr

        self._heatmap_herb = None
        self._heatmap_carn = None
        self._img_data_herb = None
        self._img_data_carn = None

        self._animal_count = None
        self.ymax_animals = None
        self.cmax_animals = None

        self._herbivore_line = None
        self._carnivore_line = None

        self.hist_specs = hist_specs
        self.hist_weight = None
        self.hist_fitness = None
        self.hist_age = None

    def update(self, step, pop_map_herb, pop_map_carn, count_herb, count_carn,
               shape, pop_weights, pop_fitness, pop_age):
        """
        Updates graphics with current data and save to file if necessary.

        :param step: current time step i.e. year
        :param pop_map_herb: current population of herbivores (2d array)
        :param pop_map_carn: current population of carnivores (2d array)
        :param count_herb: current count of herbivores in system
        :param count_carn: current count of carnivores in system
        :param shape: shape of system/island (rows, columns)
        :param pop_weights: tuple of herbivore and carnivore arrays containing their weights
        :param pop_fitness: tuple of herbivore and carnivore arrays containing their fitness
        :param pop_age: tuple of herbivore and carnivore arrays containing their age
        """

        self._update_heatmap(pop_map_herb, pop_map_carn, shape)
        self._update_pop_graph(step, count_herb, count_carn)

        if self.hist_specs is not None:
            try:
                for key in self.hist_specs.keys():
                    if key == 'weight':
                        self._update_weight_hist(pop_weights)

                    if key == 'fitness':
                        self._update_fitness_hist(pop_fitness)

                    if key == 'age':
                        self._update_age_hist(pop_age)
            except AttributeError:
                raise AttributeError('hist_specs should be a dictionary')

        self._fig.suptitle(f'Year: {step}', fontsize=12)
        self._fig.canvas.flush_events()  # ensure every thing is drawn
        plt.pause(1e-6)  # pause required to pass control to GUI

        self._save_graphics(step)

    def make_movie(self, movie_fmt=None):
        """
        Creates MPEG4 movie from visualization images saved.

        .. :note:
            Requires ffmpeg for MP4 and magick for GIF

        The movie is stored as img_base + movie_fmt
        """

        if self._img_base is None:
            raise RuntimeError("No filename defined.")

        if movie_fmt is None:
            movie_fmt = _DEFAULT_MOVIE_FORMAT

        if movie_fmt == 'mp4':
            try:
                # Parameters chosen according to http://trac.ffmpeg.org/wiki/Encode/H.264,
                # section "Compatibility"
                subprocess.check_call([_FFMPEG_BINARY,
                                       '-i', f'{self._img_base}_%05d.png',
                                       '-y',
                                       '-profile:v', 'baseline',
                                       '-level', '3.0',
                                       '-pix_fmt', 'yuv420p',
                                      f'{self._img_base}.{movie_fmt}'])
            except subprocess.CalledProcessError as err:
                raise RuntimeError(f'ERROR: ffmpeg failed with: {err}')
        elif movie_fmt == 'gif':
            try:
                subprocess.check_call([_MAGICK_BINARY,
                                       '-delay', '1',
                                       '-loop', '0',
                                       f'{self._img_base}_*.png',
                                       f'{self._img_base}.{movie_fmt}'])
            except subprocess.CalledProcessError as err:
                raise RuntimeError(f'ERROR: convert failed with: {err}')
        else:
            raise ValueError(f'Unknown movie format: {movie_fmt}')

    def setup(self, final_step, img_step, ymax_animals=None, cmax_animals=None):
        """
        Prepare graphics.
        Call this before calling :meth:`update()` for the first time after
        the final time step has changed.

        :param final_step: last time step to be visualised (upper limit of x-axis)
        :param img_step: interval between saving image to file
        :param ymax_animals: maximum number displayed on y-axis on animal count
        :param cmax_animals: dict, mapping species names to number
        """

        self._img_step = img_step
        self.ymax_animals = ymax_animals
        self.cmax_animals = cmax_animals

        # create new figure window
        if self._fig is None:
            self._fig = plt.figure()
            # Settings for space adjustments between subplots
            # self._fig.subplots_adjust(left=0, bottom=None, right=None,
            #                           top=None, wspace=0, hspace=None)
            self._fig.subplots_adjust(hspace=0.75)
            gs = self._fig.add_gridspec(3, 3)  # specification of grid/subplot layout

            # DPI control figure size to suit 13/14"

        # Insertion of island map into subplot in figure
        if self.island_map is None:
            _map_list, _n_col, _n_rows, patches = create_map(geogr=self.geogr)
            # noinspection PyUnboundLocalVariable
            self.island_map = self._fig.add_subplot(gs[0, :1])
            self.island_map.set_title("Island")
            self.island_map.imshow(_map_list)
            # Figure axis configuration
            self.island_map.set_xticks(range(1, _n_col, 3))
            self.island_map.set_yticks(range(1, _n_rows, 3))
            # Placing legend above this, expanding itself to
            # fully use the given bounding box.
            # self.island_map.legend(handles=patches, loc=3, mode='expand',
            #                        bbox_to_anchor=(0, 1, 1, 0), ncol=4, borderaxespad=0.3)
            #                        #loc='center left', bbox_to_anchor=(1, 0.5)
            # Placing legend to the right of subplot, expanding itself
            # to fully use the given bounding box.
            self.island_map.legend(handles=patches, handlelength=0.5, handleheight=0.5,
                                   loc=7, mode='expand', bbox_to_anchor=(1, 0.5),
                                   borderaxespad=0.3, frameon=False)

        # Add subplot Herbivore heat map, for images created with imshow().
        # We cannot create the actual ImageAxis object before we know
        # the size of the image, so we delay its creation.
        if self._heatmap_herb is None:
            self._heatmap_herb = self._fig.add_subplot(gs[1, :1])
            self._heatmap_herb.title.set_text('Herbivores distribution')
            # self._heatmap_herb.set_xlabel('coordinate')
            # self._heatmap_herb.set_ylabel('coordinate')
            self._img_data_herb = None

        # Add subplot Carnivore heat map, for images created with imshow().
        # We cannot create the actual ImageAxis object before we know
        # the size of the image, so we delay its creation.
        if self._heatmap_carn is None:
            self._heatmap_carn = self._fig.add_subplot(gs[1, 2])
            self._heatmap_carn.title.set_text('Carnivores distribution')
            # self._heatmap_carn.set_xlabel('coordinate')
            # self._heatmap_carn.set_ylabel('coordinate')
            self._img_data_carn = None

        # Add subplot for line graph of total animal count of herbivores and carnivores.
        if self._animal_count is None:
            self._animal_count = self._fig.add_subplot(gs[0, 2:])
            self._animal_count.set_title('Animal count')
            # self._animal_count.yaxis.tick_right()
            # self._animal_count.set_xlabel("Years")
            # self._animal_count.set_ylabel("Population")

            if self.ymax_animals is not None:
                # limit of y-axis specified by user
                self._animal_count.set_ylim(0, self.ymax_animals)

            elif self.ymax_animals is None:
                self._animal_count.set_ylim(auto=True)
                self._animal_count.set_autoscaley_on(True)
            # this should autoscale the limit of the y-axsis of the population graph
            # but it does not seem to work properly.
            # Implemented instead manual override in "_update_pop_graph"

        # needs updating on subsequent calls to simulate()
        # add 1, so we can show values for time zero and time final_step
        self._animal_count.set_xlim(0, final_step+1)

        if self._herbivore_line is None:
            mean_plot = self._animal_count.plot(np.arange(0, final_step+1),
                                                np.full(final_step+1, np.nan))
            self._herbivore_line = mean_plot[0]
        else:
            x_data, y_data_herb = self._herbivore_line.get_data()
            x_new = np.arange(x_data[-1] + 1, final_step+1)
            if len(x_new) > 0:
                y_new = np.full(x_new.shape, np.nan)
                self._herbivore_line.set_data(np.hstack((x_data, x_new)),
                                              np.hstack((y_data_herb, y_new)))

        if self._carnivore_line is None:
            mean_plot_carn = self._animal_count.plot(np.arange(0, final_step+1),
                                                     np.full(final_step+1, np.nan))
            self._carnivore_line = mean_plot_carn[0]
        else:
            x_data, y_data_carn = self._carnivore_line.get_data()
            x_new = np.arange(x_data[-1] + 1, final_step+1)
            if len(x_new) > 0:
                y_new = np.full(x_new.shape, np.nan)
                self._carnivore_line.set_data(np.hstack((x_data, x_new)),
                                              np.hstack((y_data_carn, y_new)))
        # self._animal_count.legend(labels=['H', 'C'], loc=3,
        # mode='expand', bbox_to_anchor=(0, 1, 1, 0),
        # ncol=2, borderaxespad=0.3, frameon=False)
        self._animal_count.legend(labels=['H', 'C'], handlelength=0.5, loc=6,
                                  mode='expand', bbox_to_anchor=(1, 0.5),
                                  borderaxespad=0.3, frameon=False)

        # Add subplot Herbivore histogram
        if self.hist_specs is not None:
            if self.hist_weight is None and self.hist_specs['weight']:
                self.hist_weight = self._fig.add_subplot(gs[2, 0])

            if self.hist_fitness is None and self.hist_specs['fitness']:
                self.hist_fitness = self._fig.add_subplot(gs[2, 1])

            if self.hist_age is None and self.hist_specs['age']:
                self.hist_age = self._fig.add_subplot(gs[2, 2])

    def _update_heatmap(self, pop_map_herb, pop_map_carn, shape):
        """Update the heatmaps for herbivores and carnivores"""

        # Heatmap for Herbivores
        if self._img_data_herb is not None:
            self._img_data_herb.set_data(pop_map_herb)
        else:
            if self.cmax_animals is not None and 'Herbivore' in self.cmax_animals.keys():
                cmax_herb = self.cmax_animals['Herbivore']
                self._img_data_herb = self._heatmap_herb.imshow(pop_map_herb,
                                                                interpolation='nearest',
                                                                vmin=0, vmax=cmax_herb)
            else:
                self._img_data_herb = self._heatmap_herb.imshow(pop_map_herb,
                                                                interpolation='nearest',
                                                                vmin=0, vmax=200)
            self._heatmap_herb.set_xticks(range(1, shape[1], 3))   # dynamic x ticks
            self._heatmap_herb.set_yticks(range(1, shape[0], 3))   # dynamic y ticks
            plt.colorbar(self._img_data_herb, ax=self._heatmap_herb,
                         orientation='vertical')  # label="Population density"

        # Heatmap for Carnivores
        if self._img_data_carn is not None:
            self._img_data_carn.set_data(pop_map_carn)
        else:
            if self.cmax_animals is not None and 'Carnivore' in self.cmax_animals.keys():
                cmax_carn = self.cmax_animals['Carnivore']
                self._img_data_carn = self._heatmap_carn.imshow(pop_map_carn,
                                                                interpolation='nearest',
                                                                vmin=0, vmax=cmax_carn)
            else:
                self._img_data_carn = self._heatmap_carn.imshow(pop_map_carn,
                                                                interpolation='nearest',
                                                                vmin=0, vmax=50)
            self._heatmap_carn.set_xticks(range(1, shape[1], 3))   # dynamic x ticks
            self._heatmap_carn.set_yticks(range(1, shape[0], 3))   # dynamic y ticks
            plt.colorbar(self._img_data_carn, ax=self._heatmap_carn,
                         orientation='vertical')  # label="Population density"

    def _update_pop_graph(self, step, count_herb, count_carn):
        """Updates population graph (animal count)"""
        # Plotting of total number of herbivores
        y_data_herb = self._herbivore_line.get_ydata()
        y_data_herb[step] = count_herb
        self._herbivore_line.set_ydata(y_data_herb)

        # Plotting of total number of carnivore
        y_data_carn = self._carnivore_line.get_ydata()
        y_data_carn[step] = count_carn
        self._carnivore_line.set_ydata(y_data_carn)

        # Manual "Autoscale" y-axis
        if self.ymax_animals is None and count_herb > count_carn:
            # dynamic/scaling limit of y-axis
            self._animal_count.set_ylim(bottom=0, top=count_herb+200)

        elif self.ymax_animals is None and count_herb < count_carn:
            # dynamic/scaling limit of y-axis
            self._animal_count.set_ylim(bottom=0, top=count_carn+200)

    def _update_weight_hist(self, pop_weights):
        """Updates weight histogram (animal count)"""
        # Plotting of weight of herbivores
        w_spec = self.hist_specs['weight']
        w_max = w_spec['max']
        w_delta = w_spec['delta']
        w_n_bins = round(w_max / w_delta)
        self.hist_weight.clear()
        self.hist_weight.set_title('Weight')
        self.hist_weight.hist(x=pop_weights, range=(0, w_max), bins=w_n_bins,
                              histtype='step', stacked=True, fill=False)
        # self.hist_weight.set_xticks(range(0, w_max, round(w_n_bins/2)))

    def _update_fitness_hist(self, pop_fitness):
        """Updates fitness histogram (animal count)"""
        # Plotting of weight of herbivores
        f_spec = self.hist_specs['fitness']
        f_max = f_spec['max']
        f_delta = f_spec['delta']
        f_n_bins = round(f_max / f_delta)
        self.hist_fitness.clear()
        self.hist_fitness.set_title('Fitness')
        self.hist_fitness.hist(x=pop_fitness, range=(0, f_max), bins=f_n_bins,
                               histtype='step', stacked=True, fill=False)

    def _update_age_hist(self, pop_age):
        """Updates age histogram (animal count)"""
        # Plotting of weight of herbivores
        a_spec = self.hist_specs['age']
        a_max = a_spec['max']
        a_delta = a_spec['delta']
        a_n_bins = round(a_max / a_delta)
        self.hist_age.clear()
        self.hist_age.set_title('Age')
        self.hist_age.hist(x=pop_age, range=(0, a_max), bins=a_n_bins,
                           histtype='step', stacked=True, fill=False)
        # self.hist_age.set_xticks(range(0, a_max, a_n_bins))

    def _save_graphics(self, step):
        """Saves graphics to file if file name given."""

        if self._img_base is None or step % self._img_step != 0:
            return

        plt.savefig(f'{self._img_base}_{self._img_ctr:05d}.{self._img_fmt}')
        self._img_ctr += 1
