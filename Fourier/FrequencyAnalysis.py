# -*- coding: utf-8 -*-
"""
goal:
    - Approximation of the position of the plants positions thanks to Fourier Analysis
Method
    - Convert the Otsu Image white pixels (i.e. plants pixel) into a 1D signal used
    by the Fourier Analysis
    - The Fourier Analysis is used to compute the maximum frequency of the signal
    - It is used twice. The first time to appproximate the position of the crops
    rows. The second time to approximate the positions of the plants in all the
    crops rows detected the first time.
    
variables the user can change:
    - path_root (string): root directory of the input (rotated Otsu Images) and
    the output (so that results are all available together with the input)
    
    - bins_div_X (int, min = 1): size of the bins used for the density distribution
    of the white pixels on the X Axis to smooth the signal before giving it to
    the Fourier Analysis.
    
    - bins_div_Y (int, min = 1): same as "bins_div_X" but on the Y axis
"""
import os
import sys
import numpy as np
#import matplotlib.pyplot as plt

sys.path.append(os.path.abspath("../Utility"))
import general_IO as gIO

# =============================================================================
# Utility Functions Definition
# =============================================================================
def import_data(_path, _file_names, _import_function):
    data = []
    for _n in _file_names:
        data += [_import_function(_path + "/" + _n)]
    return data

def get_file_lines(path_csv_file):
    file_object = open(path_csv_file, 'r')
    file_content = file_object.readlines()
    file_object.close()
    return(file_content)


# =============================================================================
# Specific Function Definition
# =============================================================================

def separate_X_Y_from_bsas_files(_data):
    X, Y = [], []
    for _coord in _data[1:]:
        (y, x) = _coord.split(',')#y is first because coordinates in bsas files are (line, column)
        X += [float(x)]
        Y += [float(y)]
    return np.array(X), np.array(Y)

def Compute_Power_and_Freq(_signal):    
    fourier = np.fft.fft(_signal)
    power = np.absolute(fourier/_signal.size)**2
    freq = np.fft.fftfreq(_signal.size, d=1)
    
    return power, freq

def Get_Signal_Freq(_power, _all_freq):
    nb_points = _all_freq.size
    i=0
    _max=0
    _freq_index=0
    while _all_freq[i] >= 0 and i < nb_points-1:
        
        if (_power[i+1] > _power[i]):
            if (_power[i+1] > _max):
                _max = _power[i+1]
                _freq_index = i+1
        i+=1
    if (_freq_index == 0):
        _freq_index += 1
        
    elif(_all_freq[_freq_index] < 0):
        _freq_index=1
    
    return _all_freq[_freq_index]

def Clamp_Value(_value, _min, _max):
    if (_value < _min):
        _value = _min
    elif (_value > _max):
        _value = _max
    return _value

def Get_Corrected_Peak_Index(_histogram, _peak_index, _search_window_half_width):
    subset_low_boundary = Clamp_Value(_peak_index-_search_window_half_width,
                                      0,
                                      _histogram.size-1)
    subset_high_boundary = Clamp_Value(_peak_index+_search_window_half_width+1,
                                       0,
                                       _histogram.size-1)
    subset = _histogram[subset_low_boundary:subset_high_boundary]
    return np.argsort(subset)[-1] - _search_window_half_width

def Search_Periodic_Peaks(_histogram, _period, _bin_div):
    
    signal_max_index = np.argsort(_histogram)[-1]
    
    search_window_half_width = int(0.1*_period)
    if (search_window_half_width==0):
        search_window_half_width+=1
    
    first_part_rows=[]
    peak_index = signal_max_index
    while (peak_index > 0):
        correction_to_global_max_index = Get_Corrected_Peak_Index(_histogram,
                                                                  peak_index,
                                                                  search_window_half_width)
        corrected_peak_index = peak_index + correction_to_global_max_index
        
        if (_histogram[corrected_peak_index] > 0):
            first_part_rows += [corrected_peak_index*_bin_div]
        
        peak_index = corrected_peak_index - _period
        
    
    second_part_rows=[]
    peak_index = signal_max_index
    while (peak_index < _histogram.size):
        correction_to_global_max_index = Get_Corrected_Peak_Index(_histogram,
                                                                  peak_index,
                                                                  search_window_half_width)
        corrected_peak_index = peak_index + correction_to_global_max_index
        
        if (_histogram[corrected_peak_index] > 0):
            second_part_rows += [corrected_peak_index*_bin_div]
        
        peak_index = corrected_peak_index + _period
    
    
    return first_part_rows[::-1]+second_part_rows[1:]

def Extract_Y_Coord_of_Crop_Rows(_crop_rows,
                                 _x_data_size, _x_period,
                                 _x_coord, _y_coord):
    
    window_half_width = int(0.05*_x_period)
    _x_coord_sort_indeces = np.argsort(_x_coord)
    _x_coord_sorted = _x_coord[_x_coord_sort_indeces]
    _y_coord_sorted_on_x = _y_coord[_x_coord_sort_indeces]
    
    _y_coords_per_crop_row = []
    crops_rows_count = 0
    nb_crops_rows = len(_crop_rows)
    all_rows_parsed = False
    
    i = 0
    subset_low_boundary = Clamp_Value(_crop_rows[crops_rows_count]-window_half_width,
                                      0,
                                      _x_data_size-1)
    subset_high_boundary = Clamp_Value(_crop_rows[crops_rows_count]+window_half_width+1,
                                       0,
                                       _x_data_size-1)
    _row_content=[]
    while i < _x_data_size and not all_rows_parsed:
        if (_x_coord_sorted[i]>subset_low_boundary):
            if (_x_coord_sorted[i]<subset_high_boundary):
                _row_content += [_y_coord_sorted_on_x[i]]
                i+=1
            else:
                _y_coords_per_crop_row.append(_row_content)
                _row_content = []
                crops_rows_count+=1
                if (crops_rows_count < nb_crops_rows):
                    subset_low_boundary = Clamp_Value(_crop_rows[crops_rows_count]-window_half_width,
                                          0,
                                          _x_data_size-1)
                    subset_high_boundary = Clamp_Value(_crop_rows[crops_rows_count]+window_half_width+1,
                                           0,
                                           _x_data_size-1)
                else:
                    all_rows_parsed = True
                
        else:
            i += 1
    
    if (not all_rows_parsed):
        _y_coords_per_crop_row.append(_row_content)
        
    return _y_coords_per_crop_row

def Get_Signal_Period(_data, _axis_size, _bin_div):
    histogram = np.histogram(_data, bins=int(_axis_size/_bin_div), range=(0, _axis_size))
    power, freq = Compute_Power_and_Freq(histogram[0])
    signal_freq = Get_Signal_Freq(power, freq)
    signal_period = int(1/signal_freq)
    
# =============================================================================
#     print("signal_freq", signal_freq)
# 
#     plt.subplot(212)
#     plt.scatter(freq, power)
# =============================================================================
    
    return histogram, signal_period

def All_Fourier_Analysis(_path_input_output,
                         _session_number=1,
                         _bin_div_X=2, _bin_div_Y=4):
    
################## Paths and parameters definition
    
    path_input_root = _path_input_output+"/Output/Session_"+str(_session_number)
    path_output_root = _path_input_output+"/Output_FA/Session_"+str(_session_number)
    
    path_input_bsas = path_input_root+"/BSAS/1_R/Output_Positions"
    path_input_bsas_dir0 = path_input_bsas+"/direction_0"
    path_input_bsas_dir1 = path_input_bsas+"/direction_1"
    
    names_input_bsas_dir0 = os.listdir(path_input_bsas_dir0)
    names_input_bsas_dir1 = os.listdir(path_input_bsas_dir1)
    
    path_output_FT_predictions = path_output_root+"/Plant_FT_Predictions"
    gIO.check_make_directory(path_output_FT_predictions)
    
    subset_size = 4
    
################## Import Data
    data_bsas_dir0 = import_data(path_input_bsas_dir0,
                                 names_input_bsas_dir0[:subset_size],
                                 get_file_lines)
    
    data_bsas_dir1 = import_data(path_input_bsas_dir1,
                                 names_input_bsas_dir1[:subset_size],
                                 get_file_lines)
    
    nb_images = len(data_bsas_dir0)
    
    for i in range (nb_images):
        size_str = data_bsas_dir0[i][0].split('*')
        (lines, columns) = (int(size_str[0]), int(size_str[1]))
        
        X,Y = separate_X_Y_from_bsas_files(data_bsas_dir0[i])
        
        
################## Analyse signal on X axis            
        histogram, signal_period = Get_Signal_Period(X, columns, _bin_div_X)
        crops_rows = Search_Periodic_Peaks(histogram[0], signal_period, _bin_div_X)
        nb_rows = len(crops_rows)
        print("nb_rows:", nb_rows)
        
################## Analyse signal on Y axis
        X2,Y2 = separate_X_Y_from_bsas_files(data_bsas_dir1[i])
        crops_rows_content = Extract_Y_Coord_of_Crop_Rows(
                                            crops_rows,
                                            X2.size, signal_period*_bin_div_X,
                                            X2, Y2)
        
        #For the analysis on axis Y we separate the detection of the signal period
        #and the search of the peaks. We agglomerate the signal periods of all
        #the crops rows by taking the median. This is necessary because the
        #signal of the Y axis is usually less clear than the signal on the X
        #axis.
        all_histograms_per_CR = []
        all_period_per_CR=[]
        for _cr_content in crops_rows_content:
# =============================================================================
#                   plt.figure()
#                   plt.subplot(211)
#                   plt.hist(_cr_content, bins=int(lines/bins_div_Y))
# =============================================================================
            histogram, signal_period = Get_Signal_Period(_cr_content, lines, _bin_div_Y)
            all_histograms_per_CR.append(histogram)
            all_period_per_CR.append(signal_period)
        
        predicted_plants_Y_per_crop_rows = []
        print("all_period_per_CR:", all_period_per_CR)
        signal_period = int(np.median(all_period_per_CR))
        #signal_period = int(min(all_period_per_CR))
        print("signal_period:", signal_period)
        for j in range(nb_rows):
            predicted_plants = Search_Periodic_Peaks(all_histograms_per_CR[j][0], signal_period, _bin_div_Y)
            predicted_plants_Y_per_crop_rows += [predicted_plants]
        
        
################## Reorganise plant coordinates
        predicted_FT = []
        nb_predictions = 0
        for j in range(nb_rows):
            current_CR_content = predicted_plants_Y_per_crop_rows[j]
            crops_coord_in_CR = []
            for _plant_height in current_CR_content:
                crops_coord_in_CR.append([int(crops_rows[j]), int(_plant_height)])
                nb_predictions+=1
            predicted_FT.append(crops_coord_in_CR)
        
################## Save the predictions in json file
        _file_name="PredictedRows_Img_"+str(i)+"_"+str(nb_predictions)
        gIO.WriteJson(path_output_FT_predictions, _file_name, predicted_FT)




# =============================================================================
# General Fourier Procedure
# =============================================================================

if (__name__ == "__main__"):
# ========================== FOR NON-LABELLED IMAGES ======================== #
# =============================================================================
#     All_Fourier_Analysis(_path_input_output="../Tutorial/Output_General/Set1",
#                          _session_number=1,
#                          _bin_div_X=2, _bin_div_Y=4)
# =============================================================================
    
# ========================== FOR LABELLED IMAGES ============================ #
    All_Fourier_Analysis(_path_input_output="../Tutorial/Output_General/Set3",
                         _session_number=1,
                         _bin_div_X=2, _bin_div_Y=4)
