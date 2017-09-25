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
import re

arcpy.env.workspace = r'O:\Data\Planning_IP\Admin\Staff\Jared\GIS\Tools\arcpyScripts\TestingDataset.gdb'


def delete_if_exists(layer):
    """Deleted the passed in layer if it exists. This avoids errors."""
    if arcpy.Exists(layer):
        # logging.warning("Deleting %s" % layer) # TODO: make this write to
        # logging object in the file that calls it. Try: http://stackoverflow.com/questions/15727420/using-python-logging-in-multiple-modules
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
    args = tuple(arcpy.GetParameterAsText(i)
                 for i in range(arcpy.GetArgumentCount()))
    print "args = " + str(args)
    return args


def calculate_external_field(target_layer, target_field, join_layer, join_field, output):
    """Calculates an target field from an field on another featre based on spatial intersect."""
    print("Calculating %s.%s from %s.%s" % (target_layer, target_field, join_layer, join_field))
    delete_if_exists(output)
    original_fields = arcpy.ListFields(target_layer)
    original_field_names = [f.name for f in original_fields]
    join_layer_layer = "join_layer_layer"
    arcpy.MakeFeatureLayer_management(join_layer, join_layer_layer)
    tmp_field_name = "tmp_a035bh"
    try:
        join_field_object = arcpy.ListFields(join_layer, join_field)[0]
    except IndexError as e:
        raise IndexError("could not find %s in %s" % (join_field, join_layer))
    if len(arcpy.ListFields(join_layer, join_field)) > 1:
        raise AttributeError("Multiple fields found when searching for the %s in %s" % (join_field, join_layer))
    print("  Adding and calculating %s = %s" % (tmp_field_name, join_field))
    arcpy.AddField_management(join_layer_layer, tmp_field_name, join_field_object.type)
    arcpy.CalculateField_management(join_layer_layer, tmp_field_name, "!" + join_field + "!", "PYTHON", "")
    print("  Spatially joining %s to %s" % (join_layer, target_layer))
    arcpy.SpatialJoin_analysis(target_layer, join_layer, output)
    output_fields = arcpy.ListFields(output)
    new_fields = [f for f in output_fields if f.name not in original_field_names]
    print("  Calculating %s = %s" % (target_field, tmp_field_name))
    arcpy.CalculateField_management(output, target_field, "!" + tmp_field_name + "!", "PYTHON", "") # FIXME: may need to make null values 0.
    print("  Deleting joined fields:")
    for f in new_fields:
        if not f.required:
            print("    %s" % f.name)
            arcpy.DeleteField_management(output, f.name)
        else:
            print("    Warning: Cannot delete required field: %s" % f.name)


def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})


def test_print():
    """tests that methods in this module can be called."""
    print "method called successfully"


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
    print "------"

    print "Testing calculate_external_field..."
    output = "testing_calculate_external_field"
    calculate_external_field("one_field", "first", "two_fields", "first", output)
    with arcpy.da.SearchCursor(output, "first") as cursor:
        print("cursor %s" % cursor)
        for row in cursor:
            regexp = re.compile('two_fields.*')
            assert(regexp.match("%s" % row))
    print "  pass"
