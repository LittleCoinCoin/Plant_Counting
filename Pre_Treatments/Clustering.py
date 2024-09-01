import cv2
import numpy as np
from sklearn.cluster import DBSCAN, OPTICS
import matplotlib.pyplot as plt
import concurrent.futures

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
    # Keep only the first channel
    subpart = subpart[:, :, 0]
    # Reshape it to a 1D array
    reshaped_image = subpart.reshape(-1, 1)

    # Perform clustering (DBSCAN or OPTICS)
    dbscan = _clusteringAlgorithm(**kwargs)
    clustering = dbscan.fit(reshaped_image)

    # Reshape the labels back into the original subpart shape
    clustered_subpart = clustering.labels_.reshape((bound[1] - bound[0], bound[3] - bound[2]))

    # Map the labels to 0 and 1
    # This is necessary because we have no guarentee the clustering on all subparts will
    # choose the same labels to describe black or white.
    # So, being consistent with grayscale color, we set 0 the label for black pixels and
    # 1 the label for white pixels in the original image
    
    # first, all the labels bellow 0 are set to 0
    clustered_subpart[clustered_subpart < 0] = 0
    # then, all the labels above 0 are set to 1
    clustered_subpart[clustered_subpart > 0] = 1
    # get the positions of the labels 0 and -1
    black_positions = np.where(clustered_subpart == 0)
    # if the black positions in the original image give white pixels, set them to 1 and vice versa
    if (image[bound[0]:bound[1], bound[2]:bound[3]][black_positions] > 0).all():
        white_positions = np.where(clustered_subpart == 1)
        clustered_subpart[black_positions] = 1
        clustered_subpart[white_positions] = 0

    return clustered_subpart

def ClusteringWorkflow(_image_path: str, _nbWorkers: int, _clusteringAlgorithm, **kwargs):
    print("===== {} Clustering =====".format(_clusteringAlgorithm))

    # Load the image
    image = cv2.imread(_image_path)

    # Get the bounds of the subparts of the image
    print("Computing image subparts")
    bounds = GetImageSubpartBounds(image)
    nbBounds = len(bounds)

    # Create a new image to store the clustered subparts
    rebuilt_image = np.zeros((image.shape[0], image.shape[1]), dtype=np.int64)

    #Process the subparts using multi-processes
    with concurrent.futures.ProcessPoolExecutor(max_workers = _nbWorkers) as executor:
        # Submit each subpart to the executor
        futures = [executor.submit(ClusterImageSubpart, bound, image, _clusteringAlgorithm, **kwargs) for bound in bounds]
        
        # Get the allSubparts of the tasks
        allSubparts = [future.result() for future in futures]

        # Rebuild the image from all the processes
        for i in range(nbBounds):
            rebuilt_image[bounds[i][0]:bounds[i][1], bounds[i][2]:bounds[i][3]] = allSubparts[i]
            

    # Display the clustered subpart. Use matplotlib for this
    print("Displaying")
    #create a new figure
    plt.figure()
    #show the image
    plt.imshow(rebuilt_image, cmap='viridis', vmin=-1, vmax=1)

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
    ClusteringWorkflow(_image_path=image_path, _nbWorkers=4, _clusteringAlgorithm=DBSCAN, eps=3, min_samples=5, metric="manhattan")
    #OPTICSWorkflow(image_path)
    plt.show()