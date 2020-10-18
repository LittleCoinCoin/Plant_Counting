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
    
# =============================================================================
# General Path Definition
# =============================================================================
#path of the images 
### TO BE CHANGED AS PER USER NEED
path_root = "D:/Projet/Unity/HDRP_PGoCF"

for session_number in range (1,4):
    unity_date_list = os.listdir(path_root+"/Output/MetaCapture_Session_{0}".format(session_number))
     
    unity_date_counter = 0
    unity_date_total = len(unity_date_list)
    for unity_date in unity_date_list:
        print()
        print("Meta simulation for data set", unity_date_list[unity_date_counter], 
                   "{0}/{1}".format(unity_date_counter+1, unity_date_total))
        
        path_input_raw = path_root+"/Datasets/MetaCapture_Session_{0}".format(session_number)+\
                        "/"+unity_date+"/virtual_reality"
        path_input_adjusted_position_files = path_root+"/Output_FT/MetaCapture_Session_{0}".format(session_number)+\
                                            "/"+unity_date+\
                                            "/Adjusted_Position_Files"
        path_input_OTSU = path_root+"/Output/MetaCapture_Session_{0}".format(session_number)+\
                        "/"+unity_date+"/Otsu_R"
        path_input_PLANT_FT_PRED = path_root+"/Output_FT/MetaCapture_Session_{0}".format(session_number)+\
                                    "/"+unity_date + \
                                    "/Plant_FT_Predictions"
        path_output = path_root+"/Output_Meta_Simulation"+ \
                      "/MetaCapture_Session_{0}".format(session_number)+ \
                      "/" + unity_date 
        gIO.check_make_directory(path_output)
        
        # =============================================================================
        # Files Names Collection
        # =============================================================================
        
        names_input_raw = os.listdir(path_input_raw)
        names_input_adjusted_position_files = os.listdir(path_input_adjusted_position_files)
        names_input_OTSU = os.listdir(path_input_OTSU)
        names_input_PLANT_FT_PRED = os.listdir(path_input_PLANT_FT_PRED)
        
        # =============================================================================
        # Data Collection
        # =============================================================================
        print("Data Collection...", end = " ")
        
        data_input_raw = import_data(path_input_raw, names_input_raw, get_img_array)
        data_adjusted_position_files = import_data(path_input_adjusted_position_files,
                                                   names_input_adjusted_position_files,
                                                   get_file_lines)
        data_input_OTSU = import_data(path_input_OTSU, names_input_OTSU, get_img_array)
        data_input_PLANT_FT_PRED = import_data(path_input_PLANT_FT_PRED,
                                               names_input_PLANT_FT_PRED,
                                               get_json_file_content)
        
        print("Done")
        
        # =============================================================================
        # Simulation Parameters Definition
        # =============================================================================
        RAs_group_size = 20
        RAs_group_steps = 2
        Simulation_steps = 50
        
        RALs_fuse_factor = 0.5
        RALs_fill_factor = 1.5
        
        meta_simu_name = unity_date
        
        # =============================================================================
        # Meta Simulation Definition
        # =============================================================================

        nEC = [True]
        for _nEC in nEC:
            
            MetaSimulation = MAS.MetaSimulation(meta_simu_name,
                                                path_output,
                                                names_input_raw,
                                                data_input_raw,
                                                data_input_PLANT_FT_PRED,
                                                data_input_OTSU,
                                                RAs_group_size,
                                                RAs_group_steps,
                                                RALs_fuse_factor,
                                                RALs_fill_factor,
                                                _simulation_step=Simulation_steps,
                                                _data_adjusted_position_files=data_adjusted_position_files)
            
            MetaSimulation.Launch_Meta_Simu(
                                        _coerced_X = True,
                                        _coerced_Y = False,
                                        _extensive_Init = False,
                                        _new_end_crit = _nEC,
                                        _analyse_and_remove_Rows = True,
                                        _rows_edges_exploration = True)

# =============================================================================
#             MetaSimulation.Get_Field_Assembling_Offsets()
# =============================================================================
        
        unity_date_counter += 1