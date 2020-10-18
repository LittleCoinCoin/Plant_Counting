#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 14:27:00 2019

@author: eliott
"""

import os
import re
import json
from PIL import Image

###############################################################################
#
#                       GENERAL Input/Output FUNCTIONS
#
###############################################################################    
def reader(_path, _file_name):
    """
    Basic reading function.s    
    
    _path (string):
        path pointing to the directory where _file_name is. Relative paths are working.
    
    _file_name (string):
        name of the file (with the extension) to be read
    
    Returns the content of /_path/_file_name as a list
    """
    file_object = open(_path+"/"+_file_name, 'r')
    
    file_content = file_object.readlines()
    file_object.close()
    
    return(file_content)

def read_column(_path, _file_name, _cols, _sep = "\s+"):
    
    """
    Read a file and returns a list of strings with only the selected columns.
    
    _path (string):
        path pointing to the directory where _file_name is. Relative paths are working
    
    _file_name (string):
        name of the file (with the extension) to be read
        
    _cols (list):
        list of the index of the columns we wish to read from _file_name. The index
        starts with 1.
    
    _sep (string):
        string of the pattern which seperates the columns in _file_name. This is fed
        to *re.split(pattern, string)*
    
    RETURNS the columns of _path/_file_name as a list of strings
    """
    
    content = reader(_path, _file_name)
    extract = []
    for _line in content:
        extract_line = ""
        line_split = re.split(_sep, _line)
        for _index in _cols:
            extract_line += line_split[_index-1] + " "
        
        extract_line += "\n"
        
        extract.append(extract_line)
    
    return extract

def writer(_path, _file_name, _content, _overwrite = False, _print_file_status = True):
    
    """
    Basic writing function. It is recommended to use the function *check_make_directory(_path)*
    before using *writer(_path, _file_name, _content, _overwrite)*.
    
    _file_name (string):
        name of the file (with the extension) to be written
    
    _path (string):
        path pointing toward the directory where we want to write _file_name.
        Relative paths are working
    
    _content (list of strings):
        content that we want to write in /_path/_file_name
    
    _overwrite(bool, default = False):
        If /_path/_file_name already exists, and parameter is set to True, then
        /_path/_file_name is overwritten. If set to False,
        the old file is conserved and a warning is printed.
    
    _print_file_status(bool, default=True):
        If set to True, print a message in the console to inform that the wrting
        operation has terminated with the file being created or overwritten or not.
    
    """
    
    if (not os.path.exists(_path+"/"+_file_name)):
        file_object = open(_path+"/"+_file_name, 'w')
        for _line in _content:
            if (_line[-1:] == "\n"):
                file_object.write(_line)
            else:
                file_object.write(_line+"\n")   
        file_object.close()
        if (_print_file_status):
            print(_file_name+" was successfully created")
    else:
        if (_overwrite):
            file_object = open(_path+"/"+_file_name, 'w')
            for _line in _content:
                
                if (_line[-1:] == "\n"):
                    file_object.write(_line)
                else:
                    file_object.write(_line+"\n")
            file_object.close()
            if (_print_file_status):
                print(_file_name+" was successfully overwritten")
        else:
            if (_print_file_status):
                print ("File {0} already exists in directory {1} and overwrite is set to False".format(_file_name, _path))

def WriteJson(_path, _file_name, _content, _indent=1):
    """
    Uses the Json library to condense a bit the steps to write a json file
    
    _path (string):
        path pointing toward the directory where we want to write _file_name.
        Relative paths are working
    
    _file_name (string):
        name of the file (WITHOUT the .json extension) to be written
        
    _content (dict):
        content that we want to write in /_path/_file_name
    """
    file = open(_path+"/"+_file_name+".json", "w")
    json.dump(_content, file, indent = _indent)
    file.close()

def copier(_path, _file_name, _new_path, _new_file_name, _overwrite = False):
    
    """
    Basic copying function. It is recommended to use *check_make_directory(_new_path)*
    before using *copier(_path, _file_name, _new_path, _new_file_name)*
    
    _path (string):
        path pointing toward the directory of _file_name. Relative paths are working.
    
    _file_name (string):
        name of the file (with the extension) to be copied.
    
    _new_path (string):
        path pointing toward the directory where we want to copy _file_name.
        Relative paths are working.
    
    _new_file_name (string):
        name of the file (with the extension) that is a copy of _file_name.
    
    """
    if (not os.path.exists(_new_path+'/'+_new_file_name)):
        file_object = open(_path+"/"+_file_name, 'r')
        copy_file_object = open(_new_path+'/'+_new_file_name, 'w')
        
        file_lines = file_object.readlines()
        file_object.close()
        
        copy_file_object.writelines(file_lines)
        copy_file_object.close()
        
        print("File {0} was successfully copied in {1}".format(_new_file_name, _new_path))
    
    else:
        if (_overwrite):
            file_object = open(_path+"/"+_file_name, 'r')
            copy_file_object = open(_new_path+'/'+_new_file_name, 'w')
            
            file_lines = file_object.readlines()
            file_object.close()
            
            copy_file_object.writelines(file_lines)
            copy_file_object.close()
            
            print("File {0} was successfully copied (and overwritten) in {1}".format(_new_file_name, _new_path))
        
        else:
            print ("File {0} already exists in directory {1} and overwrite is set to False".format(_new_file_name, _new_path))    
    

def concatener(_path, _file_name, _path_files_to_concatenate, _files_to_concatenate, _overwrite = False):
    
    """
    Concatenate the content of the files in _files_to_concatenate. Uses the *writer* 
    function to write the resulting file in /_path/_file_name .
    It is recommended to use the function *check_make_directory(_path)*
    before using *concatener(_path, _file_name, _files_to_concatenate, _overwrite)*.
    
    _path (string):
        path pointing toward the directory where we want to write _file_name. Relative paths are working
    
    _file_name (string):
        name of the file (with the extension) to be written
    
    _path_files_to_concatenate (list of strings):
        list of paths pointing toward the directories of the files we wish to concatenate
    
    _files_to_concatenate (list of strings):
        names of the files we wish to concatenate
    
    _overwrite(bool, default = False): If /_paht/_file_name already exists,
    and parameter is set to True, then /_paht/_file_name is overwritten. If set to False,
    the old file is conserved and a warning is printed.
    
    _paths and _files_to_concatenate needs to be of same length
    """
    nb_files = len(_files_to_concatenate)
    
    all_content = []
    for i in range(nb_files):
        content = reader(_path_files_to_concatenate[i], _files_to_concatenate[i])
        all_content += content
    
    writer(_path, _file_name, all_content, _overwrite)

def check_make_directory(_dir):
    """
    WARNING This function orks only with absolute paths
    
    Check if the directory _dir exists. If not, the function creates all the 
    intermediate directories to set up _dir correctly.
    
    WARNING At least one folder (called root) in _dir needs to exist in order 
    for check_make_directory(_dir) to work. If no root is detected, then the 
    function returns the list of all intermediate folders.
    """
    
    new_tree = _dir
    folder_to_add=[]
    root_found=False
    if (not os.path.exists(new_tree)):
        while(not root_found):
            new_tree, last_folder = find_previous_dir(new_tree)
            
            if (not (new_tree == None or last_folder == None)):
                folder_to_add.append(last_folder)
                
                if (os.path.exists(new_tree)):
                    root_found = True
            else:
                print ("The tracing of the root directory failed")
                print ("Folders to add were {0}".format(folder_to_add))
                return folder_to_add
            
        folder_to_add.reverse()
        
        for folder in folder_to_add:
            print ("Creating directory " + new_tree + "/" + folder)
            os.mkdir(new_tree+"/"+folder)
            new_tree = new_tree+"/"+folder
    
    else:
        print("The directory " + _dir + " exists")
        print("No Folders had to be created")
            
def find_previous_dir(_dir):
    """
    Detects the last name in a directory _dir with format /root/folder1/folder2
    or Windows double backslashes
    
    Returns a couple which consist in the directory WITHOUT the last folder detected
    and the last folder detected. For example (/root/folder1, folder2).
    """
    
    l = len(_dir)
    i=l-1
    _folder = ""
    while (i != 0 and _dir[i]!="/" and _dir[i]!="\\"):
        _folder+=_dir[i]
        i-=1
    
    if (i != 0):
        last_folder_length = len(_folder)
        rest_of_tree = _dir[:-last_folder_length-1]
        
        return (rest_of_tree, _folder[::-1])
    else:
        return (None, None)
