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
                    
                    _growth_monitoring = False,
                    _path_MAS_initialize = None,
                    
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
    
    if (not _growth_monitoring):
        FA.All_Fourier_Analysis(_path_output_root,
                             _session,
                             _bin_div_X, _bin_div_Y)
    
    
    MIS.All_Simulations(_path_input_rgb_img,
                    _path_output_root,
                    _labelled_images,
                    _session, _growth_monitoring,_path_MAS_initialize,
                    _RAs_group_size, _RAs_group_steps, _Simulation_steps,
                    _RALs_fuse_factor, _RALs_fill_factor)

def Growth_Monitoring(
                    _path_monitoring_root,
        
                    _folder_input_rgb_img = "",
                    _folder_output_root = "",
                    
                    _labelled_images = False,
                    _folder_position_files=None,
                    _rows_real_angle=0,
                    
                    _make_unique_folder_per_session=False, _session=1,
                    _do_Otsu=True, _do_AD=True,
                    _save_AD_score_images=False, _save_BSAS_images=False,
                    _bsas_threshold=1,
                    
                    _bin_div_X=2, _bin_div_Y=4,
                    
                    _RAs_group_size=20, _RAs_group_steps=2, _Simulation_steps=50,
                    _RALs_fuse_factor=0.5, _RALs_fill_factor=1.5):
    
    monitoring_folders = os.listdir(_path_monitoring_root)
    print(monitoring_folders)
    
    CompleteProcess(_path_input_rgb_img=_path_monitoring_root+"/"+monitoring_folders[0]+_folder_input_rgb_img,
                    _path_output_root=_path_monitoring_root+"/"+monitoring_folders[0]+_folder_output_root,
                    
                    _labelled_images = True,
                    _path_position_files=_path_monitoring_root+"/"+monitoring_folders[0]+_folder_position_files,
                    _rows_real_angle=80,
                    
                    _growth_monitoring = False,
                    
                    _make_unique_folder_per_session=False, _session=1,
                    _do_Otsu=True, _do_AD=True,
                    _save_AD_score_images=False, _save_BSAS_images=False,
                    _bsas_threshold=1,
                    
                    _bin_div_X=2, _bin_div_Y=4,
                    
                    _RAs_group_size=20, _RAs_group_steps=5, _Simulation_steps=50,
                    _RALs_fuse_factor=0.5, _RALs_fill_factor=1.5)
    
    nb_monitoring_steps = len(monitoring_folders)
    for i in range (1,nb_monitoring_steps):
        CompleteProcess(_path_input_rgb_img=_path_monitoring_root+"/"+monitoring_folders[i]+_folder_input_rgb_img,
                        _path_output_root=_path_monitoring_root+"/"+monitoring_folders[i]+_folder_output_root,
                        
                        _labelled_images = True,
                        _path_position_files=_path_monitoring_root+"/"+monitoring_folders[i]+_folder_position_files,
                        _rows_real_angle=80,
                        
                        _growth_monitoring = True,
                        _path_MAS_initialize = _path_monitoring_root+"/"+monitoring_folders[i-1]+_folder_output_root+\
                                                    "/Output_Meta_Simulation/Session_{0}/RALs_NestedPositions".format(_session),
                        
                        _make_unique_folder_per_session=False, _session=1,
                        _do_Otsu=True, _do_AD=True,
                        _save_AD_score_images=False, _save_BSAS_images=False,
                        _bsas_threshold=1,
                        
                        _bin_div_X=2, _bin_div_Y=4,
                        
                        _RAs_group_size=30, _RAs_group_steps=10, _Simulation_steps=50,
                        _RALs_fuse_factor=0.5, _RALs_fill_factor=1.5)
    

if (__name__=="__main__"):
# =============================================================================
#     CompleteProcess(_path_input_rgb_img="D:/Projet/Unity/HDRP_PGoCF/Datasets/Monitoring/Series_3/2021_1_21_10_53_49/virtual_reality",
#                     _path_output_root="D:/Projet/Unity/HDRP_PGoCF/Datasets/Monitoring/Series_3/2021_1_21_10_53_49/Ouput_General",
#                     
#                     _labelled_images = True,
#                     _path_position_files="D:/Projet/Unity/HDRP_PGoCF/Datasets/Monitoring/Series_3/2021_1_21_10_53_49/Position_Files",
#                     _rows_real_angle=80,
#                     
#                     _growth_monitoring = False,
#                     
#                     _make_unique_folder_per_session=False, _session=1,
#                     _do_Otsu=False, _do_AD=False,
#                     _save_AD_score_images=False, _save_BSAS_images=False,
#                     _bsas_threshold=1,
#                     
#                     _bin_div_X=2, _bin_div_Y=4,
#                     
#                     _RAs_group_size=50, _RAs_group_steps=10, _Simulation_steps=50,
#                     _RALs_fuse_factor=0.5, _RALs_fill_factor=1.5)
# =============================================================================
    Growth_Monitoring(
                    
                    _path_monitoring_root = "D:/Projet/Unity/HDRP_PGoCF/Datasets/Monitoring/Series_6",
            
                    _folder_input_rgb_img="/virtual_reality",
                    _folder_output_root="/Ouput_General",
                    
                    _labelled_images = True,
                    _folder_position_files="/Position_Files",
                    _rows_real_angle=80,
                    
                    _make_unique_folder_per_session=False, _session=1,
                    _do_Otsu=True, _do_AD=True,
                    _save_AD_score_images=True, _save_BSAS_images=False,
                    _bsas_threshold=1,
                    
                    _bin_div_X=2, _bin_div_Y=4,
                    
                    _RAs_group_size=50, _RAs_group_steps=10, _Simulation_steps=50,
                    _RALs_fuse_factor=0.5, _RALs_fill_factor=1.5)
