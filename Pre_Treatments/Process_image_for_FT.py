# -*- coding: utf-8 -*-
"""
Created on Sat May 23 11:55:31 2020

@author: eliot

goals:
    - Performs the pre-treatments on the images
    - Applies the Otsu Segmentation to transform and RGB image to an White and 
    Black image. The White pixel should correspond to plants.
    - Automatically adjust the rotation of the images in order for the crops rows
    to be colinear with the Y axis.

variables the user can change:
    - make_unique_folder_per_session (bool): If set to True the results generated
    are always stored in different folders everytime the script is executed. If
    set to False, the user can specify a session folder; in that case the results
    might be overwritten.
    
    - session_number (int, optional if "make_unique_folder_per_session" is set
    to True): Should only be used when "make_unique_folder_per_session" is set
    to False. In that case, the user should specify the value to create specific
    directory in which the results are stored.
    
    - do_Otsu (bool): Controls whether the Otsu segmentation should be performed
    
    - do_AD (bool): Controls whether the crops rows Angle Detection should be
    performed
    
    - save_AD_score_images (bool): Controls whether we save a copy of plot of
    the rotation score. The rotation score is used to detect the angle of the
    crops rows. We want the angle with the minimum score value.
    
    - bsas_threshold (int, min = 1): threshold for the inter cluster distance
    in the BSAS processus. A value of X means that a new cluster will be formed
    when there are X black pixels or more separating two white pixels. For reminder
    the BSAS processus is used to compute the skeletton of the crops
    
    - save_BSAS_images (bool): controls whether we save the image resulting of
    the BSAS procesusus
    
    - path_input (string): directory of the raw RGB images of the crop field
     
    - path_output_root (string): root directory from where the results will
    be saved. We recommend the user do not change any other "path_output_XXX".
    If so, the correspoding variables will have to changed also in other scrips
    managing the FrequencyAnalysis and the Multi Agent System. 

"""

import os

os.chdir("../Utility")
import general_IO as gIO

os.chdir("../Segmentation_Otsu")
import data

os.chdir("../BSAS")
import bsas

os.chdir("../Crops_Rows_Angle_Detection")
import CRAD


def All_Pre_Treatment(_path_input_rgb_img, _path_output_root,
                      _make_unique_folder_per_session=True, _session=1,
                      _do_Otsu=True, _do_AD=True,
                      _save_AD_score_images=False, _save_BSAS_images=False,
                      _bsas_threshold=1):
    
    #Creates new Output folders every time the process is launched
    gIO.check_make_directory(_path_output_root)
    session_number=_session
    if (_make_unique_folder_per_session):
        while (os.path.exists(_path_output_root+"/Output/Session_{0}".format(session_number))):
            session_number += 1
    path_output = _path_output_root+"/Output/Session_{0}".format(session_number)
    
# =============================================================================
# Images Definition
# =============================================================================
    list_images = os.listdir(_path_input_rgb_img)
    list_images_id = [img_name.split('.')[0] for img_name in list_images]
    nb_images = len(list_images)
    
# =============================================================================
# Segmentation Otsu
# Aim to detect the zone that likely contains target plants on the image
# =============================================================================
    #Output path for Otsu process
    path_output_Otsu = path_output + "/Otsu"
    path_output_Otsu_R = path_output + "/Otsu_R"
    gIO.check_make_directory(path_output_Otsu)
    gIO.check_make_directory(path_output_Otsu_R)
    if _do_Otsu:
        for i in range(nb_images):
            print()
            print ("Processing Otsu mask for image", list_images[i], "{0}/{1}".format(i+1, nb_images))
            image = data.Data(list_images[i], _path_input_rgb_img)
            image.save("mask_Otsu", "OTSU_"+list_images[i], path = path_output_Otsu)
    
# =============================================================================
# Angle Detection (AD)
# Aims to identify the correct angle to straighten the images vertically
# =============================================================================
    path_output_ADp = path_output + "/ADp" + "/" + str(_bsas_threshold)
    path_output_ADp_angle_search_score = path_output_ADp + "/Output_AngleScore"
    path_output_ADp_Images = path_output_ADp + "/Output_Images"
    
    gIO.check_make_directory(path_output_ADp_angle_search_score)
    gIO.check_make_directory(path_output_ADp_Images)
    
    #We apply BSAS procedure by default on the adjusted images
    path_output_BSAS_R = path_output+"/BSAS"+ "/" + str(_bsas_threshold)+"_R"
    path_output_BSAS_txt_R_0 = path_output_BSAS_R+"/Output_Positions"+"/direction_0"
    path_output_BSAS_images_R_0 = path_output_BSAS_R+"/Output_Images"+"/_direction_0"
    gIO.check_make_directory(path_output_BSAS_txt_R_0)
    gIO.check_make_directory(path_output_BSAS_images_R_0)
    
    path_output_BSAS_txt_R_1 = path_output_BSAS_R+"/Output_Positions"+"/direction_1"
    path_output_BSAS_images_R_1 = path_output_BSAS_R+"/Output_Images"+"/_direction_1"
    gIO.check_make_directory(path_output_BSAS_txt_R_1)
    gIO.check_make_directory(path_output_BSAS_images_R_1)
    
    path_output_BSAS_txt_R = [path_output_BSAS_txt_R_0, path_output_BSAS_txt_R_1]
    path_output_BSAS_images_R = [path_output_BSAS_images_R_0, path_output_BSAS_images_R_1]
    
    if _do_AD:
        AD_object_list = []
        for i in range(nb_images):
            print()
            print ("Angle Detection process for image", list_images[i], "{0}/{1}".format(i+1, nb_images))
            
            _AD = CRAD.CRAD(
                           list_images_id[i],
                           path_output_Otsu,
                           path_output_Otsu_R,
                           path_output_ADp_angle_search_score,
                           path_output_ADp_Images)
            
            AD_object_list.append(_AD)
            
            _AD.get_coord_map()
            
            _AD.auto_angle2()
            
            if (_save_AD_score_images):
                _AD.plot_auto_angle_score(_save = True)
        
        
        AD_voting = CRAD.CRAD_Voting(AD_object_list)
        AD_voting.Get_Best_Angle()
        print("The best angle seems to be:", AD_voting.best_angle_min)
        AD_voting.Correct_AD_based_on_best_angle()
        
        i=0
        for _AD in AD_voting.AD_objects_List:
    
            _AD.get_auto_angle_rotated_Otsu()
            
            print()
            
            for k in range (2):
                print ("BSAS process in direction", k,
                       "for image", list_images[i], "{0}/{1}".format(i+1, nb_images))
                bsp1 = bsas.BSAS_Process(path_output_Otsu_R,
                                         "OTSU_R_"+list_images_id[i]+".jpg",
                                         path_output_BSAS_txt_R[k])
                bsp1.full_process(k, False, _bsas_threshold)
                if (_save_BSAS_images):
                    bsp1.save_BSASmap(path_output_BSAS_images_R[k])
            i+=1

if (__name__=="__main__"):
    
    All_Pre_Treatment(_path_input_rgb_img="../Tutorial/Data/Non-Labelled/Set1",
                      _path_output_root="../Tutorial/Output_General/Set1",
                      _make_unique_folder_per_session=True, _session=1,
                      _do_Otsu=True, _do_AD=True,
                      _save_AD_score_images=False, _save_BSAS_images=False,
                      _bsas_threshold=1)
