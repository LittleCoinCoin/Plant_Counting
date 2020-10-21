# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 14:45:35 2020
@author: court
L'algorithme d'Otsu permet une segmentation plantes-sol adaptative: le seuil choisi par l'algo est
celui qui minimise la variance intra-classe/maximise la variance inter-classe
/_\Paramètre important/_\ th_black : seuil déterminant le 1er niveau de segmentation: les pixels
de valeur<th_black correspondent au sol, et ceux de valeur>th_black correspondent aux plantes (adventices+tournesols)
"""

#==============================================================================
##Imports
#==============================================================================

import math
import numpy as np



#==============================================================================
##Fonctions
#==============================================================================

def Hist(img, th_black):
    """
    Cette fonction génère l'histogramme d'une image.
    """
    row, col = img.shape
    y = np.zeros(256)
    y_sol = np.zeros(256)
    for i in range(0,row):
        for j in range(0,col):#on parcourt l'image
            if img[i,j]>th_black: #si le pixel n'est pas dans la partie de l'histogramme qu'on ignore (ie <th_black)
                y[img[i,j]] += 1 #on compte un pixel de plus d'une couleur donnée
            else:
                y_sol[img[i,j]] += 1

    return y



def countPixel(h):
    """compte le nb de pixels décrits par un histogramme h"""
    cnt = 0
    for i in range(0, len(h)):
          cnt += h[i]
    return cnt


def weight(a, b, h):
    """somme des pixels décrits par le sous-histogramme allant de a à b
    ie nombre total de pixels du sous-histogramme allant de a à b"""
    w = 0
    for i in range(a, b):
        w += h[i]
    return w #w est la somme des h[i]


def mean(a, b, h):
    """somme des i*w_i/w
    on obtient la couleur moyenne de la classe"""
    m = 0
    w = weight(a, b, h)
    for i in range(a, b):
        m += h[i] * i
    return m/float(w)


def variance(a, b, h):
    """
    à partir de m et w,
    calcule la variance intra-classe d'une partie de l'histogramme définie par a et b
    """
    v = 0
    m = mean(a, b, h)
    w = weight(a, b, h)
    for i in range(a, b):
        v += ((i - m) **2) * h[i] #somme des i-l'espérance au carré * w_i
    v /= w
    return v


def threshold(h, th_black):
    """
    Cette fonction explore tous les seuils de segmentation possibles.
    Il stocke pour chacun de ces seuils les valeurs de lambda obtenues dans un dictionnaire.
    Ce dictionnaire servira à trouver le meilleur seuil de segmentation.
    """
    #Initialisation des dictionnaires
    lambda_results = {}

    cnt = countPixel(h)

    for i in range(th_black + 1, len(h)): #on teste tous les seuils possibles
        #pour chaque seuil, on calcule:

        # (1) variance intra-classe du background
        #il s'agit bien du background car de 0 à i on a les pixels les plus foncés
        vb = variance(0, i, h)
        wb = weight(0, i, h) / float(cnt)
        mb = mean(0, i, h)

        # (2) variance intra-classe du foreground
        vf = variance(i, len(h), h)
        wf = weight(i, len(h), h) / float(cnt)
        mf = mean(i, len(h), h)

        #d'après Noboyuki Otsu, 1979, on calcule:

        variance_intra = wb * vb + wf * vf
        #somme pondérée des variances intra du background et du foreground


        variance_inter = wb * wf * (mb - mf)**2
        #maximale si les couleurs moyennes du foreground et du background (mb et mf)
        #sont éloignées, et si les 2 classes sont équilibrées

        #comme on veut maximiser la variance inter et minimiser l'intra,
        #cela revient à maximiser le critère lambda suivant
        lambda_value = variance_inter/variance_intra

        if not math.isnan(lambda_value):
            #on associe dans le dictionnaire lambda_results les valeurs
            #des seuils possibles et les valeurs lambda correspondantes
            lambda_results[i] = lambda_value


    return lambda_results



def get_optimal_threshold(lambda_results):
    """
    Retourne le seuil de segmentation maximisant le critère lambda
    """

    max_lambda = max(lambda_results.values())
    optimal_threshold = [k for k, v in lambda_results.items() if v == max_lambda]
    print ('optimal threshold: ', optimal_threshold[0])

    return optimal_threshold[0]


def segmentation_img(img, th_black, th_crops):
    """
    Cette fonction segmente l'image:
        - ce qui est supérieur au seuil th_crops apparaît en blanc
        - ce qui est inférieur à th_black apparaît en noir
        - le reste en gris (plantes foncées ~adventices)
    Arguments:
        - th_black: seuil séparant le sol, fixé au départ
        - th_crops: seuil obtenu via la méthode d'Otsu
    """
    row, col = img.shape

    y = np.zeros((row, col))
    for i in range(0,row):
        for j in range(0,col):
            if img[i,j]>th_black:
                if img[i,j] >= th_crops:
                    y[i,j] = 255
                else:
                    y[i,j] = 150 #les mauvaises herbes apparaissent en gris
            else: #ce qui est inférieur à th_black est mis en noir
                y[i,j] = 0
    return y

def segmentation_otsu(img, th_black):
    """
    Cette fonction applique une segmentation Otsu à une image en GRAYSCALE. Pour que la segmentation permette
    de séparer tournesols et adventices, il faut de préférence que l'image grayscale soit obtenue après transformation ExG
    Arguments:
     - name_img: nom de l'image
     - th_black: seuil à partir duquel on considère les pixels
     ex: si th_black = 38, on ne considère donc pas les pixels ayant des niveaux de gris entre
     0 et 38 (ie pixels noirs ou gris foncé)
    """
    h = Hist(img, th_black)

    lambda_results = threshold(h, th_black)
    seuil_optimal = get_optimal_threshold(lambda_results)

    res = segmentation_img(img, th_black, seuil_optimal) #on segmente l'image avec le seuil optimal trouvé

    return res
