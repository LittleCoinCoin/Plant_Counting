# -*- coding: utf-8 -*-
"""
Created on Sat May 23 11:55:31 2020

@author: eliot
"""

import os
import json
import numpy as np
from PIL import Image

import MAS_v17 as MAS

os.chdir("../Utility")
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

def All_Simulations(_path_input_rgb_img, _path_PreTreatment_and_FA,
                    _labelled_images = False,
                    _session_number=1,
                    _RAs_group_size=20, _RAs_group_steps=2, _Simulation_steps=50,
                    _RALs_fuse_factor=0.5, _RALs_fill_factor=1.5):

    # =============================================================================
    # General Path Definition
    # =============================================================================
    #
    path_input_OTSU = _path_PreTreatment_and_FA+"/Output/Session_"+str(_session_number)+"/Otsu_R"
    path_input_PLANT_FT_PRED = _path_PreTreatment_and_FA+"/Output_FA/Session_"+str(_session_number)+"/Plant_FT_Predictions"
    
    path_output = _path_PreTreatment_and_FA+"/Output_Meta_Simulation/Session_"+str(_session_number)
    gIO.check_make_directory(path_output)
    
    # =============================================================================
    # Files Names Collection
    # =============================================================================
    
    names_input_raw = os.listdir(_path_input_rgb_img)
    #
    names_input_OTSU = os.listdir(path_input_OTSU)
    names_input_PLANT_FT_PRED = os.listdir(path_input_PLANT_FT_PRED)
    
    # =============================================================================
    # Data Collection
    # =============================================================================
    print("Data Collection...", end = " ")
    
    data_input_raw = import_data(_path_input_rgb_img, names_input_raw, get_img_array)
    data_input_OTSU = import_data(path_input_OTSU, names_input_OTSU, get_img_array)
    data_input_PLANT_FT_PRED = import_data(path_input_PLANT_FT_PRED,
                                           names_input_PLANT_FT_PRED,
                                           get_json_file_content)
    
    if (_labelled_images):
        path_input_adjusted_position_files = _path_PreTreatment_and_FA+ \
                                                "/Output/Session_"+str(_session_number)+"/Adjusted_Position_Files"
        names_input_adjusted_position_files = os.listdir(path_input_adjusted_position_files)
        data_adjusted_position_files = import_data(path_input_adjusted_position_files,
                                               names_input_adjusted_position_files,
                                               get_file_lines)
    else:
        data_adjusted_position_files = None
    
    print("Done")
    
    meta_simu_name = "Session_"+str(_session_number)
    
    # =============================================================================
    # Meta Simulation Definition
    # =============================================================================
    
    MetaSimulation = MAS.MetaSimulation(meta_simu_name,
                                        path_output,
                                        names_input_raw,
                                        data_input_raw,
                                        data_input_PLANT_FT_PRED,
                                        data_input_OTSU,
                                        _RAs_group_size,
                                        _RAs_group_steps,
                                        _RALs_fuse_factor,
                                        _RALs_fill_factor,
                                        _simulation_step=_Simulation_steps,
                                        _data_adjusted_position_files=data_adjusted_position_files)
    
    if (_labelled_images):
        
        MetaSimulation.Launch_Meta_Simu_Labels(
                                    _coerced_X = True,
                                    _coerced_Y = False,
                                    _extensive_Init = False,
                                    _new_end_crit = True,
                                    _analyse_and_remove_Rows = True,
                                    _rows_edges_exploration = True)
    
    else:
    
        MetaSimulation.Launch_Meta_Simu_NoLabels(
                                    _coerced_X = True,
                                    _coerced_Y = False,
                                    _extensive_Init = False,
                                    _new_end_crit = True,
                                    _analyse_and_remove_Rows = True,
                                    _rows_edges_exploration = True)
    
if (__name__=="__main__"):

    All_Simulations(_path_input_rgb_img="D:/Projet/Unity/HDRP_PGoCF/Datasets/X_Bell5Keys_Z_InversedBell5Keys/virtual_reality",
                    _path_PreTreatment_and_FA="D:/Projet/Unity/HDRP_PGoCF/Datasets/X_Bell5Keys_Z_InversedBell5Keys/Ouput_General",
                    _labelled_images = True,
                    _session_number=1,
                    _RAs_group_size=10, _RAs_group_steps=2, _Simulation_steps=50,
                    _RALs_fuse_factor=0.5, _RALs_fill_factor=1.5)