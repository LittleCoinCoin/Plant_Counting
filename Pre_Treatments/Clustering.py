import cv2
import numpy as np
from sklearn.cluster import DBSCAN, OPTICS
from concurrent.futures import ProcessPoolExecutor
import matplotlib.pyplot as plt

import os
import sys
sys.path.append(os.path.abspath("../Utility"))
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

def ClusteringWorkflow_DBSCAN(_image_path: str, _whiteLevel = 220, **kwargs):
    
    print("DBSCAN Clustering for image: ", _image_path, " with parameters: ", kwargs)

    # Load the image
    image = cv2.imread(_image_path)
    # Keep only the first channel
    imageC1 = image[:, :, 0]

    # Get positions of the white pixels,
    white_positions = np.where(imageC1 > _whiteLevel)
    # Transpose to fit the format expected by the clustering algorithm
    white_positionsT = np.transpose(white_positions)

    # Perform clustering (DBSCAN or OPTICS)
    data = white_positionsT # an alias to facilitate development and testing alternatives, might be removed later
    clusteringManager = DBSCAN(**kwargs)
    clustering = clusteringManager.fit(data)

    return (white_positionsT, clustering)

def Plot_ClusteringWorkflow_DBSCAN(_data, _clustering):
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
    
        for label in unique_labels:
            
            ## Get the current label indeces
            labelpos = np.where(_clustering.labels_ == label)
    
            # Plot the clusters
            label_pos_x = _data[labelpos, 0]
            label_pos_y = _data[labelpos, 1]
            ## show the clusters as scatter points in the original image
            axClusters.scatter(label_pos_x, label_pos_y, label=label, s=0.1, color=color_dict[label])
            ## plot the name of the cluster at the center of the cluster
            axClusters.text(np.mean(label_pos_x), np.mean(label_pos_y), str(label), fontsize=5, color='black')

def ParallelCompute_Clusters_EpsVariation_DBSCAN(_imagePath, _nbWorkers = 4, _epsMin = 1, _epsMax = 100, _epsStep = 2):
    epsValues = np.arange(_epsMin, _epsMax+1, _epsStep)
    executions = []

    # Parallel computation of the DBSCAN clustering for each value of eps
    with ProcessPoolExecutor(max_workers=_nbWorkers) as executor:
        executions = [executor.submit(ClusteringWorkflow_DBSCAN, _imagePath, eps = _eps) for _eps in epsValues]

    return [execution.result() for execution in executions]

def Clusters_EpsVariation_DBSCAN(_imagePath, _imageName, _pathOutputNbClusterFile,
                                    _nbWorkers = 4, _epsMin = 1, _epsMax = 100, _epsStep = 2,
                                    _plotNbClusters = False):
    """
    Performs DBSCAN clustering on the image in _imagePath for different values of eps.
    The number of clusters is computed for each value of eps and saved in a file
    in directory _pathOutputNbClusterFile (the file name is the image name with .csv extension).

    Parameters:
    _imagePath: str
        The directory where the image is located.
    _imageName: str
        The name of the image with the extension.
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
    print("==== Eps parameter variation for DBSCAN clustering for image: ", _imagePath + "/" + _imageName)

    epsValues = np.arange(_epsMin, _epsMax+1, _epsStep)
    clusters = ParallelCompute_Clusters_EpsVariation_DBSCAN(_imagePath = _imagePath + "/" + _imageName,
                _nbWorkers = _nbWorkers, _epsMin = _epsMin, _epsMax = _epsMax, _epsStep = _epsStep)
    clusterNumbers = [len(np.unique(c[1].labels_)) for c in clusters]

    output = ["{}, {}".format(epsValues[i], clusterNumbers[i]) for i in range(epsValues.shape[0])]
    gIO.writer(_pathOutputNbClusterFile, _imageName.split(".")[0]+".csv", output, True, True)

    if (_plotNbClusters):
        figNbCulsters = plt.figure()
        axNbClusters = figNbCulsters.add_subplot()
        axNbClusters.set_title("Evolution of the number of clusters")
        axNbClusters.set_xlabel("eps")
        axNbClusters.set_ylabel("# of clusters")

        axNbClusters.scatter(epsValues, clusterNumbers)
        axNbClusters.plot(epsValues, clusterNumbers)

def ClusteringWorkflow_OPTICS(_image_path: str, _whiteLevel = 220, **kwargs):

    print("OPTICS Clustering for image: ", _image_path, " with parameters: ", kwargs)

    # Load the image
    image = cv2.imread(_image_path)
    # Keep only the first channel
    imageC1 = image[:, :, 0]

    # Get positions of the white pixels,
    white_positions = np.where(imageC1 > _whiteLevel)
    # Transpose to fit the format expected by the clustering algorithm
    white_positionsT = np.transpose(white_positions)

    # Perform clustering (DBSCAN or OPTICS)
    data = white_positionsT # an alias to facilitate development and testing alternatives, might be removed later
    clusteringManager = OPTICS(**kwargs)
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
        executions = [executor.submit(ClusteringWorkflow_OPTICS, _imagePath, eps = _eps, cluster_method="dbscan") for _eps in epsValues]

    return [execution.result() for execution in executions]

def Clusters_EpsVariation_OPTICS(_imagePath, _imageName, _pathOutputNbClusterFile,
                                 _nbWorkers = 4, _epsMin = 1, _epsMax = 100, _epsStep = 2,
                                 _plotNbClusters = False):
    """
    Performs OPTICS clustering on the image in _imagePath for different values of eps.
    The number of clusters is computed for each value of eps and saved in a file
    in directory _pathOutputNbClusterFile (the file name is the image name with .csv extension).

    Parameters:
    _imagePath: str
        The directory where the image is located.
    _imageName: str
        The name of the image with the extension.
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
    print("==== Eps parameter variation for OPTICS clustering for image: ", _imagePath + "/" + _imageName)

    epsValues = np.arange(_epsMin, _epsMax+1, _epsStep)
    clusters = ParallelCompute_Clusters_EpsVariation_OPTICS(_imagePath = _imagePath + "/" + _imageName, 
                _nbWorkers = _nbWorkers, _epsMin = _epsMin, _epsMax = _epsMax, _epsStep = _epsStep)
    clusterNumbers = [len(np.unique(c[1].labels_)) for c in clusters]

    output = ["{}, {}".format(epsValues[i], clusterNumbers[i]) for i in range(epsValues.shape[0])]
    gIO.writer(_pathOutputNbClusterFile, _imageName.split(".")[0]+".csv", output, True, True)
    
    if (_plotNbClusters):
        figNbCulsters = plt.figure()
        axNbClusters = figNbCulsters.add_subplot()
        axNbClusters.set_title("Evolution of the number of clusters")
        axNbClusters.set_xlabel("eps")
        axNbClusters.set_ylabel("# of clusters")

        axNbClusters.plot(epsValues, clusterNumbers, marker='o')

def Plot_NbClustersFromFile(_path, _fileName):
    """
    Imports a csv file containing the number of clusters as a function of another value.
    The file is assumed to have two columns separated by a comma. The first column is the
    value and the second column is the number of clusters.

    Parameters:
    _path: str
        The path to the directory containing the file
    _fileName: str
        The name of the file to import
    
    Returns:
        The figure.
    """

    fileContent = gIO.read(_path, _fileName)
    fileContentSTRSplit = [_line.split(',') for _line in fileContent]
    xAndNbClusters = np.array([(float(_x), float(_y)) for [_x,_y] in fileContentSTRSplit])

    figNbCulsters = plt.figure()
    axNbClusters = figNbCulsters.add_subplot()
    axNbClusters.set_title("Evolution of the number of clusters")
    axNbClusters.set_xlabel("eps")
    axNbClusters.set_ylabel("# of clusters")

    axNbClusters.scatter(xAndNbClusters[:,0], xAndNbClusters[:,1])
    axNbClusters.plot(xAndNbClusters[:,0], xAndNbClusters[:,1])

    return figNbCulsters

def Plot_NbClustersFromFiles(_path : list, _fileNames : list, _labels : list = None):
    """
    Imports a csv file containing the number of clusters as a function of another value.
    The file is assumed to have two columns separated by a comma. The first column is the
    value and the second column is the number of clusters.

    Parameters:
    _path: list
        The list of paths to the directories containing the files
    _fileNames: list
        The list of names of the files to import
    _labels: list, optional
        The labels to display for each file. Default is None. In that case the file paths are added.
    
    Returns:
        The figure.
    """

    nbPaths = len(_path)
    nbFiles = len(_fileNames)
    assert nbPaths == nbFiles, "The number of paths and the number of files must be the same."
    
    if (_labels is None):
        _labels = [_path[i] + "/" + _fileNames[i] for i in range(nbPaths)]
    else:
        assert len(_labels) == nbPaths, "The number of labels must be the same as the number of paths."

    figNbCulsters = plt.figure()
    axNbClusters = figNbCulsters.add_subplot()
    axNbClusters.set_title("Evolution of the number of clusters")
    axNbClusters.set_xlabel("eps")
    axNbClusters.set_ylabel("# of clusters")

    scatterSymbols = ['o', 'x', '+', 'v', '^', '<', '>', 's', 'd', 'p', 'h', 'H', '*', 'P', 'X']
    nbSymbols = len(scatterSymbols)

    for i in range(nbPaths):
        fileContent = gIO.read(_path[i], _fileNames[i])
        fileContentSTRSplit = [_line.split(',') for _line in fileContent]
        xAndNbClusters = np.array([(float(_x), float(_y)) for [_x,_y] in fileContentSTRSplit])

        axNbClusters.plot(xAndNbClusters[:,0], xAndNbClusters[:,1], marker=scatterSymbols[i%nbSymbols], alpha=0.5, label=_labels[i])
    
    return figNbCulsters

if (__name__ == '__main__'):
    ### Input Parameters
    #image_type = "real/Bordeaux"
    #path_data_images = "../out/real/Bordeaux/Output/Session_1/Otsu"
    image_type = "virtual/Set2"
    path_data_images = "../Tutorial/Output_General/Set2/Output/Session_1/Otsu"
    # get the file names in path_data_images
    file_names = os.listdir(path_data_images)
    
    ##### Clustering behavior relative to the eps parameter
    ### Output Parameters
    path_output = "../out/" + image_type
    path_output_clustering_behavior = path_output + "/Cluster_Number_by_EpsVariation"
    ### Tests Parameters
    epsMin = 1
    epsMax = 100
    epsStep = 2

    ### For OPTICS
    # path_output_clustering_behavior_OPTICS = path_output_clustering_behavior + "/OPTICS"
    # gIO.check_make_directory(path_output_clustering_behavior_OPTICS)
    # for image_name in file_names:
    #     Clusters_EpsVariation_OPTICS(_imagePath = path_data_images, _imageName = image_name,
    #                                  _pathOutputNbClusterFile = path_output_clustering_behavior_OPTICS,
    #                                 _nbWorkers = 4, _epsMin = epsMin, _epsMax = epsMax, _epsStep = epsStep)

    ### For DBSCAN
    # path_output_clustering_behavior_DBSCAN = path_output_clustering_behavior + "/DBSCAN"
    # gIO.check_make_directory(path_output_clustering_behavior_DBSCAN)
    # for image_name in file_names:
    #     Clusters_EpsVariation_DBSCAN(_imagePath = path_data_images, _imageName = image_name,
    #                                  _pathOutputNbClusterFile = path_output_clustering_behavior_DBSCAN,
    #                                 _nbWorkers = 4, _epsMin = epsMin, _epsMax = epsMax, _epsStep = epsStep)

    ##### Plot cluster numbers
    ### Individual files
    # filePath = path_output_clustering_behavior + "/OPTICS"
    # files = os.listdir(filePath)
    # for _file in files[:1]:
    #     Plot_NbClustersFromFile(filePath, _file)

    ### Multiple files: DBSCAN et OPTICS of the same image + SAVE the PLOTS
    path_out_plots = path_output_clustering_behavior + "/Cluster_Numbers_Comp_Plots"
    gIO.check_make_directory(path_out_plots)
    
    filePaths = [path_output_clustering_behavior + "/DBSCAN", path_output_clustering_behavior + "/OPTICS"]
    labels = ["DBSCAN", "OPTICS"]
    for _file in file_names:
        fileNameClean = _file.split(".")[0]
        fileNames = [fileNameClean+".csv", fileNameClean+".csv"]
        figNbClusters = Plot_NbClustersFromFiles(filePaths, fileNames, labels)
        figNbClusters.legend()
        figNbClusters.savefig(path_out_plots + "/" + fileNameClean + ".png")

    ##### Clustering and ploting the results 
    ### OPTICS
    # for image_name in file_names:
    #     print ("Processing image: ", image_name)
    #     image_path = path_data_images + "/" + image_name
    #     white_positions, clustering = ClusteringWorkflow_OPTICS(image_path, eps = 21)
    #     Plot_ClusteringWorkflow_OPTICS(white_positions, clustering)

    ### DBSCAN
    # for image_name in file_names:
    #     image_path = path_data_images + "/" + image_name
    #     white_positions, clustering = ClusteringWorkflow_DBSCAN(image_path, eps = 21)
    #     Plot_ClusteringWorkflow_DBSCAN(white_positions, clustering)
    
    plt.show()