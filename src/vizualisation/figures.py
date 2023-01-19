# -*- coding: utf-8 -*-

import matplotlib.patches as mpatches
import textwrap

__author__ = 'Sindre Elias Hinderaker'
__email__ = 'sindre.elias.hinderaker@nmbu.no'

"""

"""


def create_map(geogr):
    """
    Plotting of the map of the island based on a specified string
    :param geogr: string specifying the map of the island. Possible characters:\n
    'L': lowland, 'H': highland, 'D': desert, 'W': water
    :return:
    """
    # Defining RGB colors for terrain types for the map
    # Divides each number by 255 to get value between 0 and 1,
    # because legend only accepts this value range
    #             R         G         B
    color_l = (0 / 255, 204 / 255, 102 / 255)    # Lowland, dark green
    color_h = (153 / 255, 255 / 255, 153 / 255)  # Highland, light green
    color_d = (255 / 255, 255 / 255, 85 / 255)   # Desert, yellow
    color_w = (51 / 255, 153 / 255, 255 / 255)   # Water, blue
    rgb_values = {'L': color_l,
                  'H': color_h,
                  'D': color_d,
                  'W': color_w}

    # Reading and collecting inputted map data
    n_rows = len(geogr.split())
    n_col = len([elem for elem in geogr.split()[0]])
    # New and simpler solution, inspiration from:
    # https://gitlab.com/nmbu.no/emner/inf200/h2021/inf200-course-materials/-/blob/main/january_block/examples/plotting/mapping.py
    map_list = [[rgb_values[letter] for letter in line]
                for line in geogr.split()]
    # Old solution
    # map_list = []
    # for rows in geogr.split():
    #     row_list = []
    #     for elem in rows:
    #         if elem == 'H':
    #             row_list.append(color_h)
    #             # print(('inside H'))
    #         elif elem == 'L':
    #             row_list.append(color_l)
    #             # print(('inside L'))
    #         elif elem == 'D':
    #             row_list.append(color_d)
    #             # print(('inside D'))
    #         elif elem == 'W':
    #             row_list.append(color_w)
    #             # print(('inside W'))
    #     map_list.append(row_list)
    # for index, li in enumerate(map_list):
    #    print(f'{index+1} Row', li)

    # Plotting
    # plt.imshow(map_list)
    # Figure axis configuration:
    # plt.xticks(range(1, n_col))
    # plt.yticks(range(1, n_rows))
    # plt.title("Island", pad=25)
    # Label setup and configuration, inspiration from:
    # https://stackoverflow.com/questions/25482876/how-to-add-legend-to-imshow-in-matplotlib
    # https://coderedirect.com/questions/388408/matplot-imshow-add-label-to-each-color-and-put-them-in-legend
    labels = ['Lowland', 'Highland', 'Desert', 'Water']
    labels = ['L', 'H', 'D', 'W']
    colors = [color_l, color_h, color_d, color_w]
    patches = [mpatches.Patch(color=colors[i], label=labels[i]) for i in range(len(labels))]
    # Placing a legend above this subplot, expanding itself to fully use the given bounding box.
    # plt.legend(handles=patches, loc=3, mode='expand',
    #            bbox_to_anchor=(0, 1, 1, 0), ncol=4, borderaxespad=0.3)
    # plt.legend(handles=patches, loc=3, mode='expand',
    #            bbox_to_anchor=(0, 1, 1, 0), ncol=4, borderaxespad=0.3)

    # plt.show()
    return map_list, n_col, n_rows, patches


if __name__ == '__main__':
    # Map data is defined as follows:
    geogr = """\
               WWWWWWWWWWWWWWWWWWWWW
               WHHHHHLLLLWWLLLLLLLWW
               WHHHHHLLLLWWLLLLLLLWW
               WHHHHHLLLLWWLLLLLLLWW
               WWHHLLLLLLLWWLLLLLLLW
               WWHHLLLLLLLWWLLLLLLLW
               WWWWWWWWHWWWWLLLLLLLW
               WHHHHHLLLLWWLLLLLLLWW
               WHHHHHHHHHWWLLLLLLWWW
               WHHHHHDDDDDLLLLLLLWWW
               WHHHHHDDDDDLLLLLLLWWW
               WHHHHHDDDDDLLLLLLLWWW
               WHHHHHDDDDDWWLLLLLWWW
               WHHHHDDDDDDLLLLWWWWWW
               WWHHHHDDDDDDLWWWWWWWW
               WWHHHHDDDDDLLLWWWWWWW
               WHHHHHDDDDDLLLLLLLWWW
               WHHHHDDDDDDLLLLWWWWWW
               WWHHHHDDDDDLLLWWWWWWW
               WWWHHHHLLLLLLLWWWWWWW
               WWWHHHHHHWWWWWWWWWWWW
               WWWWWWWWWWWWWWWWWWWWW"""

    geogr = textwrap.dedent(geogr)
    create_map(geogr)
