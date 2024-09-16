import cv2
import numpy as np
from sklearn.cluster import DBSCAN, OPTICS
from sklearn.metrics.pairwise import manhattan_distances
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

def ClusterImageSubpart(bound, image, _clusteringAlgorithm, **kwargs):
    print("Processing subpart: ", bound)
    subpart = image[bound[0]:bound[1], bound[2]:bound[3]]

    return ClusterImageWhitePixels(subpart, _clusteringAlgorithm, **kwargs)

def ClusterImageWhitePixels(_image, _clusteringAlgorithm, _whiteLevel = 220, **kwargs):

    # Get positions of the white pixels,
    white_positions = np.where(_image > _whiteLevel)

    # compute the Manhattan distance matrix between the white pixels
    print("Computing distance matrix")
    white_positions_array = np.column_stack(white_positions)
    distance_matrix = manhattan_distances(white_positions_array)

    # Perform clustering (DBSCAN or OPTICS)
    print("Clustering")
    dbscan = _clusteringAlgorithm(**kwargs, metric="precomputed")
    clustering = dbscan.fit(distance_matrix)

    return (clustering.labels_, white_positions)

def OtsuImagePreprocess(_image_path: str):
    # Load the image
    image = cv2.imread(_image_path)
    # Keep only the first channel
    image = image[:, :, 0]
    # All pixel values bellow 220 are set to 0
    image[image < 220] = 0
    # All pixel values above 220 are set to 255
    image[image >= 220] = 255

    return image

def ClusteringWorkflow(_image_path: str, _nbWorkers: int, _clusteringAlgorithm, **kwargs):
    print("===== {} Clustering =====".format(_clusteringAlgorithm))

    # Load the image
    image = cv2.imread(_image_path)
    # Keep only the first channel
    imageC1 = image[:, :, 0]

    # Get the bounds of the subparts of the image
    #print("Computing image subparts")
    #bounds = GetImageSubpartBounds(image)
            
    (labels, positions) = ClusterImageWhitePixels(imageC1, _clusteringAlgorithm, **kwargs)

    # get the unique labels
    unique_labels = np.unique(labels)
    print ("Unique labels: ", unique_labels)

    print("Displaying")
    #create a new figure
    plt.figure()
    # get the positions of the clusters
    for label in unique_labels:
        labelpos = np.where(labels == label)
        label_pos_x = positions[0][labelpos]
        label_pos_y = positions[1][labelpos]

        # show the clusters as scatter points in the original image
        plt.scatter(label_pos_x, label_pos_y, label=label, s=0.1)

if (__name__ == '__main__'):
    image_path = "Tutorial/Output_General/Set1/Output/Session_1/Otsu/OTSU_rgb_83.jpg"
    ClusteringWorkflow(_image_path=image_path, _nbWorkers=4, _clusteringAlgorithm=DBSCAN, eps=3, min_samples=5)
    #OPTICSWorkflow(image_path)
    plt.show()