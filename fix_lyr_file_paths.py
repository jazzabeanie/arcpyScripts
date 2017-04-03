# --------------------------------
# Name:
# Purpose:
# Author: Jared Johnston
# Created:
# Copyright:   (c) TCC
# ArcGIS Version:   10.2
# Python Version:   2.7
# Source: https://blogs.esri.com/esri/arcgis/2011/08/04/pythontemplate/
#         http://gis.stackexchange.com/questions/6884/changing-data-source-path-involving-feature-dataset-in-lyr-files-using-arcpy
#         http://resources.arcgis.com/en/help/main/10.2/index.html#//00s300000008000000
#         http://resources.arcgis.com/en/help/main/10.2/index.html#//00s30000004p000000
# --------------------------------
import os
import sys
import arcpy
import logging
import re

logging.basicConfig(filename='fix_lyr_file_paths.log',  # TODO: update log filename
                    level=logging.DEBUG,
                    format='%(asctime)s @ %(lineno)d: %(message)s',
                    datefmt='%Y-%m-%d,%H:%M:%S')

# Layers:
find_string = "S:\\Infrastructure Planning\\Spatial Data\\StormWater"
replace_string = r'O:\Data\Planning_IP\Spatial\Stormwater'
logging_only = True
test_lyr = None
# test_lyr = r'C:\TempArcGIS\New Group Layer.lyr'


def do_analysis(*args):
    """Changes the workspace of the layer file. Currently only works for .lyr
    files whose working space is the Stormwater\Database folder. Operates on
    all layer paths provided as arguments if test_lyr is not provided above"""
    for layer_path in args:
        print("Processing: %s" % layer_path)
        # Parses input layer string to get the location and file name:
        current_working_directory = re.sub(r'\\[^\\]*$', r'', layer_path)
        file_name = re.sub(r'^.*\\', r'', layer_path)  # removes directory
        file_name_no_ext = re.sub(r'[.]lyr', r'', file_name)  # removes extention
        try:
            lyr = arcpy.mapping.Layer(layer_path)
        except ValueError as e:
            logging.info("Invalid layer: %s" % layer_path)
            logging.info("\t" + e.args[0])
        if lyr.isGroupLayer:
            logging.info("group layer: %s" % layer_path)
            matches = 0
            for inner_layer in arcpy.mapping.ListLayers(lyr):
                try:
                    if inner_layer.isGroupLayer:
                        logging.info("group:")
                    else:
                        new_workspacePath = inner_layer.workspacePath.replace(find_string, replace_string, 1)
                        if (inner_layer.workspacePath[:len(find_string)] == find_string):
                            logging.info("    yes: %s" % inner_layer.name)
                            inner_layer.findAndReplaceWorkspacePath(inner_layer.workspacePath , new_workspacePath)
                            matches += 1
                        else:
                            logging.info("    no, %s. Wrong workspace: %s" % (inner_layer.name, inner_layer.workspacePath))
                except arcpy.ExecuteError:
                    logging.exception(arcpy.GetMessages(2))
                except ValueError:
                    logging.info("no, error getting data source")
                except Exception as e:
                    logging.warning("no, some other error: %s" % layer_path)
                    logging.exception("\t" + e.args[0])
            if matches:
                if logging_only:
                    logging.info("yes for group layer: %s" % layer_path)
                    for inner_layer in arcpy.mapping.ListLayers(lyr):
                        try:
                            logging.info("    new workspacePath: %s" % inner_layer.workspacePath)
                        except Exception as e:
                            logging.warning("    not for: %s" % inner_layer)
                            logging.exception("    " + e.args[0])
                else:
                    lyr.saveACopy("%s\\potentiallyFixed_%s" % (current_working_directory, file_name_no_ext))
                    logging.info("potentially fixed: %s" % layer_path)
            else:
                logging.info("no, all layer in group with wrong workspace: %s" % layer_path)
        else:
            try:
                new_workspacePath = lyr.workspacePath.replace(find_string, replace_string, 1)
                if (lyr.workspacePath[:len(find_string)] == find_string):
                    if logging_only:
                        logging.info("yes for single layer: %s" % layer_path)
                        logging.info("    old workspacePath: %s" % lyr.workspacePath)
                        logging.info("    new workspacePath: %s" % new_workspacePath)
                    else:
                        lyr.findAndReplaceWorkspacePath(lyr.workspacePath , new_workspacePath)
                        lyr.saveACopy("%s\\fixed_%s" % (current_working_directory, file_name_no_ext))
                        logging.info("fixed: %s" % layer_path)
                else:
                    logging.info("no, Wrong workspace: %s" % lyr.workspacePath)
            except arcpy.ExecuteError:
                logging.exception(arcpy.GetMessages(2))
            except ValueError:
                logging.info("no, error getting data source")
            except Exception as e:
                logging.warning("no, some other error: %s" % layer_path)
                logging.exception("\t" + e.args[0])
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
This file takes the path of any number of .lyr files as it's arguments. It changes the workspacePath of from S:\Infrastructure Planning\Spatial Data\StormWater\Database to O:\Data\Planning_IP\Spatial\Stormwater\Database.
""")
