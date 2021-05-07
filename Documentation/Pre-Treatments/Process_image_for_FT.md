## Goals:
- Performs the pre-processing on images of crop fields captured by UAVs

## Method:

__add image__

- Applies the Otsu Segmentation to transform and RGB image to a Black and White image. The White pixel should correspond to plants.
- Automatically adjust the rotation of the images in order for the crops rows
to be colinear with the Y axis.

## Variables the user can change:
- *make_unique_folder_per_session (bool)*: If set to True the results generated
are always stored in different folders everytime the script is executed. If
set to False, the user can specify a session folder; in that case the results
might be overwritten.
    
- *session_number (int, optional if "make_unique_folder_per_session" is set
to True)*: Should only be used when "make_unique_folder_per_session" is set
to False. In that case, the user should specify the value to create specific
directory in which the results are stored.
    
- *do_Otsu (bool)*: Controls whether the Otsu segmentation should be performed. 
This parameters exists to save time in case one want to redo specific pre-processing.
    
- *do_AD (bool)*: Controls whether the crops rows Angle Detection should be
performed.This parameters exists to save time in case one want to redo specific
pre-processing.
    
- *save_AD_score_images (bool)*: Controls whether we save a copy of the plot of
the rotation score. The rotation score is used to detect the angle of the
crops rows. We want the angle with the minimum score value. This can be used to 
check the behaviour of the automatic angle detection method when it fails to actually
detect the correct angle.
    
- *bsas_threshold (int, min = 1)*: threshold for the inter cluster distance
in the BSAS processus. A value of X means that a new cluster will be formed
when there are X black pixels or more separating two white pixels. The BSAS
processus is used to compute the skeletton of the crops.
    
- *save_BSAS_images (bool)*: controls whether we save the image resulting of
the BSAS procesusus
    
- *path_input (string)*: directory of the raw RGB images of the crop field
     
- *path_output_root (string)*: root directory from where the results will
be saved. We recommend the user do not change any other*"path_output_XXX*.
If so, the correspoding paths will also have to changed in the other scrips
managing the FrequencyAnalysis and the Multi Agent System. 

