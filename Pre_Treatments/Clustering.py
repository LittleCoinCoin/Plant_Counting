import cv2
from sklearn.cluster import DBSCAN, OPTICS
import matplotlib.pyplot as plt

def DBSCANWorkflow(_image_path: str):
    print("===== DBSCAN Workflow =====")

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

    # Perform DBSCAN clustering
    print("Performing DBSCAN clustering")
    dbscan = DBSCAN(eps=3, min_samples=5)
    print("Fitting")
    clustering = dbscan.fit(reshaped_image)
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
    DBSCANWorkflow(image_path)
    OPTICSWorkflow(image_path)
    plt.show()