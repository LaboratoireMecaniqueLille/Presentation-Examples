# -*- coding: utf-8 -*-
import InfraRed as IR
import GetPTW as PTW
import skimage.io as io
import numpy as np
import os
#import SimpleITK as sitk

# # # # Parameters : All the parameters you may need to change are here.

sigma = 5.6704*(10**(-8)) # sigma is use in the boltzman equation
BB_Emissivity = 0.97 #0.97 for carbon black
directory= "/DIRECTORY/TO/IMAGES/calib_" # directory of th BB images for calibration : has to finish by the beginning of the name of the images (e.g here images will be calib_17.ptm, calib_18.ptm...)
result_directory="/DIRECTORY/TO/Results/" # directory for storage of the coefficients : finish by "/"
video_directory="/DIRECTORY/TO/VIDEO/TO/CALIBRATE/" # directory to video to calibrate : finish by "/"
video_name="Name_of_the_video_to_calibrate.ptw" #name of the video to calibrate (must be in video_directory folder)
Tmin=17 # minimal temperature for calibration
Tmax=30 #max temperature for calibration
Tstep=1 # step between 2 Black Body images, in °C
polynomial_degree=5 # degree of the interpolation polynome used for calibration. Default is 5.
bad_pix_critere=3 # discimative criteria for bad pixels detection. Default is 3.
area_size=30 # size, in pixels, of the side of the square area used for the mean(DL) in the NUC.
NUC=True # set True if you want to use the NUC (DL=>DL) function
Flux=True # set True if you want to convert DL to flux
save_tif=False #set to True is you want a visualization of every image in the video. Activate this option only when calibration is sure, as it takes some time to run.
extension="ptm"  # Extension of your black body images. Correct parameters are "ptm" or "ptw"
camera="titanium" # Name of your camera. Correct parameters are "jade" or "titanium". (RIP Jade...)

 

# # # # Routine : You shouldn't have anything to modify in this part. 

if __name__ == '__main__':
# check if your parameters are correct
  if NUC == False and Flux ==False:
    raise NameError("You can't set both NUC and Flux to False")
  
#Creating a calibration class:
  cal=IR.Calibration(sigma,BB_Emissivity,directory,result_directory,video_directory,Tmin,Tmax,Tstep,polynomial_degree,bad_pix_critere,area_size,NUC,Flux,extension,camera)


#Calling the calibration class functions:
  imageBB=cal.import_imageBB() #import the BB images

  matrice, DL_mean, shape=cal.reshape(imageBB) # reshape images as a matrix of vectors

# Calibrate Black Body images. May raise some warnings during fitting, these are due to bad pixels and you should not worry about it.
  if Flux==True:
    if NUC==True: # First apply a NUC(DL=>DL), then calculate the calibration coefficient 
      DLC_NUC=cal.NUC_DL(matrice,DL_mean)
      DLC_Calibrated=cal.DL2Flux(DLC_NUC)
    else: # Calibrate (DL=>Flux), without NUC
      DLC_Calibrated=cal.DL2Flux(matrice)
  elif Flux==False:
    DLC_Calibrated=cal.NUC_DL(matrice,DL_mean)

  DL_final,mouchard_final,last_nbr_BP=cal.bad_pixels(DLC_Calibrated,shape) # look for bad pixels and mask them

  cal.verif_calibration(imageBB) # display calibrated black body images to check if calibration was done right. 
  
  
# # # # calibration is now done! From now on the calibration coefficients and bad pixels are saved as .npy so you can use them later.

# # # # Next part is to apply the calibration to your experiment. You may have to modify some parameters in the next part.


  if save_tif=True:
    cal.apply_to_essay(save_tif,video_name) # apply calibration to every images in the video and saves them as .tiff
    
  # To apply colors to a small sample of the converted images, for visualization:
    images_directory="/DIRECTORY/TO/CALIBRATED/IMAGES/"
    first_img=495 #number of first image
    last_img=600 #number of last image
    mean_=21000 # mean value of the essay (in mK)
    std_=500 # deviation used for the colorbar (in mK)

    images=[]
    for i in range (first_img, last_img+1): #creating the list of images you want to colorize
      images.append("img_Traction_1.ptw%s.tiff"%i)
      
    cal.color_images(images_directory,images,mean_,std_) # colorize and save