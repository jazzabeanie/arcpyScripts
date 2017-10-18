# --------------------------------
# Name: jj_tests.py
# Purpose: To test commonly used methods.
# Author: Jared Johnston
# Created: 11/10/2017
# Copyright:   (c) TCC
# ArcGIS Version:   10.5
# Python Version:   2.7
# Template Source: https://blogs.esri.com/esri/arcgis/2011/08/04/pythontemplate/
# --------------------------------
import os # noqa
import arcpy
import re
import logging
import jj_methods as jj

arcpy.env.workspace = r'O:\Data\Planning_IP\Admin\Staff\Jared\GIS\Tools\arcpyScripts\TestingDataset.gdb'
testing = True


def test_delete_if_exists():
    print "Testing delete_if_exists..."
    arcpy.CopyFeatures_management
    (r'R:\InfrastructureModels\Growth\Database\GrowthModelGMZ.mdb\GMZ',
     r'C:\TempArcGIS\scratchworkspace.gdb\testing_delete_if_exists')
    jj.delete_if_exists
    (r'C:\TempArcGIS\scratchworkspace.gdb\testing_delete_if_exists')
    if arcpy.Exists(r'C:\TempArcGIS\scratchworkspace.gdb'
                    r'\testing_delete_if_exists'):
        print "  delete_if_exists failed. Layer not deleted."
    else:
        print "  pass"
    print "------"

def test_field_in_feature_class():
    print "Testing field_in_feature_class finds an existing field..."
    test_feature_class = "testing_field_in_feature_class"
    jj.delete_if_exists(test_feature_class)
    arcpy.CreateFeatureclass_management(
            arcpy.env.workspace, # out_path
            test_feature_class, # out_name
            "POLYGON") # geometry_type
    arcpy.AddField_management(test_feature_class, "this_field_exists", "TEXT")
    if jj.field_in_feature_class("this_field_exists", test_feature_class):
        print "  Pass"
    else:
        print "  Fail, %s field exists in %s, but tool returns False" % ("this_field_exists", test_feature_class)
    print "Testing field_in_feature_class doesn't find a missing field..."
    if jj.field_in_feature_class("some_nonexistent_field", test_feature_class):
        print "  Fail, %s field is not in %s, but tool returns True" % ("some_nonexistent_field", test_feature_class)
        print "  Fields that exist:"
        for field in arcpy.ListFields(test_feature_class):
            print "    %s" % field.name
    else:
        print "  Pass"
    jj.delete_if_exists(test_feature_class)
    print "------"


def test_arguments_exist():
    print "Testing arguments_exist..."
    if jj.arguments_exist():
        print "  This file was called with arguments"
    else:
        print "  This file was not called with arguments"
    print "------"

def test_return_tuple_of_args():
    print "Testing return_tuple_of_args..."
    print "  Here are the passed in args: " + str(jj.return_tuple_of_args())
    print "------"

def test_calculate_external_field():
    print "Testing calculate_external_field..."
    output = "testing_calculate_external_field"
    jj.calculate_external_field("one_field", "first", "two_fields", "first", output)
    with arcpy.da.SearchCursor(output, "first") as cursor:
        print("cursor %s" % cursor)
        for row in cursor:
            regexp = re.compile('two_fields.*')
            assert(regexp.match("%s" % row))
    print "  pass"
    print "------"


def test_get_file_from_path():
    print "Testing get_file_from_path..."
    some_path = r'C:\TempArcGIS\testing.gdb\foobar'
    if (jj.get_file_from_path(some_path) == "foobar"):
        print "  pass"
    else:
        print "  fail"
    print "------"


def test_get_directory_from_path():
    print "Testing get_directory_from_path..."
    some_path = r'C:\TempArcGIS\testing.gdb\foobar'
    if (jj.get_directory_from_path(some_path) == "C:\\TempArcGIS\\testing.gdb"):
        print "  pass"
    else:
        print "  fail"
    print "------"


def test_renameFieldMap():
    print "Testing renameFieldMap"
    print "TODO"
    print "------"


def test_redistributePolygon():
    # TODO: improve the tests for this method. All input data should be created on the fly, more tests should be added, more polygons should be added, etc.
    print "Testing redistributePolygon..."
    left_x = 479582.11
    right_x = 479649.579
    lower_y = 7871595.813
    upper_y = 7871628.886
    array = [(left_x,lower_y),
         (left_x,upper_y),
         (right_x,upper_y),
         (right_x,lower_y),
         (left_x,lower_y)]
    redistribution_test = arcpy.env.workspace + "\\redistribution_test_layer"
    jj.delete_if_exists(redistribution_test)
    jj.create_polygon(redistribution_test, array)
    redistributePolygonInputs = {}
    redistributePolygonInputs["redistribution_layer_name"] = redistribution_test
    redistributePolygonInputs["growth_model_polygon"] = arcpy.env.workspace + "\\growth_model_polygon_test"
    redistributePolygonInputs["output_filename"] = "redistributed"
    redistributePolygonInputs["field_list"] = ["Dwelling_1"]
    print "  Testing invalid distribution method is caught"
    for method in [0, "blah", 6.5]:
        redistributePolygonInputs["distribution_method"] = method
        try:
            jj.redistributePolygon(redistributePolygonInputs)
        except AttributeError as e:
            if e.args[0] == 'distribution method must be either 1, 2 or 3':
                print "    Pass"
            else:
                print "    Fail"
        except Exception as e:
            print "    Fail:"
            print "      " + e.args[0]
    print "  Testing number of properties method:"
    redistributePolygonInputs["distribution_method"] = 2
    jj.redistributePolygon(redistributePolygonInputs)
    with arcpy.da.SearchCursor(redistributePolygonInputs["output_filename"], ['Dwelling_1']) as cursor:
        for row in cursor:
            if row[0] == 10:
                print "    Pass"
            else:
                print "    Fail: Dwelling_1 should be 10"
    print "  Testing area method:"
    redistributePolygonInputs["distribution_method"] = 1
    jj.redistributePolygon(redistributePolygonInputs)
    for row in arcpy.da.SearchCursor(redistributePolygonInputs["output_filename"], ['Dwelling_1']):
        if row[0] == 4:
            print "    Pass"
        else:
            print "    Fail: Dwelling_1 should be 4"
    print "------"


def test_create_polygon():
    print "Testing create_polygon..."
    print "  Testing create a polygon that intersects a point ..."
    array = [(479509.625,7871431.255),
         (479509.625,7871508.742),
         (479563.712,7871508.742),
         (479563.712,7871431.255),
         (479509.625,7871431.255)]
    output = arcpy.env.workspace + "\\test_create_polygon"
    jj.delete_if_exists(output)
    jj.create_polygon(output, array)
    feature_layer = "test_create_polygon_feature_layer"
    jj.delete_if_exists(feature_layer)
    arcpy.MakeFeatureLayer_management(output, feature_layer)
    arcpy.SelectLayerByLocation_management(feature_layer, "INTERSECT", "one_field")
    selected = arcpy.Describe(feature_layer).FIDSet
    if selected:
        print "    Pass"
    else:
        print "    Fail: tool doesn't create shape in expected location or doens't create shape at all (%s)" % output
    print "  Testing create a polygon that doesn't intersects a point ..."
    array = [(479579.725,7871431.255),
         (479579.725,7871508.742),
         (479593.812,7871508.742),
         (479593.812,7871431.255),
         (479579.725,7871431.255)]
    output = arcpy.env.workspace + "\\test_create_polygon"
    jj.delete_if_exists(output)
    jj.create_polygon(output, array)
    jj.delete_if_exists(feature_layer)
    feature_layer = "test_create_polygon_feature_layer"
    arcpy.MakeFeatureLayer_management(output, feature_layer)
    arcpy.SelectLayerByLocation_management(feature_layer, "INTERSECT", "one_field")
    print "    Selected: %s" % arcpy.Describe(feature_layer).FIDSet
    selected = arcpy.Describe(feature_layer).FIDSet
    if selected == "":
        print "    Pass"
    else:
        print "    Fail: tool doesn't create shape in expected location or selection feature location has changed (%s)" % output
    print "------"


def test_for_each_feature():
    print "Testing test_for_each_features..."
    def increase(feature_layer):
        global count
        count+=1
    def check_only_1_feature(feature_layer):
        feature_count = arcpy.GetCount_management(feature_layer)
        if feature_count.getOutput(0) == u'1':
            print "    Pass"
        else:
            print "    Fail: multiple objects selected in %s" % feature_layer
    shape1 = [(479509.625,7871431.255),
         (479509.625,7871508.742),
         (479563.712,7871508.742),
         (479563.712,7871431.255),
         (479509.625,7871431.255)]
    shape2 = [(479609.625,7871431.255),
         (479609.625,7871508.742),
         (479663.712,7871508.742),
         (479663.712,7871431.255),
         (479609.625,7871431.255)]
    shape3 = [(479709.625,7871431.255),
         (479709.625,7871508.742),
         (479763.712,7871508.742),
         (479763.712,7871431.255),
         (479709.625,7871431.255)]
    for_each_test_feature_class = r'O:\Data\Planning_IP\Admin\Staff\Jared\GIS\Tools\arcpyScripts\TestingDataset.gdb\for_each_test_feature_class'
    jj.delete_if_exists(for_each_test_feature_class)
    jj.create_polygon(for_each_test_feature_class, shape1, shape2, shape3)
    print "  Only 1 object seleted..."
    jj.for_each_feature(for_each_test_feature_class, check_only_1_feature)
    print "  Every feature is itterated over..."
    global count
    count = 0
    jj.for_each_feature(for_each_test_feature_class, increase)
    if count == 3:
        print "    Pass"
    else:
        print "    Fail, count = %s (supposed to be 3)" % count
    print "------"


if __name__ == '__main__':
    # TODO: set up logging so that I don't see 'No handlers could be found for logger "__main__"'
    print "Running tests"
    print ""
    # test_delete_if_exists()
    # test_arguments_exist()
    # test_field_in_feature_class()
    # test_return_tuple_of_args()
    # test_calculate_external_field()
    # test_get_file_from_path()
    # test_get_directory_from_path()
    # test_renameFieldMap()
    test_redistributePolygon()
    # test_for_each_featuretest_create_polygon()
    # test_for_each_feature()

    os.system('pause')
