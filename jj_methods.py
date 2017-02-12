# --------------------------------
# Name: jj_methods.py
# Purpose: To server commonly used methods.
# Author: Jared Johnston
# Created: 10/02/2017
# Copyright:   (c) TCC
# ArcGIS Version:   10.2
# Python Version:   2.7
# Template Source: https://blogs.esri.com/esri/arcgis/2011/08/04/pythontemplate/
# --------------------------------
import os # noqa
import sys # noqa
import arcpy


def delete_if_exists(layer):
    """Deleted the passed in layer if it exists. This avoids errors."""
    if arcpy.Exists(layer):
        logging.warning("Deleting %s" % layer) # noqa
        arcpy.Delete_management(layer)


def arguments_exist():
    """Returns true if the file was called with arguments, false otherwise."""
    if arcpy.GetArgumentCount() != 0:
        return True
    else:
        return False


def return_tuple_of_args():
    """Takes all the arguments passed into the script, and puts them into a
    tuple."""
    return tuple(arcpy.GetParameterAsText(i)
                 for i in range(arcpy.GetArgumentCount()))


# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE,
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == '__main__':
    print "Running test"
    print ""
    print "Testing delete_if_exists..."
    arcpy.CopyFeatures_management
    (r'R:\InfrastructureModels\Growth\Database\GrowthModelGMZ.mdb\GMZ',
     r'C:\TempArcGIS\scratchworkspace.gdb\testing_delete_if_exists')
    delete_if_exists
    (r'C:\TempArcGIS\scratchworkspace.gdb\testing_delete_if_exists')
    if arcpy.Exists(r'C:\TempArcGIS\scratchworkspace.gdb'
                    r'\testing_delete_if_exists'):
        print "  delete_if_exists failed. Layer not deleted."
    else:
        print "  pass"
    print "------"

    print "Testing arguments_exist..."
    if arguments_exist():
        print "  This file was called with arguments"
    else:
        print "  This file was not called with arguments"
    print "------"

    print "Testing return_tuple_of_args..."
    print "  Here are the passed in args: " + str(return_tuple_of_args())
