
<img src="https://github.com/LittleCoinCoin/Plant_Counting/blob/Pre-Release/Documentation/Images/Logos/logoAPT.jpg"/> <img src="https://github.com/LittleCoinCoin/Plant_Counting/blob/Pre-Release/Documentation/Images/Logos/ekinocs-logo.png" width="200"/> <img src="https://github.com/LittleCoinCoin/Plant_Counting/blob/Pre-Release/Documentation/Images/Logos/LOGO_TerresInnovia.jpg" width="200"/>


# Plant_Counting
 This repo provides a solution to automatically count crops on images captured by Unmanned Aerial Vehicles (UAV). 
 
 > The package is under development and consequent changes to the solution's implementation may occur in the future.
 
# Methods
 The solution developted here relies on unsupervised learning and a Multi-Agents System (MAS) to count the crops.
 The underlying idea is that plants in a crop field are not randomly positioned but spatially organized.
 It should therefore be possible to detect the crops by first detecting the geometry of the crop field.
 The "unsupervised learning" step gives us an approximation of that geometry while the MAS refines this approximation to actually detect the plants.
 Considering the lack of public labelled datasets of crop fields, we designed our method using synthetic datasets for which we built a [generator](https://github.com/LittleCoinCoin/HDRP_PGoCF). It then tested on both synthetic and real data.
 
# How to run the code?
The code is separated in three parts. Supposing that you have an image of a crop field captured by a UAV, 
the procedure will consist in [Pre-Processing](https://github.com/LittleCoinCoin/Plant_Counting/blob/Pre-Release/Documentation/Pre-Treatments/Process_image_for_FT.md), [Approximation of the Geometry](https://github.com/LittleCoinCoin/Plant_Counting/blob/Pre-Release/Documentation/Fourier/FrequencyAnalysis.md) (Fourier Analysis), [Detection of the
Plants](https://github.com/LittleCoinCoin/Plant_Counting/blob/Pre-Release/Documentation/MAS/Multi_Images_Simulation_v12bis.md) (with the MAS). It is possible to Rune all three steps in one go with the script named *WholeProcess.py*; or 
all three steps separately with the scripts *Process_image_for_FT.py*, *FrequencyAnalysis.py* and *Multi_Images_Simulation_v12bis.py*.
Further details about each scripts are available in the Documentation.
A little [tutorial](https://github.com/LittleCoinCoin/Plant_Counting/blob/Pre-Release/Tutorial/Tutorial.md) is available

# References
 * The paper presenting the method:
 >Jacopin, E.; Berda, N.; Courteille, L.; Grison, W.; Mathieu, L.; Cornuéjols, A. and Martin, C. (2021). Using Agents and Unsupervised Learning for Counting Objects in Images with Spatial Organization. In Proceedings of the 13th International Conference on Agents and Artificial Intelligence - Volume 2: ICAART, ISBN 978-989-758-484-8 ISSN 2184-433X, pages 688-697. DOI: [10.5220/0010228706880697](https://www.scitepress.org/PublicationsDetail.aspx?ID=oMt1HgWONLQ=&t=1)
 * There is also a video for a more concise view than the paper:
 
 [![Alt text](https://img.youtube.com/vi/85YllTyfxaQ/0.jpg)](https://www.youtube.com/watch?v=85YllTyfxaQ)
 
