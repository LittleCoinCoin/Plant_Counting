# -*- coding: utf-8 -*-

import os
import json
import numpy as np
from PIL import Image

import MAS


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
labelled_image = True
    
path_input_root = "../Tutorial"

path_input_raw = path_input_root+"/Data/Labelled/Set3/Processed/Field_0/GrowthStage_0/RGB"
path_input_OTSU = path_input_root+"/Output_General/Set3/Output/Session_{0}/Otsu_R".format(session_number)
path_input_PLANT_FT_PRED = path_input_root+"/Output_General/Set3/Output_FA/Session_{0}/Plant_FT_Predictions".format(session_number)

names_input_raw = os.listdir(path_input_raw)
names_input_OTSU = os.listdir(path_input_OTSU)
names_input_PLANT_FT_PRED = os.listdir(path_input_PLANT_FT_PRED)


# =============================================================================
# Data Collection
# =============================================================================
print("Data Collection...", end = " ")

subset_size = 8

data_input_raw = import_data(path_input_raw,
                             names_input_raw[:subset_size],
                             get_img_array)
data_input_OTSU = import_data(path_input_OTSU,
                              names_input_OTSU[:subset_size],
                              get_img_array)
data_input_PLANT_FT_PRED = import_data(path_input_PLANT_FT_PRED,
                                       names_input_PLANT_FT_PRED[:subset_size],
                                       get_json_file_content)

if (labelled_image):
    path_input_adjusted_position_files = path_input_root+"/Output_General/Set3/Output/Session_{0}/Adjusted_Position_Files".format(session_number)
    names_input_adjusted_position_files = os.listdir(path_input_adjusted_position_files)
    data_adjusted_position_files = import_data(path_input_adjusted_position_files,
                                           names_input_adjusted_position_files[:subset_size],
                                           get_json_file_content)

print("Done")

# =============================================================================
# Simulation Parameters Definition
# =============================================================================
RAs_group_size = 20
RAs_group_steps = 2
Search_Simulation_steps = 50

RALs_fuse_factor = 0.5
RALs_fill_factor = 1.5

_image_index = 0

follow_bool = True
path_output_follow = path_input_root+\
                    "/Output_General/Set3/Output_Meta_Simulation/Session_{3}/Simu_Steps_Pictures/{1}_{2}/Img_{0}".format(
                            _image_index, RAs_group_size, RAs_group_steps, session_number)
simu_name = "Simu_Follow_on_Img{0}".format(_image_index)

print(names_input_OTSU[_image_index])
print(names_input_adjusted_position_files[_image_index])
print(names_input_PLANT_FT_PRED[_image_index])

# =============================================================================
# Simulation Definition
# =============================================================================
print("Simulation Definition:")
MAS_Simulation = MAS.Simulation_MAS(data_input_raw[_image_index],
                                    data_input_PLANT_FT_PRED[_image_index],
                                    data_input_OTSU[_image_index],
                                    RAs_group_size, RAs_group_steps,
                                    RALs_fuse_factor, RALs_fill_factor,
                                    [0,0],
                                    data_adjusted_position_files[_image_index],
                                    follow_bool,
                                    path_output_follow,
                                    simu_name)
MAS_Simulation.Initialize_AD()
MAS_Simulation.Perform_Search_Simulation(Search_Simulation_steps,
                                             _coerced_X=True,
                                             _coerced_Y=False,
                                             _analyse_and_remove_Rows=True,
                                             _edge_exploration = True)

# =============================================================================
# Simulation Analysis
# =============================================================================
print("Computing Scores...", end = " ")
MAS_Simulation.Get_RALs_infos()
MAS_Simulation.Compute_Scores()
print("Done")

print(MAS_Simulation.simu_steps_times)
print("NB Rals =", MAS_Simulation.RALs_recorded_count[-1])
print("TP =", MAS_Simulation.TP)
print("FN =", MAS_Simulation.FN)
print("FP =", MAS_Simulation.FP)
#print(MAS_Simulation.RALs_dict_infos)


# =============================================================================
# MAS_Simulation.Show_Adjusted_And_RALs_positions()
# =============================================================================
MAS_Simulation.Show_nb_RALs()
#MAS_Simulation.Show_RALs_Deicision_Scores()
