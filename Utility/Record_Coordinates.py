# -*- coding: utf-8 -*-
"""
Created on Sun Sep 13 12:23:30 2020

@author: eliott

Manual labelling of the positions of plants on an image.

The user indicate the directory where the images are stored and the index of 
the image in the corresponding list.
Then, on execution, the user can click on images to store the coordinates of the
target object. 
In the current version, both the raw RGB image and the Otsu image are needed
because we overlay the two types of images to help the user see where the plants
are located.
"""

import os
import json
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches

import general_IO as gIO


# =============================================================================
# Utility Functions Definition
# =============================================================================
def import_data(_path, _file_names, _import_function):
    data = []
    for _n in _file_names:
        data += [_import_function(_path + "/" + _n)]
    return data

def get_json_file_content(_path_json_file):
    f = open(_path_json_file)
    return json.load(f)

def get_img_array(path_img):
    img = Image.open(path_img)
    return np.array(img)

def get_file_lines(path_csv_file):
    file_object = open(path_csv_file, 'r')
    file_content = file_object.readlines()
    file_object.close()
    return(file_content)
    
# =============================================================================
# General Path Definition
# =============================================================================
#path of the images 
### TO BE CHANGED AS PER USER NEED
session_number = 1
unity_date = "images_niort_decoupees"
    
path_input_root = ""
path_input_raw = ""
names_input_raw = os.listdir(path_input_raw)

path_input_OTSU = ""
names_input_OTSU = os.listdir(path_input_OTSU)


path_output_position_files = ""

# =============================================================================
# Data Collection
# =============================================================================
print("Data Collection...", end = " ")

subset_size = 50

data_input_raw = import_data(path_input_raw,
                             names_input_raw[:subset_size],
                             get_img_array)
data_input_OTSU = import_data(path_input_OTSU,
                              names_input_OTSU[:subset_size],
                              get_img_array)

print("done")

def onclick(event):
    global ix, iy, coords, ax, image_size
    ix, iy = event.xdata, event.ydata
    print ("x = {0}, y = {1}".format(ix, iy))

    coords.append("{0},{1},{2},{3}".format(int(ix), image_size[0]-int(iy),
                                          ix/image_size[1], (image_size[0]-iy)/image_size[0]))
    
    circle = patches.Circle((ix, iy),
                            radius = 5,
                            linewidth = 2,
                            edgecolor = "red",
                            facecolor = "red")
    ax.add_patch(circle)
    fig.canvas.draw()

    return coords

def on_key(event):
    global coords,target_image
    print('you pressed', event.key)
    
    if (event.key == "enter"):
        name = names_input_raw[target_image].split(".")[0]
        gIO.writer(path_output_position_files, name+".csv",
                   coords, True, True)
    

target_image=49

fig = plt.figure()
ax = fig.add_subplot(111)
ax.imshow(data_input_raw[target_image])
ax.imshow(data_input_OTSU[target_image], alpha=0.2)

coords = []
image_size = data_input_OTSU[target_image].shape
print(image_size)

cid = fig.canvas.mpl_connect('button_press_event', onclick)
cid2 = fig.canvas.mpl_connect('key_press_event', on_key)