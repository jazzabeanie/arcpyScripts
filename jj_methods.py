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
import logging
# see here for logging best practices: https://stackoverflow.com/questions/15727420/using-python-logging-in-multiple-modules

arcpy.env.workspace = r'O:\Data\Planning_IP\Admin\Staff\Jared\GIS\Tools\arcpyScripts\TestingDataset.gdb'
logging = logging.getLogger(__name__)


# TODO: create a bunch of functions that create test data sets. For example: add the function below, but let the list of verticies be passed in as an argument.
# def create_test_area_polygon(output):
#     """
#     returns an array of points used to create a polygon that will be used to create the test case.
#     """
#     print "directory = " + jj.get_directory_from_path(output)
#     print "name = " + jj.get_file_from_path(output)
#     arcpy.CreateFeatureclass_management(
#             jj.get_directory_from_path(output), # out_path
#             jj.get_file_from_path(output), # out_name
#             "POLYGON") # geometry_type
#             # "#", # template
#             # "DISABLED", # has_m
#             # "DISABLED", # has_z
#             # inputs["growth_model_polygon"]) # spatial_reference
#     array = arcpy.Array([arcpy.Point(471966.2812500,7858694.5000000),
#                          arcpy.Point(471895.5000000,7858701.0000000),
#                          arcpy.Point(471865.5000000,7858703.5000000),
#                          arcpy.Point(471844.0312500,7858706.0000000),
#                          arcpy.Point(471622.6875000,7858726.0000000),
#                          arcpy.Point(471389.3750000,7858747.5000000),
#                          arcpy.Point(469967.9687500,7858874.5000000),
#                          arcpy.Point(469973.7812500,7858974.5000000),
#                          arcpy.Point(469972.3125000,7858999.0000000),
#                          arcpy.Point(469971.6875000,7859029.0000000),
#                          arcpy.Point(469975.3125000,7859051.0000000),
#                          arcpy.Point(469980.9062500,7859076.0000000),
#                          arcpy.Point(469976.3125000,7859121.5000000),
#                          arcpy.Point(469971.6875000,7859153.0000000),
#                          arcpy.Point(469970.0625000,7859174.0000000),
#                          arcpy.Point(469974.3437500,7859201.5000000),
#                          arcpy.Point(469998.0312500,7859241.0000000),
#                          arcpy.Point(470036.7812500,7859313.0000000),
#                          arcpy.Point(470047.4062500,7859344.0000000),
#                          arcpy.Point(470069.3750000,7859444.0000000),
#                          arcpy.Point(470073.0937500,7859478.0000000),
#                          arcpy.Point(470075.0625000,7859514.5000000),
#                          arcpy.Point(470074.8125000,7859556.0000000),
#                          arcpy.Point(470073.5625000,7859620.0000000),
#                          arcpy.Point(470067.9062500,7859716.0000000),
#                          arcpy.Point(470046.4062500,7859801.5000000),
#                          arcpy.Point(470010.3750000,7859843.5000000),
#                          arcpy.Point(469898.5312500,7859872.5000000),
#                          arcpy.Point(469845.2187500,7859882.0000000),
#                          arcpy.Point(469831.9062500,7859899.0000000),
#                          arcpy.Point(469831.1562500,7859915.0000000),
#                          arcpy.Point(469830.7500000,7859925.0000000),
#                          arcpy.Point(469847.1875000,7859991.0000000),
#                          arcpy.Point(469849.1875000,7860075.0000000),
#                          arcpy.Point(469851.6562500,7860109.0000000),
#                          arcpy.Point(469847.4375000,7860172.0000000),
#                          arcpy.Point(469838.5625000,7860231.0000000),
#                          arcpy.Point(469840.0312500,7860251.5000000),
#                          arcpy.Point(469818.8125000,7860315.0000000),
#                          arcpy.Point(469801.7812500,7860347.0000000),
#                          arcpy.Point(469815.8437500,7860404.0000000),
#                          arcpy.Point(469832.2187500,7860506.5000000),
#                          arcpy.Point(469837.5000000,7860506.0000000),
#                          arcpy.Point(470369.8750000,7860453.5000000),
#                          arcpy.Point(470400.2812500,7860773.0000000),
#                          arcpy.Point(470480.0937500,7860765.5000000),
#                          arcpy.Point(470515.1250000,7860762.0000000),
#                          arcpy.Point(470538.5312500,7860760.0000000),
#                          arcpy.Point(470558.4375000,7860758.0000000),
#                          arcpy.Point(470578.3437500,7860756.0000000),
#                          arcpy.Point(470598.2500000,7860754.5000000),
#                          arcpy.Point(470618.1562500,7860752.5000000),
#                          arcpy.Point(470638.0625000,7860750.5000000),
#                          arcpy.Point(470657.9687500,7860748.5000000),
#                          arcpy.Point(470677.8750000,7860747.0000000),
#                          arcpy.Point(470697.7812500,7860745.0000000),
#                          arcpy.Point(470717.6875000,7860743.0000000),
#                          arcpy.Point(470737.5937500,7860741.0000000),
#                          arcpy.Point(470757.5000000,7860739.5000000),
#                          arcpy.Point(470777.4062500,7860737.5000000),
#                          arcpy.Point(470797.3125000,7860735.5000000),
#                          arcpy.Point(470795.4375000,7860715.5000000),
#                          arcpy.Point(470794.0312500,7860700.5000000),
#                          arcpy.Point(470793.3125000,7860693.0000000),
#                          arcpy.Point(470792.8750000,7860688.5000000),
#                          arcpy.Point(470792.0937500,7860680.0000000),
#                          arcpy.Point(470790.9375000,7860668.0000000),
#                          arcpy.Point(470789.0625000,7860648.0000000),
#                          arcpy.Point(470828.8750000,7860644.0000000),
#                          arcpy.Point(470848.7812500,7860642.5000000),
#                          arcpy.Point(470868.6875000,7860640.5000000),
#                          arcpy.Point(470888.5937500,7860638.5000000),
#                          arcpy.Point(470908.4687500,7860636.5000000),
#                          arcpy.Point(470928.3750000,7860635.0000000),
#                          arcpy.Point(470948.2812500,7860633.0000000),
#                          arcpy.Point(470973.3125000,7860630.5000000),
#                          arcpy.Point(470975.9375000,7860658.5000000),
#                          arcpy.Point(470976.1875000,7860661.0000000),
#                          arcpy.Point(470987.2812500,7860672.5000000),
#                          arcpy.Point(470995.2187500,7860757.5000000),
#                          arcpy.Point(471005.2500000,7860756.5000000),
#                          arcpy.Point(471035.1875000,7860753.5000000),
#                          arcpy.Point(471067.5312500,7860750.5000000),
#                          arcpy.Point(471077.6562500,7860749.5000000),
#                          arcpy.Point(471086.9687500,7860845.0000000),
#                          arcpy.Point(471162.7812500,7860838.0000000),
#                          arcpy.Point(471251.1250000,7860842.0000000),
#                          arcpy.Point(471258.9687500,7860704.0000000),
#                          arcpy.Point(471344.4062500,7860709.0000000),
#                          arcpy.Point(471351.2187500,7860594.5000000),
#                          arcpy.Point(471357.3437500,7860560.5000000),
#                          arcpy.Point(471362.5000000,7860542.0000000),
#                          arcpy.Point(471371.6875000,7860518.0000000),
#                          arcpy.Point(471385.0625000,7860487.0000000),
#                          arcpy.Point(471400.4062500,7860457.5000000),
#                          arcpy.Point(471411.0937500,7860441.5000000),
#                          arcpy.Point(471420.4375000,7860429.5000000),
#                          arcpy.Point(471431.9375000,7860417.0000000),
#                          arcpy.Point(471448.7500000,7860403.5000000),
#                          arcpy.Point(471465.8437500,7860392.5000000),
#                          arcpy.Point(471492.5625000,7860381.0000000),
#                          arcpy.Point(471534.2187500,7860371.5000000),
#                          arcpy.Point(471561.5000000,7860370.5000000),
#                          arcpy.Point(471590.6250000,7860372.0000000),
#                          arcpy.Point(471619.5625000,7860379.5000000),
#                          arcpy.Point(471642.4375000,7860389.5000000),
#                          arcpy.Point(471872.5312500,7860509.5000000),
#                          arcpy.Point(471989.6875000,7860139.0000000),
#                          arcpy.Point(472010.8125000,7860053.0000000),
#                          arcpy.Point(472027.3125000,7859953.5000000),
#                          arcpy.Point(472037.2812500,7859795.5000000),
#                          arcpy.Point(472004.7500000,7859272.5000000),
#                          arcpy.Point(471964.3437500,7858942.5000000),
#                          arcpy.Point(471959.8750000,7858871.5000000),
#                          arcpy.Point(471959.3125000,7858801.0000000),
#                          arcpy.Point(471962.7812500,7858728.0000000),
#                          arcpy.Point(471966.2812500,7858694.5000000)])
#     polygon = arcpy.Polygon(array)
#     # Open an InsertCursor and insert the new geometry
#     cursor = arcpy.da.InsertCursor(output, ['SHAPE@'])
#     cursor.insertRow([polygon])
#     del cursor


def delete_if_exists(layer):
    """Deleted the passed in layer if it exists. This avoids errors."""
    if arcpy.Exists(layer):
        logging.warning("Deleting %s" % layer)
        arcpy.Delete_management(layer)


def arguments_exist():
    """Returns true if the file was called with arguments, false otherwise."""
    if arcpy.GetArgumentCount() != 0:
        return True
    else:
        return False


def field_in_feature_class(field_name, feature_class):
    """
    returns true if field (parameter 1), exists in feature class (parameter 2). returns false if not.
    See: https://epjmorris.wordpress.com/2015/04/22/how-can-i-check-to-see-if-an-attribute-field-exists-using-arcpy/
    """
    # return field_name in [field.name for field in arcpy.ListFields(feature_class)]
    fields = arcpy.ListFields(feature_class, field_name)
    if len(fields) == 1:
        return True
    else:
        return False


def return_tuple_of_args():
    """Takes all the arguments passed into the script, and puts them into a
    tuple."""
    args = tuple(arcpy.GetParameterAsText(i)
                 for i in range(arcpy.GetArgumentCount()))
    logging.debug("args = " + str(args))
    return args


def renameFieldMap(fieldMap, name_text):
	"""
	Sets the output fieldname of a FieldMap object. Used when creating FieldMappings.
	"""
	type_name = fieldMap.outputField
	type_name.name = name_text
	fieldMap.outputField = type_name


def calculate_external_field(target_layer, target_field, join_layer, join_field, output):
    """Calculates an target field from an field on another featre based on spatial intersect."""
    logging.debug("Calculating %s.%s from %s.%s" % (target_layer, target_field, join_layer, join_field))
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
    logging.debug("  Adding and calculating %s = %s" % (tmp_field_name, join_field))
    arcpy.AddField_management(join_layer_layer, tmp_field_name, join_field_object.type)
    arcpy.CalculateField_management(join_layer_layer, tmp_field_name, "!" + join_field + "!", "PYTHON", "")
    logging.debug("  Spatially joining %s to %s" % (join_layer, target_layer))
    arcpy.SpatialJoin_analysis(target_layer, join_layer, output)
    output_fields = arcpy.ListFields(output)
    new_fields = [f for f in output_fields if f.name not in original_field_names]
    logging.debug("  Calculating %s = %s" % (target_field, tmp_field_name))
    arcpy.CalculateField_management(output, target_field, "!" + tmp_field_name + "!", "PYTHON", "") # FIXME: may need to make null values 0.
    logging.debug("  Deleting joined fields:")
    for f in new_fields:
        if not f.required:
            logging.debug("    %s" % f.name)
            arcpy.DeleteField_management(output, f.name)
        else:
            logging.debug("    Warning: Cannot delete required field: %s" % f.name)


def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})


def get_file_from_path(path):
    """Returns the filename from a provided path."""
    head, tail = os.path.split(path)
    return tail or os.path.basename(head)


def get_directory_from_path(path):
    """Returns the directory from a provided path."""
    return os.path.dirname(os.path.abspath(path))


def test_print():
    """tests that methods in this module can be called."""
    logging.info("success")
    logging.debug("fail")


# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE,
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == '__main__':
    # TODO: set up logging so that I don't see 'No handlers could be found for logger "__main__"'
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

    print "Testing field_in_feature_class finds an existing field..."
    test_feature_class = "testing_field_in_feature_class"
    delete_if_exists(test_feature_class)
    arcpy.CreateFeatureclass_management(
            arcpy.env.workspace, # out_path
            test_feature_class, # out_name
            "POLYGON") # geometry_type
    arcpy.AddField_management(test_feature_class, "this_field_exists", "TEXT")
    if field_in_feature_class("this_field_exists", test_feature_class):
        print "  Pass"
    else:
        print "  Fail, %s field exists in %s, but tool returns False" % ("this_field_exists", test_feature_class)
    print "Testing field_in_feature_class doesn't find a missing field..."
    if field_in_feature_class("some_nonexistent_field", test_feature_class):
        print "  Fail, %s field is not in %s, but tool returns True" % ("some_nonexistent_field", test_feature_class)
        print "  Fields that exist:"
        for field in arcpy.ListFields(test_feature_class):
            print "    %s" % field.name
    else:
        print "  Pass"
    delete_if_exists(test_feature_class)
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
    print "------"

    print "Testing get_file_from_path..."
    some_path = r'C:\TempArcGIS\testing.gdb\foobar'
    if (get_file_from_path(some_path) == "foobar"):
        print "  pass"
    else:
        print "  fail"
    print "------"

    print "Testing get_directory_from_path..."
    some_path = r'C:\TempArcGIS\testing.gdb\foobar'
    if (get_directory_from_path(some_path) == "C:\\TempArcGIS\\testing.gdb"):
        print "  pass"
    else:
        print "  fail"
    print "------"

    print "Testing renameFieldMap"
    print "TODO"
    print "------"

    os.system('pause')
