# -*- coding: utf-8 -*-
"""
Writing a parser to reorganize the json output and RGB images of the Unity Perception
package. 
By default all captures of all fields and all growth stages are written in a
single Json file. We will cut this json file to organize one folder per field
generated and one sub folder per growth stage.

"""

import os
import json
import shutil

os.chdir("../Utility")
import general_IO as gIO


def Process_UP_Json_Output(_path_source,
                           _path_processed,
                           _nb_fields, _nb_growth_stages, _nb_images_per_gs,
                           _nb_annotations, _nb_metrics):
    
# =============================================================================
#     Load source Json 
# =============================================================================
    gIO.check_make_directory(_path_processed)
    
    all_captures_file_content = Extract_Files_With_Prefix(_path_source+"/Dataset/", "captures")
    captures_file_content = Aggregate_Dict_Values_List(all_captures_file_content, "captures")
    
    all_metrics_file_content = Extract_Files_With_Prefix(_path_source+"/Dataset/", "metrics")
    metrics_file_content = Aggregate_Dict_Values_List(all_metrics_file_content, "metrics")
    
# =============================================================================
#     Partioning per Fields
# =============================================================================
    print()
    print("Partitioning all Captures")
    captures_per_field = Partition_Per_Factors(captures_file_content["captures"],
                                             [_nb_growth_stages, _nb_images_per_gs, _nb_annotations],
                                             _nb_fields)
    print()
    print("Partitioning all Metrics")
    metrics_per_field = Partition_Per_Factors(metrics_file_content["metrics"],
                                            [_nb_growth_stages, _nb_images_per_gs, _nb_metrics],
                                            _nb_fields)
    
# =============================================================================
#     Partitioning Per growth stages
# =============================================================================
    captures_per_gs = []
    metrics_per_gs = []
    for i in range(_nb_fields):
        print()
        print("Partitioning captures of Field {0}/{1}".format(i+1, nb_fields))
        captures_per_gs += [Partition_Per_Factors(captures_per_field[i],
                                             [_nb_images_per_gs, _nb_annotations],
                                             _nb_growth_stages)]
        print("Partitioning metrics of Field {0}/{1}".format(i+1, nb_fields))
        metrics_per_gs += [Partition_Per_Factors(metrics_per_field[i],
                                             [_nb_images_per_gs, _nb_metrics],
                                             _nb_growth_stages)]
    
# =============================================================================
#     Extracting Image names
# =============================================================================
    images_per_gs = []
    for i in range(_nb_fields):
        print()
        print("Extracting image names of Field {0}/{1}".format(i+1, nb_fields))
        images_per_fields = []
        for j in range (_nb_growth_stages):
            images = []
            for _cap in captures_per_gs[i][j]:
                if (_cap["filename"] != None):
                    images += [_cap["filename"].split("/")[-1]]
            images_per_fields += [images]
        images_per_gs += [images_per_fields]
    
# =============================================================================
#     Generating Reorganized directories
# =============================================================================
    for i in range(_nb_fields):
        print()
        print("Generating new jsons for Field {0}/{1}".format(i+1, nb_fields))
        for j in range (_nb_growth_stages):
            print("Growth Stage {0}/{1}".format(j+1, nb_growth_stages))
            path_field_gs = _path_processed+"/Field_{0}/GrowthStage_{1}".format(i,j)
            gIO.check_make_directory(path_field_gs+"/Dataset")
            gIO.check_make_directory(path_field_gs+"/RGB")
            
            partitioned_captures = {}
            partitioned_captures["version"] = captures_file_content["version"]
            partitioned_captures["captures"] = captures_per_gs[i][j]
            partitioned_captures_file = open(path_field_gs+"/Dataset/captures_000.json", "w")
            json.dump(partitioned_captures, partitioned_captures_file, indent = 3)
            partitioned_captures_file.close()
            
            partitioned_metrics = {}
            partitioned_metrics["version"] = metrics_file_content["version"]
            partitioned_metrics["metrics"] = metrics_per_gs[i][j]
            partitioned_metrics_file = open(path_field_gs+"/Dataset/metrics_000.json", "w")
            json.dump(partitioned_metrics, partitioned_metrics_file, indent = 3)
            partitioned_metrics_file.close()
            
            for _img in images_per_gs[i][j]:
                shutil.copy(_path_source+"/RGB/"+_img, path_field_gs+"/RGB/"+_img)
        

def Extract_Files_With_Prefix(_path, _prefix):
    
    all_file_names = os.listdir(_path)
    prefix_length = len(_prefix)
    
    all_files_content = []
    for _file_name in all_file_names:
        if (_file_name[:prefix_length] == _prefix):
        
            captures_file = open(_path + "/" + _file_name, "r")
            all_files_content += [json.load(captures_file)]
            captures_file.close()
    return all_files_content

def Aggregate_Dict_Values_List(_dict_list, _key):
    
    for _dict in _dict_list[1:]:
        _dict_list[0][_key] += _dict[_key]
    
    return _dict_list[0]

def Partition_Per_Factors(_source_list, _factors_list, _root_factor):
    
    nb_individuals_per_root = 1
    for _f in _factors_list:
        nb_individuals_per_root *= _f
    nb_total_individuals = _root_factor * nb_individuals_per_root
    print("nb_individuals_per_root:", nb_individuals_per_root)
    print("nb_total_individuals:", nb_total_individuals)
    return Partition_List(_source_list, nb_total_individuals, nb_individuals_per_root)
    

def Partition_List(_list, _length, _step):
    partition = []
    for i in range (0, _length, _step):
        partition += [_list[i:i+_step]]
    
    return partition
    

if __name__=="__main__":

    nb_fields = 1
    nb_growth_stages = 1
    nb_images_per_gs = 4
    nb_annotations = 2
    nb_metrics = 1
    
    
    path_data = "../Tutorial/Data/Labelled/Set3"
    path_source = path_data + "/Source"
    path_processed = path_data + "/Processed"
    
    Process_UP_Json_Output(path_source, 
                           path_processed, 
                           nb_fields, nb_growth_stages, nb_images_per_gs,
                           nb_annotations, nb_metrics)

