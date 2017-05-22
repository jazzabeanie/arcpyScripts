# --------------------------------
# Name: fix_lyr_file_paths.py
# Purpose: Changing references to layers within .lyr files
# Author: Jared Johnston
# Created: 3/04/2017
# Copyright:   (c) TCC
# ArcGIS Version:   10.2
# Python Version:   2.7
# Sources: https://blogs.esri.com/esri/arcgis/2011/08/04/pythontemplate/
#          http://gis.stackexchange.com/questions/6884/changing-data-source-path-involving-feature-dataset-in-lyr-files-using-arcpy
#          http://resources.arcgis.com/en/help/main/10.2/index.html#//00s300000008000000
#          http://resources.arcgis.com/en/help/main/10.2/index.html#//00s30000004p000000
# --------------------------------
import os
import sys
import arcpy
import logging
import re

logging.basicConfig(filename='fix_lyr_file_paths.log',
                    level=logging.DEBUG,
                    format='%(asctime)s @ %(lineno)d: %(message)s',
                    datefmt='%Y-%m-%d,%H:%M:%S')

# Layers:
find_string = "S:\\Infrastructure Planning\\Spatial Data\\StormWater"
replace_string = r'O:\Data\Planning_IP\Spatial\Stormwater'
logging_only = False
test_lyr = None
# test_lyr = r'C:\TempArcGIS\New Group Layer.lyr'


def do_analysis(*args):
    """Changes the workspace of the layer file. Currently only works for .lyr
    files whose working space is the Stormwater\Database folder. Operates on
    all layer paths provided as arguments if test_lyr is not provided above"""
    if logging_only:
        logging.info("LOGGING ONLY. This script will not make any changes in it's current state. To run the script in write mode, change the logging_only variable to False. This log displays no or yes for each .lyr file, and each layer within group .lyr files if they can be fixed by the script.")
    else:
        logging.info("The status of the layers follows:")
    for layer_path in args:
        print("Processing: %s" % layer_path)
        current_working_directory = re.sub(r'\\[^\\]*$', r'', layer_path)  # removes filename and extention from path
        file_name = re.sub(r'^.*\\', r'', layer_path)  # removes directory
        file_name_no_ext = re.sub(r'[.]lyr', r'', file_name)  # removes extention
        try:
            lyr = arcpy.mapping.Layer(layer_path)
        except ValueError as e:
            logging.info("no, invalid layer: %s" % layer_path)
            if logging_only: logging.info("\t" + e.args[0])
        if lyr.isGroupLayer:
            if logging_only: logging.info("group layer: %s" % layer_path)
            matches = 0
            for inner_layer in arcpy.mapping.ListLayers(lyr):
                try:
                    if inner_layer.isGroupLayer:
                        if logging_only: logging.info("    group:")
                    else:
                        new_workspacePath = inner_layer.workspacePath.replace(find_string, replace_string, 1)
                        if (inner_layer.workspacePath[:len(find_string)] == find_string):
                            inner_layer.findAndReplaceWorkspacePath(inner_layer.workspacePath , new_workspacePath)
                            if logging_only: logging.info("    yes: %s" % inner_layer.name)
                            matches += 1
                        elif (inner_layer.workspacePath[:len(replace_string)] == replace_string):
                            logging.info("    layer already pointing to new location: %s" % inner_layer.name)
                        else:
                            if logging_only: logging.info("    no, %s. Wrong workspace: %s" % (inner_layer.name, inner_layer.workspacePath))
                except arcpy.ExecuteError:
                    if logging_only: logging.exception(arcpy.GetMessages(2))
                except ValueError as e:
                    if logging_only:
                        logging.info("    no, couldn't get data source: %s" % inner_layer.name)
                        # logging.exception("    " + e.args[0])
                except Exception as e:
                    if logging_only:
                        logging.warning("    no, some other error for layer: %s" % layer_path)
                        logging.exception("    " + e.args[0])
            if matches:
                if logging_only:
                    logging.info("yes for group layer: %s" % layer_path)
                    for inner_layer in arcpy.mapping.ListLayers(lyr):
                        try:
                            logging.info("    new workspacePath: %s" % inner_layer.workspacePath)
                        except Exception as e:
                            logging.info("    details of changes:")
                else:
                    lyr.saveACopy("%s\\%s_potentiallyFixed" % (current_working_directory, file_name_no_ext))
                    logging.info("potentially fixed: %s" % layer_path)
            else:
                logging.info("no: %s" % layer_path)
        else:  # .lyr contains a single layer
            try:
                new_workspacePath = lyr.workspacePath.replace(find_string, replace_string, 1)
                if (lyr.workspacePath[:len(find_string)] == find_string):
                    if logging_only:
                        logging.info("yes for single layer: %s" % layer_path)
                        logging.info("    old workspacePath: %s" % lyr.workspacePath)
                        logging.info("    new workspacePath: %s" % new_workspacePath)
                    else:
                        lyr.findAndReplaceWorkspacePath(lyr.workspacePath , new_workspacePath)
                        lyr.saveACopy("%s\\%s_fixed" % (current_working_directory, file_name_no_ext))
                        logging.info("fixed: %s" % layer_path)
                elif (lyr.workspacePath[:len(replace_string)] == replace_string):
                    logging.info("already pointing to new location: %s" % layer_path)
                else:
                    logging.info("no, Wrong workspace in: %s" % layer_path)
            except arcpy.ExecuteError:
                logging.exception(arcpy.GetMessages(2))
            except ValueError:
                logging.info("no, couldn't get data source for %s" % layer_path)
            except Exception as e:
                logging.warning("no, some other error for layer: %s" % layer_path)
                if logging_only: logging.exception("\t" + e.args[0])
# End do_analysis function


# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE,
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == '__main__':
    arguments_exist = True if (arcpy.GetArgumentCount() != 0) else False
    if test_lyr:
        do_analysis(test_lyr)
    elif arguments_exist:
        argv = tuple(arcpy.GetParameterAsText(i)
                     for i in range(arcpy.GetArgumentCount()))
        do_analysis(*argv) # see here for help on #argv https://docs.python.org/2.7/tutorial/controlflow.html#unpacking-argument-lists # noqa
    else:
        print("""
This file takes the path of any number of .lyr files as it's arguments.

Within the code, it has two variables - find_string, and replace_string. These
contain the partial paths that will be substitued in the .lyr files. If these
are to be edited, make sure that consistent formatting it used (find_string
need to have backslashed escaped, replace_string does not).

There is also a logging_only variable which, when set to True, will log the
results only. No files will be written to. This is useful for checking the
results before you run the script.

For any .lyr files that the script fixes, it will save a copy of the layer with
the filename preprended with either;
- 'fixed_' for single layer .lyr files; or
- 'potentiallyFixed_' for group .lyr files.

The ./assess_layers.bat file has been used to run this script.
""")
        os.system('pause')
