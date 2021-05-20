# Instructions

## Dependencies 
- [Pillow](https://anaconda.org/anaconda/pillow)
- [PyClustering](https://anaconda.org/conda-forge/pyclustering)
- [Scikit Learn](https://anaconda.org/anaconda/scikit-learn)
- [Scikit Image](https://anaconda.org/anaconda/scikit-image)
- [OpenCV](https://anaconda.org/conda-forge/opencv)

## Description
This tutorial is based on the dummy images you may find in */Data/Non-Labelled/Set1*.
The images are synthetic and were generated with [our custom generator](https://github.com/LittleCoinCoin/HDRP_PGoCF).
Although the synthetic images we generate are automatically labelled (that's the point of synthetic data, right?), we 
removed the labels to do as if we were dealing with freshly acquired images of a real crop field captured
by a UAV. 

In this tutorial, we will run the pre-processing and the 2 steps detection method on the images.
These three processes can be run separately with the scripts *Process_image_for_FT.py*, *FrequencyAnalysis.py*
and *Multi_Images_Simulation_v12bis.py*. You can refer to the [documentation](https://github.com/LittleCoinCoin/Plant_Counting/tree/Pre-Release/Documentation)  for more information about the parameters accessible.


By default the paths parameters point to the images in */Set1*. Results are already accessible
in the */Output_General* folder. 
You can of course change the paths parameters to point to a folder containing your own images.
However, the crop rows of all images __MUST__ be oriented in the same direction. Also, the crop rows
__SHOULD NOT__ exhibit obvious curves at the scale of the image.
We also discourage applying our method on a mosaïc image representing a complete field. Instead, we recommend
tilling it into smaller chunks; an image size around 2000x2000 pixels runs fine on our end but it ultimately
depends on the performances of your machine.

## Pre-processing
Run *Process_image_for_FT.py*

During the pre-processing, the images will be i) segmented using an Otsu segmentation; ii) rotated so that
the crop rows are vertically oriented; iii) filtered to extract the skeleton of the crop rows ([BSAS](https://pyclustering.github.io/docs/0.9.0/html/db/d8b/classpyclustering_1_1cluster_1_1bsas_1_1bsas.html)
method).

Results are found in the folder */Output*. The segmented image are in the */Otsu* folder and their rotated
counter part are in the folder */Otsu_R*. Images of the skeletton of the crop rows are saved only if the 
parameter *_save_BSAS_images=true*.

## Approximation of the geometry of the crop field
Run *FrequencyAnalysis.py*

The goal of this step is to detect the crop rows and approximate the position of the target plants.
We do so by performing a Fourier analysis of the histograms resulting of the projections on the X and
Y axis of the white pixels of the Otsu images.

Results are in the folder */Output_FA*. They are json files containing the position of the predicted plants
for each crop row.

## Refining the detection of the plants
Run *Multi_Images_Simulation_v12bis.py* 

During this step, the Multi-Agents System is initialized based on the approximation made by the Fourier Analysis.
Should the detection results be very bad for your own set of images, please start by altering the parameter 
*_RAs_group_size* ([doc](https://github.com/LittleCoinCoin/Plant_Counting/blob/Pre-Release/Documentation/MAS/Multi_Images_Simulation_v12bis.md)).

The results are in the folder */Output_Meta_Simulation*. The file **MetaSimulationResults_\*** summarizes the 
detection results. The variable *_NB_RALs_* correspond to the number of plants. You can have access to the positions
of the plants per crop row in json files In the folder */RALs_NestedPositions_\**.

## Runing the MAS on a single image
It is possible to run the Multi-Agents System on a single image to visualize the positions of the plant agents.
This can help to fine tune a bit the parameters' values for the MAS. For instance, this is very useful to check whether
different values of *_RAs_group_size* could improve the detectection performances.

For this, run the script *Single_Image_Simulation_v11.py*
(don't mind the commented bits of the code)

By default *Single_Image_Simulation_v11.py* paths variables point to */Set1*. Bear in mind that the pre-processing
and Fourier Analysis steps must have been performed before trying to run *Single_Image_Simulation_v11.py*.
Indeed, the vertically adjusted Otsu images (in folder */Otsu_R*) and the predictions of the Fourier Analysis
(in folder */Plant_FT_Predictions*) should exist for the MAS to run.

Sometimes, datasets are quite large so, to avoid loading the whole image dataset, it is possible to limit the loeading
to the k first images. This can be set with the parameter *subset_size*.

Every parameter of the MAS can be changed with the variables *RAs_group_size*, *RAs_group_steps*, *Simulation_steps*,
*RALs_fuse_factor*, *RALs_fill_factor*. See the [doc](https://github.com/LittleCoinCoin/Plant_Counting/blob/Pre-Release/Documentation/MAS/Multi_Images_Simulation_v12bis.md) for more details about what they do.

You can specify which image you want to run the MAS on with the vairable "_image_index" (starts at 0).

The function *MAS_Simulation.Show_RALs_Position(_recorded_position_indeces=[-1], _colors=['g'])* at the end of the script will
generate a plot with the position of the plant agents as green squares centered.
