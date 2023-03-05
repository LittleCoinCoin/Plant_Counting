# -*- coding: utf-8 -*-

import os
import sys

import MAS

sys.path.append(os.path.abspath("../Utility"))
import general_IO as gIO
    
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

names_input_raw = gIO.listdir_nohidden(path_input_raw)
names_input_OTSU = gIO.listdir_nohidden(path_input_OTSU)
names_input_PLANT_FT_PRED = gIO.listdir_nohidden(path_input_PLANT_FT_PRED)


# =============================================================================
# Data Collection
# =============================================================================
print("Data Collection...", end = " ")

subset_size = 8

data_input_raw = gIO.multi_read(path_input_raw,
                                names_input_raw[:subset_size],
                                gIO.read_img)
data_input_OTSU = gIO.multi_read(path_input_OTSU,
                                 names_input_OTSU[:subset_size],
                                 gIO.read_img)
data_input_PLANT_FT_PRED = gIO.multi_read(path_input_PLANT_FT_PRED,
                                          names_input_PLANT_FT_PRED[:subset_size],
                                          gIO.read_json)

if (labelled_image):
    path_input_adjusted_position_files = path_input_root+"/Output_General/Set3/Output/Session_{0}/Adjusted_Position_Files".format(session_number)
    names_input_adjusted_position_files = gIO.listdir_nohidden(path_input_adjusted_position_files)
    data_adjusted_position_files = gIO.multi_read(path_input_adjusted_position_files,
                                                  names_input_adjusted_position_files[:subset_size],
                                                  gIO.read_json)

print("Done")

# =============================================================================
# Simulation Parameters Definition
# =============================================================================

# Multi-Agents System
RAs_group_size = 20
RAs_group_steps = 2
Search_Simulation_steps = 1

RALs_fuse_factor = 0.5
RALs_fill_factor = 1.5

# The index of the image you want to analyze among the imported data
_image_index = 0

# Save images to visualize every step of the simulation.
follow_bool = True
# Whether you want to show the positions of the labelled plants. Set to True
# if you want to see them. False, otherwise. This only has an effect if you
# provide labelled images and if "labelled_image" at the beginning of this
# script is also set to True.
show_labelled_plant_positions = True
path_output_follow = path_input_root+\
                    "/Output_General/Set3/Output_Meta_Simulation/Session_{3}/Simu_Steps_Pictures/{1}_{2}/Img_{0}".format(
                            _image_index, RAs_group_size, RAs_group_steps, session_number)
simu_name = "Simu_Follow_on_Img{0}".format(_image_index)

print("OTSU input:", names_input_OTSU[_image_index])
print("Plant Fourier Transform Predictions input:", names_input_PLANT_FT_PRED[_image_index])
if (labelled_image):
    print("Labelled Plants Adjusted Positions input:", names_input_adjusted_position_files[_image_index])

# =============================================================================
# Simulation Definition
# =============================================================================
print("Simulation Definition:")

if (labelled_image):
    MAS_Simulation = MAS.Simulation_MAS(data_input_raw[_image_index],
                                        data_input_PLANT_FT_PRED[_image_index],
                                        data_input_OTSU[_image_index],
                                        RAs_group_size, RAs_group_steps,
                                        RALs_fuse_factor, RALs_fill_factor,
                                        [0,0],
                                        data_adjusted_position_files[_image_index],
                                        follow_bool,
                                        show_labelled_plant_positions,
                                        path_output_follow,
                                        simu_name)
else:
    MAS_Simulation = MAS.Simulation_MAS(data_input_raw[_image_index],
                                        data_input_PLANT_FT_PRED[_image_index],
                                        data_input_OTSU[_image_index],
                                        RAs_group_size, RAs_group_steps,
                                        RALs_fuse_factor, RALs_fill_factor,
                                        [0,0],
                                        None,
                                        follow_bool,
                                        False,
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
if (labelled_image):
    print("Computing Scores...", end = " ")
    MAS_Simulation.Get_RALs_infos()
    MAS_Simulation.Compute_Scores()
    print("Done")

print("Simulation steps timings =", MAS_Simulation.simu_steps_times)
print("NB Rals =", MAS_Simulation.RALs_recorded_count[-1])

if (labelled_image):
    print("TP =", MAS_Simulation.TP)
    print("FN =", MAS_Simulation.FN)
    print("FP =", MAS_Simulation.FP)


# =============================================================================
# MAS_Simulation.Show_Adjusted_And_RALs_positions()
# =============================================================================
MAS_Simulation.Show_nb_RALs()
#MAS_Simulation.Show_RALs_Deicision_Scores()
