# -*- coding: utf-8 -*-
"""
Created on Sat Jan 18 09:52:40 2020

@author: Le groupe tournesol

Ce script permet l'obtention d'une carte des centroïdes des rangs, à partir d'une image
segmentée (cultures en blanc, le reste en noir), via l'algorithme de clustering séquentiel
BSAS (des fonctions du script bsas_functions.py sont appelées).
Cette étape est, en cas de recouvrement important, nécessaire pour que la détection de lignes
via l'algorithme de Hough donne des résultats satisfaisants.

"""

#source code (modified)
from bsas_functions import bsas

#other libraries
import os
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image



class BSAS_Process:

    def __init__(self, path_input_img, img_id, _path_output_txt):#_img_array,
        """
            - img: segmented image (only a few pixel values)
            --> ex: image obtained through ExG or Otsu segmentation (using the latter is recommended)
        """
                
        self.img_array = self.get_img_array(os.path.join(path_input_img, img_id))
        self.img_array = np.where(self.img_array > 200, 255, 0)
        
        self.img_id = img_id

        self.path_output_txt = _path_output_txt

    @staticmethod
    def get_img_array(path_img):
        img = Image.open(path_img)
        original_img_array = np.array(img)
        return original_img_array

    def set_BSAS_parameters(self, _threshold = None):
        """
        This function allows the user to help setting the parameters of the BSAS algorithm,
        which are:

        - max_clusters: maximum number of clusters which can be formed on a line
        --> should be big, so that the algorithm chooses the appropriate
        number of clusters itself without any constraint.
        Hence the default setting at 10000.

        - threshold: if the distance between two pixels is superior
        to this threshold, a new cluster is created.
        CRITICAL PARAMETER, should be set by the user.
        """

        self.max_clusters = 10000
        if (_threshold == None):
            plt.imshow(self.img)
            print ("Please click 2 points to indicate the distance between two rows.\n",
                   "This distance should be underestimated.")
            x = plt.ginput(2)
            self.threshold = abs(x[0][0]-x[1][0])
        else:
            self.threshold = _threshold
            
        #print(self.threshold)

    def line_BSAS(self, line_id):
        """
        This function conducts a clustering of white pixels on a given line of
        an image array.
        Inputs:
            - line_id: position of the line in the image array

        """

        sample = []
        line_centroids = []

        for j in range(np.shape(self.img_array)[1]):
            #print(self.img_array[line_id,j][0])
            if self.img_array[line_id,j][0]==255: #only white pixels are clustered
                #print("Add sample")
                sample.append([line_id,j])

        # If white pixels have been found, they are clustered through the BSAS algorithm
        if len(sample)>0:
            bsas_instance = bsas(sample, self.max_clusters, self.threshold)
            bsas_instance.process()
            line_centroids = bsas_instance.get_representatives()

        #list of all the centroid coordinates
        return line_centroids
    
    def line_BSAS2(self, line_id):
        #sample = []
        line_centroids = []
        
        
        pixel_index = 0
        while pixel_index < self.img_array.shape[1]:
            
            if (self.img_array[line_id, pixel_index][0]==255):
                new_clust = [pixel_index]
                clust_pixel_index = pixel_index+1
                nb_black_pixels = 0
                nb_pixel_in_clust = 0
                while clust_pixel_index < self.img_array.shape[1] and nb_black_pixels < self.threshold:
                    if (self.img_array[line_id, clust_pixel_index][0]==255):
                        new_clust += [clust_pixel_index]
                        nb_pixel_in_clust += 1
                    else:
                        nb_black_pixels += 1
                        
                    clust_pixel_index += 1
                
                pixel_index = clust_pixel_index
                
                if (nb_pixel_in_clust > 1):
                    mean_clust = np.ceil(np.mean(new_clust))
                    
                    if (mean_clust > self.img_array.shape[1]):
                        mean_clust -= 1
                    line_centroids.append([line_id, mean_clust])
                
            else:
                pixel_index += 1
        
        return line_centroids

    def col_BSAS2(self, col_id):
        #sample = []
        line_centroids = []
                
        pixel_index = 0
        while pixel_index < self.img_array.shape[0]:
            
            if (self.img_array[pixel_index, col_id][0]==255):
                new_clust = [pixel_index]
                clust_pixel_index = pixel_index+1
                nb_black_pixels = 0
                nb_pixel_in_clust = 0
                while clust_pixel_index < self.img_array.shape[0] and nb_black_pixels < self.threshold:
                    if (self.img_array[clust_pixel_index, col_id][0]==255):
                        new_clust += [clust_pixel_index]
                        nb_pixel_in_clust += 1
                    else:
                        nb_black_pixels += 1
                        
                    clust_pixel_index += 1
                
                pixel_index = clust_pixel_index
                
                if (nb_pixel_in_clust > 1):
                    mean_clust = np.ceil(np.mean(new_clust))
                    
                    if (mean_clust > self.img_array.shape[0]):
                        mean_clust -= 1
                    line_centroids.append([mean_clust, col_id])
                
            else:
                pixel_index += 1
        
        return line_centroids

    def img_BSAS(self):
        """
        This function applies the BSAS algorithm on all lines of an image.
        
        _direction (int):
            controls whether BSAS will be applied horizontally (=0) or vertically
            (=1)
        """

        img_centroids = []  #contains all the cluster centers found with the BSAS algorithm on the img
        
        #print("Computing centroids for image:", self.img_id, end="... ")
        if (self.direction == 0):
            for i in range(np.shape(self.img_array)[0]):#for each line of pixels
                #centroids found with self.line_BSAS are added to the global list
                #print(self.line_BSAS(i))
                #img_centroids.append(self.line_BSAS(i))
                img_centroids.append(self.line_BSAS2(i))
        elif(self.direction == 1):
            for i in range(np.shape(self.img_array)[1]):#for each column of pixels
                #centroids found with self.line_BSAS are added to the global list
                #print(self.line_BSAS(i))
                #img_centroids.append(self.line_BSAS(i))
                img_centroids.append(self.col_BSAS2(i))
            
            
        self.img_centroids = img_centroids
        print("Done")
        #print(self.img_centroids)

    def save_centroid_coordinates(self):
        """
        This function saves all the centroid coordinates in a text file, which can be
        used later on to recreate the BSASmap.
        The text file is of the form: h1,w1;h2,w2...

        """
        name = (self.img_id).split('.')[0]
        file = open(self.path_output_txt+"/"+str(name)+'_bsas.txt',"w")
        #a txt file named after the image is created
        file.write(str(np.shape(self.img_array)[0])+'*'+str(np.shape(self.img_array)[1])+'\n')
        for k in range(np.shape(self.img_array)[self.direction]): #for each line
            line_centroids = self.img_centroids[k]
            for centroid in line_centroids:
                [h, w] = centroid
                file.write(str(int(h))+','+str(int(w))+'\n')
                
        #gIO.writer(self.path_output_txt, str(name)+'_bsas.txt', self.img_centroids, True, False)
        file.close()

    def get_BSASmap(self):
        """
        This function generates the black&white image of the "row skeletons".
        This image will be given as an input to the line_detection_script.

        """
        #BSAS map is initialized as a black background, on which the centroids
        #will appear as white spots

        BSAS_map = np.zeros_like(self.img_array, dtype = "uint8")

        for k in range(np.shape(self.img_array)[self.direction]): #for each line
            line_centroids = self.img_centroids[k]
            for [h,w] in line_centroids:
                BSAS_map[int(h),int(w)]=255 #the pixel is set to white
                    

        self.BSAS_map = Image.fromarray(BSAS_map).convert('L')


    def display_BSASmap(self):
        self.BSAS_map.show()

    def save_BSASmap(self, output_path_img, output_format = 'JPEG'):
        if not hasattr(self, "BSAS_map"):
            self.get_BSASmap()
        self.BSAS_map.save(output_path_img + "/" +self.img_id,output_format)

    def full_process(self, _direction = 0, display = True, _rows_threshold = None):
        """
        This function manages the whole process of BSAS implementation and
        visualisation (optional, if display == True)
        
        _direction (int):
            controls whether BSAS will be applied horizontally (=0) or vertically
            (=1)
        """
        self.direction = _direction
        
        self.set_BSAS_parameters(_rows_threshold)
        self.img_BSAS()
        self.save_centroid_coordinates()

        if display:
            self.get_BSASmap()
            self.display_BSASmap()
            #the function save can be added here


if __name__ == '__main__':

    path_input_img = 'C:/Users/court/Documents/APT/3A/projet_fil_rouge/images_segmentees/Otsu/DJI_0031_1x1.jpg'
    img_id =  'DJI_0031_1x1'
    path_output_txt = 'C:/Users/court/Documents/APT/3A/projet_fil_rouge/final/tests/'

    bsp1 = BSAS_Process(path_input_img, img_id, path_output_txt)
    bsp1.full_process(False)