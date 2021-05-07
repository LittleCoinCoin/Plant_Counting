## Goal:
- Approximating the positions of the plants thanks to a Fourier Analysis

## Methods:
A quick grasp of the methods are also available in the [video](https://www.youtube.com/watch?v=85YllTyfxaQ&t=88s)
![](https://github.com/LittleCoinCoin/Plant_Counting/blob/Pre-Release/Documentation/Images/FourierAnalysis_v3-1.png)
- Converts the Otsu Image white pixels (i.e. plants pixel) into a 1D signal 
by keeping only the X or Y coordinates (basically a projection of the white
pixels on the X or Y axis.
- We use the Fourier Analysis to compute the maximum frequency of the 1D signal.
- It is used twice. The first time to appproximate the position of the crops
rows (with the 1D signal on the X axis). The second time to approximate the positions
of the plants in all the crops rows (with the 1D signal on the Y axis detected
the first time.
    
## Variables the user can change:
- *path_root (string)*: root directory of the input (rotated Otsu Images) and
the output (so that results are all available together with the input).

- *_session_number (int)*: the results of every run are further organized in a 
session folder. This parameters controls the index of the folder.
    
- *bins_div_X (int, min = 1)*: size of the bins used for the density distribution
of the white pixels on the X Axis to smooth the signal before giving it to
the Fourier Analysis.
    
- *bins_div_Y (int, min = 1)*: same as "bins_div_X" but on the Y axis.
