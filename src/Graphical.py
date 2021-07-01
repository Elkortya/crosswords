"""
Make a graphical output of a grid
"""


import cv2
import numpy as np
import os


def make_pretty_output_out_of_grid(grid,nb_box_h,nb_box_w):
    """ Make a graphical output of a grid. Saves the image in a folder.

    :param grid: (Grid) the grid we wish to plot
    :param nb_box_h: (int) number of horizontal boxes
    :param nb_box_w: (int) number of vertical boxes
    :return: None
    """

    # Graphical parameters
    npx = 200
    h = npx * nb_box_h
    w = npx * nb_box_w
    im = np.ones((h,w))*255
    th = 2
    text_thickness = 30

    # Draw the lines
    for i in range(nb_box_h):
        cv2.line(im,(0,i*npx),(w,i*npx),(0),thickness=th)

    for i in range(nb_box_w):
        cv2.line(im,(i*npx,0),(i*npx,h),(0),thickness=th)

    # Draw each letter
    for el,line in enumerate(grid):
        for ec,letter in enumerate(line):
            if letter.isalpha():
                cv2.putText(im,letter.upper(),
                            (
                            int((ec+0.2) * npx),
                            int((el+1-0.2)*npx)
                            ),
                            fontFace =cv2.FONT_HERSHEY_SIMPLEX,
                            thickness=text_thickness, fontScale= w/150, color = 0)
            # Draw black squares
            if letter == "$":
                im[el*npx:(el+1)*npx,ec*npx:(ec+1)*npx] = 0

    # Final tweaks
    margin = int(npx/2)
    im_final = np.ones((h+2*margin, w+2*margin))*255
    im_final[margin:h+margin,margin:w+margin] = im
    cv2.line(im_final,(margin,(nb_box_h)*npx+margin),(w+margin,(nb_box_h)*npx+margin),(0),thickness=th)
    cv2.line(im_final, ((nb_box_w) * npx+margin, 0+margin), ((nb_box_w) * npx+margin, h+margin), (0), thickness=th)

    # Save image
    cv2.imwrite(os.path.join(os.path.dirname(os.path.dirname(__file__)),"res", "result.png"), im_final)
