# -*- coding: utf-8 -*-
"""
Created on Fri May 29 10:23:23 2020

@author: eliot

The classes are built to contain the method automatically looking for the crops
rows angle.
"""
# =============================================================================
# from sklearn.cluster import DBSCAN
# =============================================================================
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image #, ImageDraw


class CRAD_Voting:
    """
    This class gathers all the angles of the crops rows detected in the images
    thanks to the CRAD class.
    Then, on the hypothesis that all the images have identical orientation,
    we consider that the real angle of the crops rows is the most detected one.
    This is similar to a vote where each LineDetection objects vote for the 
    angle that they detected. We then consider that the angle with the more votes
    is the real one. Therefore we operate the corrections on all the LD objects
    which do not match.
    
    """
    def __init__(self, _AD_objects_list):
        self.AD_objects_List = _AD_objects_list
    
    def Get_Best_Angle(self):
        print("Getting best angle")
        self.dict_angles = {}
        for _AD in self.AD_objects_List:
            try:
                self.dict_angles[int(_AD.angle_min)] += 1
            except KeyError:
                self.dict_angles[int(_AD.angle_min)] = 1
        self.angles_sort = []
        for k,v in self.dict_angles.items():
            self.angles_sort.append([v,k])
        self.angles_sort.sort()
        
        self.best_angle_min = self.angles_sort[-1][1]
    
    def Correct_AD_based_on_best_angle(self):
        print("Correcting LDs based on best angle")
        for _AD in self.AD_objects_List:
            if (_AD.angle_min != self.best_angle_min):
                
                _AD.angle_min = self.best_angle_min
                
                _AD.angle_min_rotation_matrix = _AD.rotation_matrix(np.deg2rad(_AD.angle_min))
        
                _AD.coord_centroid_map_Rot = np.dot(_AD.coord_map,
                                                     _AD.angle_min_rotation_matrix)
                

class CRAD:

    def __init__(self, 
                 img_id,
                _path_Otsu,
                _path_Otsu_R,
                _path_output_angle_score_search,
                _path_output_histogram
               ):
        """
        TO DO
        """
        
        self.img_id = img_id
        
        self.path_Otsu = _path_Otsu
        self.Otsu_img = Image.open(_path_Otsu+"/OTSU_"+self.img_id+".jpg")
        self.Otsu_img_arr = np.array(Image.open(_path_Otsu+"/OTSU_"+self.img_id+".jpg"))
        
        self.path_Otsu_R = _path_Otsu_R
        
        self.path_output_angle_score_search = _path_output_angle_score_search
        self.path_output_histogram = _path_output_histogram
    
    def get_coord_map(self):
        #self.Otsu_img_arr[:,:,0] correspond to the Red canal of the image 
        #but the Otsu image is in black and white so it does not make any
        #diferrence with the other canals.
        #Although, for some reasons, the saved image does not have either black
        #pixels [0 0 0] or white pixels [255 255 255]. Maybe because of the .jpg
        #format?
        #Anyway, we go through the whole thing and change the value to 0 or 255
        #depending on the threshold placed at 200
        
        real_BW_Otsu = np.where(self.Otsu_img_arr > 200, 255, 0)
        
        self.coord_map = np.fliplr(np.transpose(np.nonzero(real_BW_Otsu[:,:,0])))
    
    def display_centroid_map(self):
        plt.clf()
        plt.imshow(self.centroid_map)
    
    def auto_angle2(self):
        """
        Aims to detect the orientation of the crops rows
        """
        print("looking for the angle")
        self.angle_min = 0
        score_min = 1
                
        self.auto_angle_score_plot = []
        angles = np.arange(0,180,1)
        for _a in angles:
            theta = np.radians(_a)
            XY_rot = np.dot(self.coord_map, self.rotation_matrix(theta))
            
            X_rot_ceil = np.ceil(XY_rot[:,0])
            X_rot_ceil_unique = np.unique(X_rot_ceil)
            
            score = np.shape(X_rot_ceil_unique)[0]/abs(np.max(X_rot_ceil)-np.min(X_rot_ceil)+1)
            self.auto_angle_score_plot += [score]
            
            if (score < score_min):
                score_min = score
                self.angle_min = _a
        
        self.angle_min_rotation_matrix = self.rotation_matrix(np.deg2rad(self.angle_min))
        
        self.coord_centroid_map_Rot = np.dot(self.coord_map,
                                             self.angle_min_rotation_matrix)
    
    def rotation_matrix(self, _theta):
        """
        Counter clock wise rotation matrix
        """
        return np.array([[np.cos(_theta), -np.sin(_theta)],
                         [np.sin(_theta),  np.cos(_theta)]])
    
    def get_auto_angle_rotated_Otsu(self):
        self.Otsu_img_rot = self.Otsu_img.rotate(self.angle_min, expand=True)
        self.Otsu_img_rot.save(self.path_Otsu_R+ "/OTSU_R_"+self.img_id+".jpg", "JPEG")
        
        real_BW_Otsu_rot = np.where(np.array(self.Otsu_img_rot) > 200, 255, 0)
        self.Otsu_img_arr_rot = np.fliplr(np.transpose(np.nonzero(real_BW_Otsu_rot[:,:,0])))
        
    def plot_auto_angle_rotation(self, _save = False):
        """
        Plots the cloud points of the image before and after rotation
        
        You must have computed self.angle_min with the self.auto_angle2() method.
        """
        
        plt.figure()
        
        plt.scatter(self.coord_map[:,0],
                    self.coord_map[:,1], s = 0.05, marker="x")
        
        plt.scatter(self.coord_centroid_map_Rot[:,0],
                    self.coord_centroid_map_Rot[:,1], s = 0.05, marker="x")
        
        if (_save):
            plt.savefig(self.path_output_angle_score_search+"/"+"Rotated_"+ \
                        self.img_id+"_"+str(self.angle_min)+".jpg")
            plt.close()
                
    def plot_auto_angle_score(self, _save = False):
        """
        Plots the score as a function of the degres
        
        You must have computed self.angle_min with the self.auto_angle2() method.
        """
        plt.figure()
        angles = np.arange(0,180,1)
        plt.plot(angles, self.auto_angle_score_plot)
        if (_save):
            plt.savefig(self.path_output_angle_score_search+"/"+"AngleScore_"+\
                        self.img_id+".jpg")
            plt.close()
    
    def plot_axis_projection_histogram(self, _array_to_consider,
                                       _axis_array_index,
                                       nb_bins_divider = 1,
                                       _save_preffix = "_"):
        
        axis_rot_ceil = np.sort(np.ceil(_array_to_consider[:,_axis_array_index]))
        
        nb_bins = abs(np.max(axis_rot_ceil)-np.min(axis_rot_ceil)+1)
                
        print(nb_bins)
        plt.figure()
        plt.hist(axis_rot_ceil,
                 bins = int(nb_bins/nb_bins_divider), cumulative=False)
        plt.savefig(self.path_output_histogram+"/"+"Proj{0}_".format(_axis_array_index)+\
                        str(nb_bins_divider)+_save_preffix+self.img_id+".jpg")
        plt.close()
        

