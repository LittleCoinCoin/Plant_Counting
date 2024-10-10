import cv2
import numpy as np
from sklearn.cluster import DBSCAN, OPTICS
from concurrent.futures import ProcessPoolExecutor
import matplotlib.pyplot as plt

import os
import sys
sys.path.append(os.path.abspath("./Utility"))
import general_IO as gIO

def GetImageSubpartBounds(image, _maxHeight = 100, _maxWidth = 100):
    subparts = []
    height, width = image.shape[:2]
    for y in range(0, height, _maxHeight):
        
        maxHeight = _maxHeight
        #If the subpart that is most at the bottom goes over the image height
        #then we need to adjust the height of the subpart 
        if (y + _maxHeight > height):
            maxHeight = height - y

        for x in range(0, width, _maxWidth):
            maxWidth = _maxWidth
            #if the subpart that is most at the right goes over the image width
            #then we need to adjust the width of the subpart
            if (x + _maxWidth > width):
                maxWidth = width - x
            subparts.append([y, y+maxHeight, x, x+maxWidth])

    return subparts

def ClusteringWorkflow_OPTICS(_image_path: str, _whiteLevel = 220, **kwargs):

    print("OPTICS Clustering for image: ", _image_path, " with parameters: ", kwargs)

    # Load the image
    image = cv2.imread(_image_path)
    # Keep only the first channel
    imageC1 = image[:, :, 0]

    # Get the bounds of the subparts of the imag
    bounds = GetImageSubpartBounds(image, 200, 200)
    ## Restrict imageC1 to the first bound
    bound = bounds[0]
    imageC1 = imageC1[bound[0]:bound[1], bound[2]:bound[3]]

     # Get positions of the white pixels,
    white_positions = np.where(imageC1 > _whiteLevel)
    # Transpose to fit the format expected by the clustering algorithm
    white_positionsT = np.transpose(white_positions)

    # Perform clustering (DBSCAN or OPTICS)
    data = white_positionsT # an alias to facilitate development and testing alternatives, might be removed later
    clusteringManager = OPTICS(**kwargs, cluster_method="dbscan")
    clustering = clusteringManager.fit(data)

    return (white_positionsT, clustering)

def Plot_ClusteringWorkflow_OPTICS(_data, _clustering):

    # get the unique labels
    unique_labels = np.unique(_clustering.labels_)
    print ("Unique labels:\n", unique_labels)

    # Get rainbow colors for the clusters
    colors = plt.cm.rainbow(np.linspace(0, 1, len(unique_labels)))
    ## Put the colors in a dictionary
    color_dict = dict(zip(unique_labels, colors))

    figClusters = plt.figure()
    axClusters = figClusters.add_subplot()
    axClusters.set_title("Clustering")
    ordered_labels = _clustering.labels_[_clustering.ordering_]
    ordered_data = _data[_clustering.ordering_]

    figReachability = plt.figure()
    axReachability = figReachability.add_subplot()
    axReachability.set_title("Reachability plot")
    reachability = _clustering.reachability_[_clustering.ordering_]
    # get the positions of the clusters
    for label in unique_labels:
        
        ## Get the current label indeces
        labelpos = np.where(ordered_labels == label)

        # Plot the clusters
        label_pos_x = ordered_data[labelpos, 0]
        label_pos_y = ordered_data[labelpos, 1]
        ## show the clusters as scatter points in the original image
        axClusters.scatter(label_pos_x, label_pos_y, label=label, s=0.1, color=color_dict[label])
        ## plot the name of the cluster at the center of the cluster
        axClusters.text(np.mean(label_pos_x), np.mean(label_pos_y), str(label), fontsize=5, color='black')

        # Plot the reachability
        ## Generate reachability plot
        Rk = reachability[labelpos]
        axReachability.scatter(labelpos[0], Rk, color=color_dict[label], alpha = 0.5)
    
    axReachability.plot([0, len(reachability)], [_clustering.eps, _clustering.eps], color='black')

def ParallelCompute_Clusters_EpsVariation_OPTICS(_imagePath, _nbWorkers = 4, _epsMin = 1, _epsMax = 100, _epsStep = 2):    
    epsValues = np.arange(_epsMin, _epsMax+1, _epsStep)
    executions = []

    # Parallel computation of the OPTICS clustering for each value of eps
    with ProcessPoolExecutor(max_workers=_nbWorkers) as executor:
        executions = [executor.submit(ClusteringWorkflow_OPTICS, _imagePath, eps = _eps) for _eps in epsValues]

    return [execution.result() for execution in executions]

def Clusters_EpsVariation_OPTICS(_imagePath, _pathOutputNbClusterFile,
                                 _nbWorkers = 4, _epsMin = 1, _epsMax = 100, _epsStep = 2,
                                 _plotNbClusters = False):
    """
    Performs OPTICS clustering on the image in _imagePath for different values of eps.
    The number of clusters is computed for each value of eps and saved in a file
    in directory _pathOutputNbClusterFile (the file name is the image name with .csv extension).

    Parameters:
    _imagePath: str
        The path to the image to process
    _pathOutputNbClusterFile: str
        The path to the directory where to save the number of clusters for each value of eps.
    _nbWorkers: int
        The number of workers to use for parallel processing
    _epsMin: float
        The minimum value of eps to consider
    _epsMax: float
        The maximum value of eps to consider
    _epsStep: float
        The step to use to go from _epsMin to _epsMax
    _plotNbClusters: bool
        If True, a plot of the number of clusters as a function of eps is displayed.

    Returns:
        None
    """
    print("==== Eps parameter variation for OPTICS clustering for image: ", _imagePath)

    epsValues = np.arange(_epsMin, _epsMax+1, _epsStep)
    clusters = ParallelCompute_Clusters_EpsVariation_OPTICS(_imagePath = _imagePath, 
                _nbWorkers = _nbWorkers, _epsMin = _epsMin, _epsMax = _epsMax, _epsStep = _epsStep)
    clusterNumbers = [len(np.unique(c[1].labels_)) for c in clusters]

    output = ["{}, {}".format(epsValues[i], clusterNumbers[i]) for i in range(epsValues.shape[0])]
    gIO.writer(_pathOutputNbClusterFile, image_name.split(".")[0]+".csv", output, True, True)
    
    if (_plotNbClusters):
        figNbCulsters = plt.figure()
        axNbClusters = figNbCulsters.add_subplot()
        axNbClusters.set_title("Evolution of the number of clusters")
        axNbClusters.set_xlabel("eps")
        axNbClusters.set_ylabel("# of clusters")

        axNbClusters.scatter(epsValues, clusterNumbers)
        axNbClusters.plot(epsValues, clusterNumbers)

if (__name__ == '__main__'):
    path_data_images = "Tutorial/Output_General/Set1/Output/Session_1/Otsu"
    # get the file names in path_data_images
    file_names = os.listdir(path_data_images)
    
    path_output = "./out"
    path_output_clustering_behavior = path_output + "/Cluster_Number_by_EpsVariation"
    gIO.check_make_directory(path_output_clustering_behavior)

    epsMin = 1
    epsMax = 100
    epsStep = 2
    for image_name in file_names:
        image_path = path_data_images + "/" + image_name
        Clusters_EpsVariation_OPTICS(_imagePath = image_path, _pathOutputNbClusterFile = path_output_clustering_behavior,
         _nbWorkers = 4, _epsMin = epsMin, _epsMax = epsMax, _epsStep = epsStep)
    
    plt.show()