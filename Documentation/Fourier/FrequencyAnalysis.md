## goal:
- Approximating the positions of the plants thanks to a Fourier Analysis

## Method

__add image__

- Convert the Otsu Image white pixels (i.e. plants pixel) into a 1D signal used
by the Fourier Analysis
- The Fourier Analysis is used to compute the maximum frequency of the signal
- It is used twice. The first time to appproximate the position of the crops
rows. The second time to approximate the positions of the plants in all the
crops rows detected the first time.
    
## variables the user can change:
- *path_root (string)*: root directory of the input (rotated Otsu Images) and
the output (so that results are all available together with the input)

- *_session_number (int)*: The results of every run are further organized in a 
session folder. This parameters controls the index of the folder.
    
- *bins_div_X (int, min = 1)*: size of the bins used for the density distribution
of the white pixels on the X Axis to smooth the signal before giving it to
the Fourier Analysis.
    
- *bins_div_Y (int, min = 1)*: same as "bins_div_X" but on the Y axis