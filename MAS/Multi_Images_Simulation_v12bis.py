# -*- coding: utf-8 -*-
"""
Created on Sat May 23 11:55:31 2020

@author: eliot
"""

import os
import json
import numpy as np
from PIL import Image

import MAS_v16 as MAS

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
                    _session_number=1,
                    _RAs_group_size=20, _RAs_group_steps=2, _Simulation_steps=50,
                    _RALs_fuse_factor=0.5, _RALs_fill_factor=1.5):

    # =============================================================================
    # General Path Definition
    # =============================================================================
    #path_input_adjusted_position_files = path_root+"/Output_FT///Adjusted_Position_Files"
    path_input_OTSU = _path_PreTreatment_and_FA+"/Output/Session_"+str(_session_number)+"/Otsu_R"
    path_input_PLANT_FT_PRED = _path_PreTreatment_and_FA+"/Output_FA/Session_"+str(_session_number)+"/Plant_FT_Predictions"
    
    path_output = _path_PreTreatment_and_FA+"/Output_Meta_Simulation/Session_"+str(_session_number)
    gIO.check_make_directory(path_output)
    
    # =============================================================================
    # Files Names Collection
    # =============================================================================
    
    names_input_raw = os.listdir(_path_input_rgb_img)
    #names_input_adjusted_position_files = os.listdir(path_input_adjusted_position_files)
    names_input_OTSU = os.listdir(path_input_OTSU)
    names_input_PLANT_FT_PRED = os.listdir(path_input_PLANT_FT_PRED)
    
    # =============================================================================
    # Data Collection
    # =============================================================================
    print("Data Collection...", end = " ")
    
    data_input_raw = import_data(_path_input_rgb_img, names_input_raw, get_img_array)
    #data_adjusted_position_files = import_data(path_input_adjusted_position_files,
    #                                           names_input_adjusted_position_files,
    #                                           get_file_lines)
    data_adjusted_position_files = None
    data_input_OTSU = import_data(path_input_OTSU, names_input_OTSU, get_img_array)
    data_input_PLANT_FT_PRED = import_data(path_input_PLANT_FT_PRED,
                                           names_input_PLANT_FT_PRED,
                                           get_json_file_content)
    
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
    
    MetaSimulation.Launch_Meta_Simu_NoLabels(
                                _coerced_X = True,
                                _coerced_Y = False,
                                _extensive_Init = False,
                                _new_end_crit = True,
                                _analyse_and_remove_Rows = True,
                                _rows_edges_exploration = True)
    
if (__name__=="__main__"):

    All_Simulations(_path_input_rgb_img="../Tutorial/Data/Non-Labelled/Set1",
                    _path_PreTreatment_and_FA="../Tutorial/Output_General/Set1",
                    _session_number=1,
                    _RAs_group_size=20, _RAs_group_steps=2, _Simulation_steps=50,
                    _RALs_fuse_factor=0.5, _RALs_fill_factor=1.5)