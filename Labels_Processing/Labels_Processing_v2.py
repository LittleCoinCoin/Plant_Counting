# -*- coding: utf-8 -*-
"""
Created on Sat Feb  6 14:17:38 2021

@author: eliot

Here we include the functions used to process the labelled images generated with
Unity
"""
import os
import sys
import numpy as np
np.set_printoptions(threshold=sys.maxsize)

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from PIL import Image
import json

os.chdir("../Utility")
import general_IO as gIO

viewport_annotation_id = "c0b4a22c-0420-4d9f-bafc-954b8f7b35a7"

def Produce_Adjusted_Position_Files( _path_position_file,
                                     _path_adjusted_position_files,
                                     _rows_real_angle,
                                     _path_input_rgb_img,
                                     _list_rgb_images,
                                     _pivot = np.array([960,540])
                                     ):
    
    posFile = open(_path_position_file+"/"+"/captures_000.json", 'r')
    
    posFile_deserialized = json.load(posFile)
    
    nb_capture = len(posFile_deserialized["captures"])
    
# =============================================================================
#     print(nb_capture)
#     print(posFile_deserialized)
# =============================================================================
    
    ViewPortValues = []
    for i in range(nb_capture):
        for _annot in posFile_deserialized["captures"][i]["annotations"]:
            if (_annot["annotation_definition"] == viewport_annotation_id):
                ViewPortValues += [_annot["values"]]
    
    #print(ViewPortValues)
    
    nb_imgs = len(_list_rgb_images)
    print(nb_imgs, len(ViewPortValues))
    assert nb_imgs == len(ViewPortValues)
    
    _theta = np.deg2rad(_rows_real_angle)
    R = np.array([[np.cos(_theta), np.sin(_theta)],
                         [-np.sin(_theta),  np.cos(_theta)]])
    
    
    for i in range (nb_imgs):
        _img = Image.open(_path_input_rgb_img+\
                          "/" + _list_rgb_images[i])
        #_img_rot = _img.rotate(_rows_real_angle, expand=True)
        
        a = np.array([_img.width, 0])
        #b = np.array([0, 0])
        #offset to have only positives coordinates
        y_offset_p = (np.dot(R, a-_pivot))+_pivot
        x_offset_p = (np.dot(R, -_pivot))+_pivot
        
# =============================================================================
#         plt.figure()
#         plt.imshow(_img.rotate(_rows_real_angle, expand=True))
#         plt.scatter(x_offset_p[0]-x_offset_p[0],x_offset_p[1]-y_offset_p[1])
#         plt.scatter(y_offset_p[0]-x_offset_p[0],y_offset_p[1]-y_offset_p[1])
#         print(x_offset_p, y_offset_p)
# =============================================================================
        nb_plants = len(ViewPortValues[i])
        print(nb_plants)
        y_offset = y_offset_p[1]
        x_offset = x_offset_p[0]
        
        _adjusted_pos = []
        _x = []
        _y = []
        for j in range(nb_plants):
            #print(ViewPortValues[i][j])
            _screen_prop = np.array([ViewPortValues[i][j]["ViewPort"]["x"],
                                     ViewPortValues[i][j]["ViewPort"]["y"]])
            
            _rot_coord = np.dot(R, np.array([_screen_prop[0] *_img.width,
                                             (1-_screen_prop[1])*_img.height])-_pivot)+\
                        _pivot + np.array([-x_offset, -y_offset])
                        
                        
            _adjusted_pos  += [{"instance_id": ViewPortValues[i][j]["instance_id"],
                                "view_port_x": ViewPortValues[i][j]["ViewPort"]["x"],
                                "view_port_y": ViewPortValues[i][j]["ViewPort"]["y"],
                                "image_x": _screen_prop[0] *_img.width,
                                "image_y": (1-_screen_prop[1])*_img.height,
                                "rotated_x": _rot_coord[0],
                                "rotated_y": _rot_coord[1]}]
            
            _x.append(_rot_coord[0])
            _y.append(_rot_coord[1])
            
        #print(_adjusted_pos)
        
        gIO.check_make_directory(_path_adjusted_position_files)
        gIO.WriteJson(_path_adjusted_position_files, 
                      "Adjusted_plant_positions_"+_list_rgb_images[i].split(".")[0],
                      _adjusted_pos)
# =============================================================================
#         plt.figure()
#         plt.imshow(_img.rotate(_rows_real_angle, expand=True))
#         plt.scatter(_x, _y)
# =============================================================================

def Compute_Pixels_In_Plant_Bounding_Boxes(_path_input_position_files,
                                          _path_output_files,
                                          _path_input_Support_Images):
    
    _list_support_images = os.listdir(_path_input_Support_Images)
    nb_imgs = len(_list_support_images)
    
    _list_position_files = os.listdir(_path_input_position_files)
    nb_pos_files = len(_list_position_files)
    
    print(_list_position_files, _list_support_images)
    
    assert nb_imgs==nb_pos_files
    
    gIO.check_make_directory(_path_output_files)
    
    for i in range(1):
        print ("Processing Bounding Boxes of Image {0}/{1}".format(i+1, nb_imgs))
        
        _img = Image.open(_path_input_Support_Images+\
                          "/" + _list_support_images[i])
        
        _pos_file_content = gIO.reader(_path_input_position_files,
                                       _list_position_files[i])
    
        dict_img_plants_bounding_boxes = Extract_Plant_Bounding_Boxes(_img,
                                                                      _pos_file_content)
        
        original_box_corners, rotated_box_corners, ordered_keys = Correct_Extracted_Plant_Bounding_Boxes(dict_img_plants_bounding_boxes)
        
        All_Explorers = Get_Box_Explorers(original_box_corners,
                                          dict_img_plants_bounding_boxes, ordered_keys)
        
        #print(All_Explorers)
        nb_box = len( original_box_corners)
        for j in range (nb_box):
# =============================================================================
#             print(dict_img_plants_bounding_boxes[ordered_keys[j]]["center"])
# =============================================================================
            nb_pix = Compute_Surface(_img, rotated_box_corners[j], All_Explorers[j])
            
            dict_img_plants_bounding_boxes[ordered_keys[j]]["Nb_White_Pixels"] = nb_pix
        
# =============================================================================
#         name = "Bounding_Boxes_"+_list_position_files[i].split(".")[0]
#         file = open(_path_output_files+"/"+name+".json", "w")
#         json.dump(dict_img_plants_bounding_boxes, file, indent = 2)
#         file.close()
# =============================================================================
        
        Show_Boxes_And_Explorers(_img,
                                 rotated_box_corners,
                                 All_Explorers)
        
        #print (dict_img_plants_bounding_boxes)

def Extract_Plant_Bounding_Boxes(_img, _pos_file_content):
        
    _dict_all_bounding_boxes = {}
    for _line in _pos_file_content:
        _dict_bounding_box = {}
        _line_split = _line[:-1].split(",")
        _dict_bounding_box["center"]=[int(float(_line_split[2])*_img.width),
                                      int((1-float(_line_split[3]))*_img.height)]
        _dict_bounding_box["width"]=int(float(_line_split[4])*_img.width)
        _dict_bounding_box["height"]=int(float(_line_split[5])*_img.height)
        _dict_bounding_box["angle"]=float(_line_split[6])
        
        _dict_all_bounding_boxes[_line_split[0]+"_"+_line_split[1]]=_dict_bounding_box
            
    return _dict_all_bounding_boxes

def Correct_Extracted_Plant_Bounding_Boxes(_dict_img_plants_bounding_boxes):
    
    _ordered_keys = []
    _original_corners = []
    _rotated_corners = []
    for (_k,_v) in _dict_img_plants_bounding_boxes.items():
        
        _ordered_keys += [_k]
        
        _pivot = np.array(_v["center"])
        _theta = np.deg2rad(_v["angle"])
        R = np.array([[np.cos(_theta), -np.sin(_theta)],
                         [np.sin(_theta),  np.cos(_theta)]])
        
        p_SW = np.array((_v["center"][0]-np.ceil(0.25*_v["width"]),
                         _v["center"][1]-np.ceil(0.5*_v["height"])))
        p_SW_rot = np.dot(R, p_SW-_pivot)+_pivot
        
        p_NW = np.array((_v["center"][0]-np.ceil(0.25*_v["width"]),
                         _v["center"][1]+np.ceil(0.5*_v["height"])))
        p_NW_rot = np.dot(R, p_NW-_pivot)+_pivot
        
        p_NE = np.array((_v["center"][0]+np.ceil(0.25*_v["width"]),
                         _v["center"][1]+np.ceil(0.5*_v["height"])))
        p_NE_rot = np.dot(R, p_NE-_pivot)+_pivot
        
        p_SE = np.array((_v["center"][0]+np.ceil(0.25*_v["width"]),
                         _v["center"][1]-np.ceil(0.5*_v["height"])))
        p_SE_rot = np.dot(R, p_SE-_pivot)+_pivot
        
# =============================================================================
#         print([p_SW, p_NW, p_NE, p_SE])
#         print([p_SW_rot, p_NW_rot, p_NE_rot, p_SE_rot])
# =============================================================================
        _original_corners += [[p_SW, p_NW, p_NE, p_SE]]
        _rotated_corners += [[p_SW_rot, p_NW_rot, p_NE_rot, p_SE_rot]]
        
    return _original_corners, _rotated_corners, _ordered_keys

def Get_All_Line_Parameters(_rotated_corners):
    para1 = Compute_Line_Equation(_rotated_corners[0],_rotated_corners[1]) #Line SW, NW
    para2 = Compute_Line_Equation(_rotated_corners[1],_rotated_corners[2]) #Line NW, NE
    para3 = Compute_Line_Equation(_rotated_corners[2],_rotated_corners[3]) #Line NE, SE
    para4 = Compute_Line_Equation(_rotated_corners[3],_rotated_corners[0]) #Line SE, SW
    
    return [para1, para2, para3, para4]
    

def Get_Box_Explorers(_original_corners,
                      _dict_img_plants_bounding_boxes, _ordered_dict_keys,
                      _translation_dividor = 10):
    
    All_Explorers = []
    nb_boxes = len(_original_corners)
    #c = 0
    for i in range(nb_boxes):
        #print(c)
# =============================================================================
#         if (_box[0][0] != _box[1][0]):
#             all_para = Get_All_Line_Parameters(_box)
#             
#             b_max = max(all_para[0][1],all_para[2][1]) # max b of lines (SW, NW) & (NE, SE)
#             b_min = min(all_para[0][1],all_para[2][1]) # min b of lines (SW, NW) & (NE, SE)
#             
#             _translation_step = (b_max-b_min)/_translation_dividor
#             if (_translation_step < 1 ):
#                 _translation_step = 1
#             print (b_min, b_max, _translation_step)
#             
#             _box_explorers = []
#             while b_min + _translation_step < b_max:
#                 b_min += _translation_step
#                 _translated_line_params = (all_para[0][0], b_min) #lines ara parallel so all_para[0][0] or all_para[2][0] do not matter
#                 #
#                 print ("_translated_line_params", _translated_line_params,
#                        "all_para[1]", all_para[1])
#                 _p1_intersection = Line_Intersection(_translated_line_params, all_para[1])
#                 _p2_intersection = Line_Intersection(_translated_line_params, all_para[3])
#                 
#                 print ("_p1_intersection",_p1_intersection)
#                 
#                 x_lim = (int(min(_p1_intersection[0], _p2_intersection[0])),
#                          int(max(_p1_intersection[0], _p2_intersection[0])))
#                 
#                 print (x_lim)
#     
#                 _box_explorers += Sample_Line(_translated_line_params, x_lim)
#                 
#             All_Explorers += [_box_explorers]
#         
#         else:
# =============================================================================
        x_lim = (int(min(_original_corners[i][0][0],_original_corners[i][2][0])),
                int(max(_original_corners[i][0][0], _original_corners[i][2][0])))
        y_lim = (int(min(_original_corners[i][0][1],_original_corners[i][1][1])),
                int(max(_original_corners[i][0][1], _original_corners[i][1][1])))
        
        _translation_step = int((y_lim[1]-y_lim[0])/_translation_dividor)
        if (_translation_step < 1 ):
            _translation_step = 1
        
        _box_explorers = []
        for _b in range ( y_lim[0] + _translation_step,
                         y_lim[1],
                         _translation_step):
            _box_explorers += Sample_Line((0, _b), x_lim)
            
        rotated_box_explorers = []
        for _explorers in _box_explorers:
            _pivot = np.array(_dict_img_plants_bounding_boxes[_ordered_dict_keys[i]]["center"])
            _point = np.array(_explorers)
            _theta = np.deg2rad(_dict_img_plants_bounding_boxes[_ordered_dict_keys[i]]["angle"])
            R = np.array([[np.cos(_theta), -np.sin(_theta)],
                             [np.sin(_theta),  np.cos(_theta)]])
            _rotated_point = np.dot(R, _point-_pivot)+_pivot
            rotated_box_explorers += [_rotated_point]
        
        All_Explorers += [rotated_box_explorers]
        
        #c += 1
    
    return All_Explorers

def Compute_Surface(_img, _box_corners, _box_explorers):
        """
        Counts the number of white pixels in the area covered by the bounding box.
        """
        _img_array = np.array(_img)
        
        nb_contiguous_white_pixel = 0 #reset
        
        _xs = [_box_corners[i][0] for i in range (4)]
        _ys = [_box_corners[i][1] for i in range (4)]
        square_width = int(max(_xs) - min(_xs))
        square_height = int(max(_ys) - min(_ys))
        
        anchor_x = int(min(_xs))
        anchor_y = int(min(_ys))

        surface_print=np.zeros((square_height,square_width))
        
        directions = [(0,1), (0,-1), (1,0), (-1,0)] #(x, y)

        nb_explorers = len(_box_explorers)
# =============================================================================
#         print("nb_explorers", nb_explorers)
# =============================================================================
        while nb_explorers > 0:
# =============================================================================
#             print (_box_explorers[0])
# =============================================================================
            print_row = int(_box_explorers[0][1])-anchor_y#row coord in surface print array
            print_col = int(_box_explorers[0][0])-anchor_x#column coord in surface print array
            
            image_row = int(_box_explorers[0][1])#row coord in image array
            image_col = int(_box_explorers[0][0])#col coord in image array
# =============================================================================
#             print ("print_row", print_row, "print_col", print_col, 
#                    "image_row", image_row, "image_col", image_col)
# =============================================================================
            if (image_row < _img.height and 
                image_col < _img.width):# and
                #print_row < surface_print.shape[0] and 
                #print_col < surface_print.shape[1]
                #Is_Point_Inside_Rectangle((print_col, print_row), _box_corners)):
# =============================================================================
#                 print(_img_array[image_row][image_col])
# =============================================================================
                if (_img_array[image_row][image_col][0] > 220):#if the pixel is white
                    surface_print[print_row][print_col]=2
                    nb_contiguous_white_pixel +=1
                    
                    for _d in directions:
                        if (Is_Point_Inside_Rectangle((image_col+_d[0], image_row+_d[1]), _box_corners)):
                            if (0 <= print_row + _d[1] < square_height and
                                0 <= print_col + _d[0] < square_width):#if in the bounds of the surface_print array size
                                if (surface_print[print_row + _d[1]][print_col + _d[0]] == 0):#if the pixel has not an explorer already
                                    
                                    surface_print[print_row+_d[1]][print_col+_d[0]]=1#we indicate that we have added the coords to the explorers
                                    
                                    new_explorer_x = image_col + _d[0]
                                    new_explorer_y = image_row + _d[1]
                                    _box_explorers += [(new_explorer_x, 
                                                        new_explorer_y)]
                                    nb_explorers += 1
            
            _box_explorers = _box_explorers[1:]
            nb_explorers -= 1
            
            #nb_op+=1
# =============================================================================
#         print(surface_print)
# =============================================================================
# =============================================================================
#         fig = plt.figure(figsize=(5,5),dpi=300)
#         ax = fig.add_subplot(111)
#         ax.imshow(surface_print)
#         print("nb_white_pixels", nb_contiguous_white_pixel)
# =============================================================================
            
        return nb_contiguous_white_pixel

def Show_Boxes_And_Explorers(_img,_rotated_box_corners,
                             _explorers):
    fig = plt.figure(figsize=(5,5),dpi=300)
    ax = fig.add_subplot(111)
    ax.imshow(_img)
    
    Show_Plant_Bounding_Boxes(_rotated_box_corners)
    
# =============================================================================
#     for _exp in _explorers:
#         Show_Explorers(_exp, ax)
# =============================================================================

def Show_Plant_Bounding_Boxes(_rotated_box_corners):
    
    nb_rect = len(_rotated_box_corners)
    
    for i in range(nb_rect):
        x_rot = []
        y_rot = []
        for j in range (4):
            x_rot += [_rotated_box_corners[i][j][0]]
            y_rot += [_rotated_box_corners[i][j][1]]
        
        plt.plot(x_rot, y_rot, color='green', linewidth=0.5)

def Show_Explorers(_explorers, _ax):
    
    for _coord in _explorers:
        circle = patches.Circle(_coord,
                        radius = 0.5,
                        edgecolor = None,
                        facecolor = 'orange')
        _ax.add_patch(circle)

def Is_Point_Inside_Rectangle(_p, _box_corners):
    """
    we suppose _all_para is given by the function Get_All_Line_Parameters
    
    To be inside the rectangle, The point has to:
        -be on the right of the SW-NW line '_all_para[0]'
        -be on the left of the SE-NE line '_all_para[2]'
        -be below the NE-NW line '_all_para[1]'
        -be abovethe SW-SE line '_all_para[3]'
    """
    
    _inside = False
    
    if (_box_corners[0][0] !=_box_corners[1][0] and
        _box_corners[1][0] !=_box_corners[2][0]): #tilting rectangle
        _all_para = Get_All_Line_Parameters(_box_corners)
        
        x1 = rec_f_line(_p[1], _all_para[0][0], _all_para[0][1])
        x2 = rec_f_line(_p[1], _all_para[2][0], _all_para[2][1])
        y1 = f_line(_p[0], _all_para[1][0], _all_para[1][1])
        y2 = f_line(_p[0], _all_para[3][0], _all_para[3][1])
        max_y = max(y1, y2)
        min_y = min(y1, y2)
        max_x = max(x1, x2)
        min_x = min(x1, x2)
# =============================================================================
#         print("Tilting")
#         print(_p[0], min_x, max_x, _p[0] > min_x, _p[0] < max_x)
#         print(_p[1], min_y, max_y, _p[1] < min_y, _p[1] > max_y)
# =============================================================================
        
        if (_p[0] > min_x and 
            _p[0] < max_x and
            _p[1] > min_y and 
            _p[1] < max_y):
            
            _inside = True
    else:
        #print("Flat")
        #print(_p, _box_corners)
        all_x = [_box_corners[i][0] for i in range(4)]
        max_x = max(all_x)
        min_x = min(all_x)
        all_y = [_box_corners[i][1] for i in range(4)]
        max_y = max(all_y)
        min_y = min(all_y)
        
        if (_p[0] > min_x and
            _p[0] < max_x and 
            _p[1] > min_y and
            _p[1] < max_y ):
            
            _inside = True
# =============================================================================
#     print( _inside)
# =============================================================================
    return _inside

def Compute_Line_Equation(_p1, _p2):
    x1, y1 = _p1
    x2, y2 = _p2

    assert x1 != x2
    
    a = (y1-y2)/(x1-x2)
    b = y1-a*x1
    
    return (a,b)

def f_line(x,a,b):
    return a*x+b

def rec_f_line(y,a,b):
    return (y-b)/a

def Line_Intersection(_para1, _para2):
    a1, b1 = _para1
    a2, b2 = _para2
    
    assert a1 != a2
    
    x = (b2-b1)/(a1-a2)
    y = (x-b1)/a1
    
    return (x,y)

def Sample_Line(_para, _x_limits, _sample_dividor = 10):
    
    _step = int(np.floor((_x_limits[1] - _x_limits[0])/_sample_dividor))
    
    if (_step < 1):
        _step = 1
    
    return [(_x, int(f_line(_x, _para[0], _para[1]))) for _x in range(
                                                            _x_limits[0]+_step,
                                                            _x_limits[1],
                                                            _step)]

if (__name__ == "__main__"):
    
    root_path = "../Tutorial/"
    nb_fields = 100
    nb_gs = 3
    for i in range (nb_fields):
        for j in range (nb_gs):
            gs_path = root_path+"/Processed/Field_{0}/GrowthStage_{1}".format(i,j)
            Produce_Adjusted_Position_Files(gs_path+"/Dataset",
                                            gs_path+"/Positions",
                                            80,
                                            gs_path+"/RGB",
                                            os.listdir(gs_path+"/RGB"))
