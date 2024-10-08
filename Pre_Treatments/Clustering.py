import cv2
import numpy as np
from sklearn.cluster import DBSCAN, OPTICS
import matplotlib.pyplot as plt

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
    print("===== OPTICS Clustering =====")

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
    print("Clustering")
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

if (__name__ == '__main__'):
    image_path = "Tutorial/Output_General/Set1/Output/Session_1/Otsu/OTSU_rgb_83.jpg"
    
    
    (whitePositions, clustering) = ClusteringWorkflow_OPTICS(_image_path=image_path, eps=1.25)
    Plot_ClusteringWorkflow_OPTICS(whitePositions, clustering)
    #OPTICSWorkflow(image_path)
    plt.show()