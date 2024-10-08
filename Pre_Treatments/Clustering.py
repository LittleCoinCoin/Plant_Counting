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

def ClusterImageSubpart(bound, image, _clusteringAlgorithm, **kwargs):
    print("Processing subpart: ", bound)
    subpart = image[bound[0]:bound[1], bound[2]:bound[3]]

    return ClusterImageWhitePixels(subpart, _clusteringAlgorithm, **kwargs)

def ClusterImageWhitePixels(_image, _clusteringAlgorithm, _whiteLevel = 220, **kwargs):

    # Get positions of the white pixels,
    white_positions = np.where(_image > _whiteLevel)
    # Transpose to fit the format expected by the clustering algorithm
    white_positionsT = np.transpose(white_positions)

    # Perform clustering (DBSCAN or OPTICS)
    print("Clustering")
    data = white_positionsT # an alias to facilitate development and testing alternatives, might be removed later
    # clusteringManager = _clusteringAlgorithm(eps = 10, p = 2, xi = 0.375)
    clusteringManager = _clusteringAlgorithm(eps = 1, cluster_method="dbscan")
    clustering = clusteringManager.fit(data)


    # Generate reachability plot
    plt.figure()
    reachability = clustering.reachability_[clustering.ordering_]
    plt.plot(reachability)
    plt.title('Reachability plot')

    return (clustering.labels_, white_positions)

def ClusteringWorkflow(_image_path: str, _clusteringAlgorithm, **kwargs):
    print("===== {} Clustering =====".format(_clusteringAlgorithm))

    # Load the image
    image = cv2.imread(_image_path)
    # Keep only the first channel
    imageC1 = image[:, :, 0]

    # Get the bounds of the subparts of the imag
    bounds = GetImageSubpartBounds(image, 200, 200)
    ## Restrict imageC1 to the first bound
    bound = bounds[0]
    imageC1 = imageC1[bound[0]:bound[1], bound[2]:bound[3]]
            
    (labels, positions) = ClusterImageWhitePixels(imageC1, _clusteringAlgorithm, **kwargs)

    # get the unique labels
    unique_labels = np.unique(labels)
    print ("Unique labels: ", unique_labels)

    # Get rainbow colors for the clusters
    colors = plt.cm.rainbow(np.linspace(0, 1, len(unique_labels)))
    ## Put the colors in a dictionary
    color_dict = dict(zip(unique_labels, colors))

    print("Displaying")
    #create a new figure
    plt.figure()
    # get the positions of the clusters
    for label in unique_labels:
        labelpos = np.where(labels == label)
        label_pos_x = positions[0][labelpos]
        label_pos_y = positions[1][labelpos]

        # show the clusters as scatter points in the original image
        plt.scatter(label_pos_x, label_pos_y, label=label, s=0.1, color=color_dict[label])

        # plot the name of the cluster at the center of the cluster
        plt.text(np.mean(label_pos_x), np.mean(label_pos_y), str(label), fontsize=5, color='black')

# Do a similar thing but with OPTICS
def OPTICSWorkflow(_image_path: str):
    print("===== OPTICS Workflow =====")

    # Load the image
    image = cv2.imread(_image_path)

    # Take a subpart of the image in the center that is 100x100 pixels
    # This is done to speed up the clustering
    center_x = image.shape[1] // 2
    center_y = image.shape[0] // 2
    subpart = image[center_y - 50:center_y + 50, center_x - 50:center_x + 50]
    # Keep only the first channel
    subpart = subpart[:, :, 0]
    reshaped_image = subpart.reshape(-1, 1)
    print("subpart: ", subpart)

    # Perform OPTICS clustering
    print("Performing OPTICS clustering")
    optics = OPTICS(eps=3, min_samples=5)
    print("Fitting")
    clustering = optics.fit(reshaped_image)
    print("Labels: ", clustering.labels_)

    # Reshape the labels back into the original subpart shape
    print("Reshaping")
    clustered_subpart = clustering.labels_.reshape(subpart.shape)
    print("Clustered subpart: ", clustered_subpart)

    # Display the clustered subpart. Use matplotlib for this
    print("Displaying")
    #create a new figure
    plt.figure()
    #show the image
    plt.imshow(clustered_subpart, cmap='viridis')

if (__name__ == '__main__'):
    image_path = "Tutorial/Output_General/Set1/Output/Session_1/Otsu/OTSU_rgb_83.jpg"
    ClusteringWorkflow(_image_path=image_path, _clusteringAlgorithm=OPTICS, eps=200, min_samples=5)
    #OPTICSWorkflow(image_path)
    plt.show()