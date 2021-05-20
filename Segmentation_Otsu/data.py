# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 13:36:47 2020

@author:
    Naomie Berda
    Léa Courteille
    Grison William
    Lucas Mathieu
"""

import os
from skimage.util import random_noise
path_scripts = os.path.dirname(os.path.abspath(__file__))
os.chdir(path_scripts)
import otsu as o


import numpy as np 
import matplotlib.pyplot as plt
import cv2
from PIL import Image, ImageFilter


class Data:
    '''
    Classe avec l'ensemble des données chargées
    
        path_images -- string :
            chemin du repertoire d'accès aux images
        name -- string :
            nom de l'image
        image_array -- array :
            tableau des pixels l'image (RGB)
        image_gray -- array :
            tableau des pixels de l'image en noir et blanc
        image_ExG -- array :
            tableau des pixels de l'image convertis en valeur d'ExG
        mask -- array :
            tableau du mask obtenu appliqué à image_ExG
        rang_aligne -- array :
            tableau du mask oriente de tel sorte que les rang de culture soient verticals
    '''
    
    def __init__(self, name, path_images="",
                 _apply_noise = False,
                 _noise_type = "speckle",
                 _noise_var = 0.01,
                 _apply_blur = False,
                 _blur_radius = 2,
                 _img_array_restrictions=None):
        
        self.path_images = path_images
        self.name = name
        self.image_PIL=Image.open(os.path.join(self.path_images,self.name))
        if (_apply_blur):
            self.image_PIL = self.image_PIL.filter(ImageFilter.GaussianBlur(radius = _blur_radius))
        self.image_array =  np.array(self.image_PIL)
        if (_img_array_restrictions != None):
            self.image_array = self.image_array[self.image_array.shape[0]-_img_array_restrictions[0]:,
                                                :_img_array_restrictions[1]]
        self.image_gray = np.array(self.image_PIL.convert('L'))
        
        #plt.imshow(self.image_array)
        
        self._apply_noise = _apply_noise
        self.noise_type = _noise_type
        self.noise_var = _noise_var
    
    def apply_noise(self, _img_arr):
        noise_arr = random_noise(_img_arr,
                                 mode=self.noise_type,
                                 var=self.noise_var, clip = True)
            
        # The above function returns a floating-point image
        # on the range [0, 1], thus we changed it to 'uint8'
        # and from [0,255]        
        return np.array(255*noise_arr, dtype = 'uint8')
                      

    def convertir_ExG(self):
        '''
        convertis image en ExG
        '''
        image = self.image_array
            
        image = np.dot(image[...,:3], [-1, 2, -1])
        
        if (self._apply_noise):
            image = np.array(255*((image+abs(np.min(image)))/(np.max(image+abs(np.min(image))))), dtype = 'uint8')
            image = self.apply_noise(image)
        print("conv_ExG_4", np.min(image), np.max(image))
        #plt.imshow(image)
        return image


    def create_maskExG(self):
        '''
        créer le mask : filtre valeur tel que ExG > (moy(ExG) + 2*std(ExG)) 
        '''
        # masque de detection du vert
        self.image_ExG = self.convertir_ExG()
        
        seuil_min = np.mean(self.image_ExG) + 2*np.std(self.image_ExG)
        mask=np.zeros(self.image_ExG.shape)
        mask = np.where(self.image_ExG<seuil_min, mask, 255)
        self.mask_ExG = mask
    
      
    def convertir_HSV(self):
        """
        retourne l'image en HSV
        """
        #lecture image avec cv2 (image en BGR par défaut)
        image = cv2.imread(os.path.join(self.path_images,self.name))
        #conversion image en RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        return image


    def create_maskHSV(self, sensibilite=20):
        """
        cree un masque HSV en valeur 0/255
        """
        # masque de detection du vert
        self.image_HSV = self.convertir_HSV()
        lower_green = np.array([60 - sensibilite, 0, 0]) 
        upper_green = np.array([60 + sensibilite, 255, 255])
        mask = cv2.inRange(self.image_HSV, lower_green , upper_green)
        self.mask_HSV = mask


        
        
    def create_maskOtsu(self, start_threshold=10):
        """
        cree un masque avec la méthode Otsu en 0/255
        """
        
        if not hasattr(self, "mask_ExG"):
            self.create_maskExG()

        self.mask_Otsu = o.segmentation_otsu(self.image_ExG, start_threshold)
        #conversion en noir et blanc :
        self.mask_Otsu=np.where(self.mask_Otsu<=200, 0, 255)
    
       
    def create_maskfusion(self):
        """
        cree un masque plus conservateur, où sont présents uniquement les points conservés par les 3 filtres précédents
        """
        #charger les filtres ExG, HSV et Otsu
        if not hasattr(self, "mask_Otsu"):
            self.create_maskOtsu()
        if not hasattr(self, "mask_HSV"):
            self.create_maskHSV()
        
        #faire une map des points égaux à 255
        self.mask_fusion=self.mask_ExG+self.mask_HSV+self.mask_Otsu
        self.mask_fusion=np.where(self.mask_fusion==255*3, self.mask_fusion, 0)
        self.mask_fusion=(self.mask_fusion/3).astype(int)
        
    def create_maskunion(self):
        """
        cree un masque plus conservateur, où sont présents les points conservés par chaque filtre 
        """
        #charger les filtres ExG, HSV et Otsu
        if not hasattr(self, "mask_Otsu"):
            self.create_maskOtsu()
        if not hasattr(self, "mask_HSV"):
            self.create_maskHSV()
            
        #faire une map des points égaux à 255
        self.mask_union=self.mask_ExG+self.mask_HSV+self.mask_Otsu
        self.mask_union=np.where(self.mask_union>=255, self.mask_union, 0)
        self.mask_union=np.where(self.mask_union==0, self.mask_union, 255).astype(int)


    def display(self, object_name, *args):
        '''
        object_name :
            image, mask_ExG, mask_HSV, mask_Otsu, image_HSV, image_ExG, mask_fusion
        
        A partir du nom de l'objet à display, l'affiche. Si l'objet n'existe pas, le créée avec les éventuels
        arguments *args
        '''
        
        #Initialisation des objets pour la suite et modif de image_name par convenance        
        fonctions=[self.create_maskExG, self.create_maskHSV, self.create_maskOtsu,
                   self.create_maskExG, self.create_maskHSV, self.create_maskfusion,
                   self.create_maskunion ]
        indices=["mask_ExG", "mask_HSV", "mask_Otsu",
                 "image_HSV", "image_ExG", "mask_fusion",
                 "mask_union"]
        if object_name=="image":
            object_name="image_array"
        #Si object_name n'existe pas dans les attributs de Data, on appelle la fonction correspondante
        if not hasattr(self, object_name):
            print("in")
            indice=indices.index(object_name)
            fonctions[indice](*args)        
            
        #Finalement, on l'affiche
        plt.figure()
        plt.imshow(getattr(self, object_name))
        
        
    def save(self,object_name,file_name,*args,path=None):
        """
        ATTENTION : Si path est utilisé, il doit être spécifié dans la commande comme path="qqch" !
        
        
        object_name : mask_ExG, mask_HSV, mask_Otsu, mask_fusion, mask_union
        
        A partir du nom de l'objet à display, l'affiche. Si l'objet n'existe pas, le créée avec les éventuels
        arguments *args
        """
        fonctions=[self.create_maskExG, self.create_maskHSV, self.create_maskOtsu,
                   self.create_maskfusion, self.create_maskunion]
        indices=["mask_ExG", "mask_HSV", "mask_Otsu", "mask_fusion", "mask_union"]
        
        if not hasattr(self, object_name):
            indice=indices.index(object_name)
            fonctions[indice](*args)            
        _to_save=Image.fromarray(getattr(self, object_name)).convert("RGB")
        
        #Si un chemin est spécifié, on le joint au nom de l'image
        if path!=None:
            name=file_name.split(".")[0]
            file_name=os.path.join(path, name)
        
        #Si le nom donné pour file_name ne finit pas par .jpg, on l'ajoute
        if file_name[-3:]!=".jpg":
            file_name=file_name+".jpg"
        
        #enregistrement
        _to_save.save(file_name, "JPEG")
        
