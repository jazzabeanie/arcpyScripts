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
#import jj_methods as m
import re

logging.basicConfig(filename='fix_lyr_file_paths.log',  # TODO: update log filename
                    level=logging.DEBUG,
                    format='%(asctime)s @ %(lineno)d: %(message)s',
                    datefmt='%Y-%m-%d,%H:%M:%S')
logging.warning("------")

# Layers:
test_lyr = r'C:\TempArcGIS\Major-Catchments.lyr'


def do_analysis(*args):
    """Changes the workspace of the layer file. Currently only works for .lyr files whose working space is the Stormwater\Database folder. Still in testing mode. See test_lyr above"""
    # TODO: set this up to operate on a bunch of files. os.path.walk may be an option? Or the location of each layer to operate on could be passed in as an argument.
    for layer in args:
        try:
            # TODO: check if layer is a groupd .lyr file and itterate over them all
            lyr = arcpy.mapping.Layer(layer)
            # print("\tlyr.workspacePath = %s" % lyr.workspacePath )
            current_working_directory = re.sub(r'\\[^\\]*$', r'', layer) # Parses input layer string to get the location
            # print("\tcurrent_working_directory = %s" % current_working_directory)
            if (lyr.datasetName != lyr.longName):
                # logging.warning("no, layer is nested: %s" % layer)
                logging.warning("no, layer: %s" % layer)
                logging.warning("datasetName =  %s" % lyr.datasetName)
                logging.warning("longName =  %s" % lyr.longName)
                # continue
                # print("This layer appears to be nested. This tool has not been tested for nested layer. Proceed with caution.")
                # logging.warning("This layer appears to be nested. This tool has not been tested for nested layer. Proceed with caution.")
                # raw_input("Press ENTER to continue.")
            # TODO: use the lyr.workspacePath to assign to the oldpath variable, then use regex to substitue r'S:\Infrastructure Planning\Spatial Data\StormWater' for r'O:\Data\Planning_IP\Spatial\Stormwater'
            # new_workspacePath = r'O:\Data\Planning_IP\Spatial\Stormwater\Database'
            new_workspacePath = re.sub(r'S:\\Infrastructure Planning\\Spatial Data\\StormWater', r'O:\Data\Planning_IP\Spatial\Stormwater', lyr.workspacePath, count=1)
            path_string_length = len(lyr.workspacePath)
            # print("lyr.workspacePath length = %s" % path_string_length)
            if (lyr.workspacePath[:59] == r'S:\Infrastructure Planning\Spatial Data\StormWater\Database'):
                logging.warning("yes: %s" % new_workspacePath)
                lyr.findAndReplaceWorkspacePath(lyr.workspacePath , new_workspacePath)
                lyr.saveACopy("%s\\fixed_%s" % (current_working_directory, lyr.datasetName))
            else:
                logging.warning("no, wrong workspace: %s" % lyr.workspacePath)
        except arcpy.ExecuteError:
            print arcpy.GetMessages(2)
            logging.warning(arcpy.GetMessages(2))
        except Exception as e:
            logging.warning("no, layer contains multiple files: %s" % layer)
            print "\t" + e.args[0]
            logging.warning("\t" + e.args[0])
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
        print(argv)
        do_analysis(*argv) # see here for help on #argv https://docs.python.org/2.7/tutorial/controlflow.html#unpacking-argument-lists # noqa
    else:
        print("""
This file takes the path of any number of .lyr files as it's arguments. It changes the workspacePath of from S:\Infrastructure Planning\Spatial Data\StormWater\Database to O:\Data\Planning_IP\Spatial\Stormwater\Database.
""")
