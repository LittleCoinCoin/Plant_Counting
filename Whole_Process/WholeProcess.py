# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 15:55:35 2020

@author: eliot
"""
import os

os.chdir("../Pre_Treatments")
import Process_image_for_FT as PiFT

os.chdir("../Fourier")
import FrequencyAnalysis as FA

os.chdir("../MAS")
import Multi_Images_Simulation_v12bis as MIS

def CompleteProcess(_path_input_rgb_img, _path_output_root,
                    
                    _labelled_images = False, _path_position_files=None,
                    _rows_real_angle=0,
                    
                    _make_unique_folder_per_session=False, _session=1,
                    _do_Otsu=True, _do_AD=True,
                    _save_AD_score_images=False, _save_BSAS_images=False,
                    _bsas_threshold=1,
                    
                    _bin_div_X=2, _bin_div_Y=4,
                    
                    _RAs_group_size=20, _RAs_group_steps=2, _Simulation_steps=50,
                    _RALs_fuse_factor=0.5, _RALs_fill_factor=1.5):
    
    PiFT.All_Pre_Treatment(_path_input_rgb_img,
                      _path_output_root,
                      _path_position_files,
                      _rows_real_angle,
                      _make_unique_folder_per_session, _session,
                      _do_Otsu, _do_AD,
                      _save_AD_score_images, _save_BSAS_images,
                      _bsas_threshold)
    
    FA.All_Fourier_Analysis(_path_output_root,
                         _session,
                         _bin_div_X, _bin_div_Y)
    
    
    MIS.All_Simulations(_path_input_rgb_img,
                    _path_output_root,
                    _labelled_images,
                    _session,
                    _RAs_group_size, _RAs_group_steps, _Simulation_steps,
                    _RALs_fuse_factor, _RALs_fill_factor)

if (__name__=="__main__"):
    CompleteProcess(_path_input_rgb_img="D:/Projet/Unity/HDRP_PGoCF/Datasets/X_Bell5Keys_Z_InversedBell5Keys/virtual_reality",
                    _path_output_root="D:/Projet/Unity/HDRP_PGoCF/Datasets/X_Bell5Keys_Z_InversedBell5Keys/Ouput_General",
                    
                     _labelled_images = True,
                     _path_position_files="D:/Projet/Unity/HDRP_PGoCF/Datasets/X_Bell5Keys_Z_InversedBell5Keys/Position_Files",
                     _rows_real_angle=80,
                    
                    _make_unique_folder_per_session=False, _session=1,
                    _do_Otsu=True, _do_AD=True,
                    _save_AD_score_images=False, _save_BSAS_images=False,
                    _bsas_threshold=1,
                    
                    _bin_div_X=2, _bin_div_Y=4,
                    
                    _RAs_group_size=10, _RAs_group_steps=2, _Simulation_steps=50,
                    _RALs_fuse_factor=0.5, _RALs_fill_factor=1.5)
    