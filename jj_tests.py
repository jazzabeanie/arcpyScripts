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
# testing = True
testing = False

logging.basicConfig(filename='jj_tests.log',
    level=logging.INFO,
    format='%(asctime)s @ %(lineno)d: %(message)s',
    datefmt='%Y-%m-%d,%H:%M:%S')


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
    jj.log("Testing redistributePolygon...")
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
    redistributePolygonInputs["layer_to_redistribute_to"] = redistribution_test
    redistributePolygonInputs["layer_to_be_redistributed"] = arcpy.env.workspace + "\\growth_model_polygon_test"
    redistributePolygonInputs["output_filename"] = "redistributed"
    redistributePolygonInputs["fields_to_be_distributed"] = ["Dwelling_1"]
    jj.log("  Testing number of fields")
    redistributePolygonInputs["distribution_method"] = 2
    jj.log("    Fields in %s" % redistributePolygonInputs["layer_to_redistribute_to"])
    redistribution_layer_fields = [f.name for f in arcpy.ListFields(redistributePolygonInputs["layer_to_redistribute_to"])]
    for field in redistribution_layer_fields:
        jj.log("      %s" % field)
    jj.log("    Fields in %s" % redistributePolygonInputs["layer_to_be_redistributed"])
    layer_to_be_redistributed_fields = [f.name for f in arcpy.ListFields(redistributePolygonInputs["layer_to_be_redistributed"])]
    for field in layer_to_be_redistributed_fields:
        jj.log("      %s" % field)
    jj.redistributePolygon(redistributePolygonInputs)
    jj.log("    Fields in %s" % redistributePolygonInputs["output_filename"])
    output_fields = [f.name for f in arcpy.ListFields(redistributePolygonInputs["output_filename"])]
    for field in output_fields:
        jj.log("      %s" % field)
    if True:
        jj.log("  Pass?")
    jj.log("  Testing invalid distribution method is caught")
    for method in [0, "blah", 6.5]:
        redistributePolygonInputs["distribution_method"] = method
        try:
            jj.redistributePolygon(redistributePolygonInputs)
        except AttributeError as e:
            if re.match('distribution method must be either 1, 2 or 3', e.args[0]):
                jj.log("    Pass")
            else:
                jj.log("    Fail")
        except Exception as e:
            jj.log("    Fail:")
            jj.log("      " + e.args[0])
    jj.log("  Testing invalid field is caught")
    redistributePolygonInputs["fields_to_be_distributed"] = ["nonexistent_field"]
    try:
        jj.redistributePolygon(redistributePolygonInputs)
        # TODO: manually raise an error
    except AttributeError as e:
        if re.match('.*does not exist.*', e.args[0]):
            jj.log("    Pass")
        else:
            jj.log("    Fail: wrong error message")
            jj.log("      " + e.args[0])
    except Exception as e:
        jj.log("    Fail: Some other exception raised")
        jj.log("      " + e.args[0])
    jj.log("  Testing number of properties method:")
    redistributePolygonInputs["fields_to_be_distributed"] = ["Dwelling_1"]
    redistributePolygonInputs["distribution_method"] = 2
    jj.redistributePolygon(redistributePolygonInputs)
    with arcpy.da.SearchCursor(redistributePolygonInputs["output_filename"], ['Dwelling_1']) as cursor:
        for row in cursor:
            if row[0] == 10:
                jj.log("    Pass")
            else:
                jj.log("    Fail: Dwelling_1 should be 10")
    jj.log("    Testing sums are equal:")
    #
    redistributed_count = 0
    with arcpy.da.SearchCursor(redistributePolygonInputs["output_filename"], "Dwelling_1") as cursor:
        for row in cursor:
            redistributed_count += row[0]
    #
    layer_to_be_redistributed_count = 0
    with arcpy.da.SearchCursor(redistributePolygonInputs["output_filename"], "Dwelling_1") as cursor:
        for row in cursor:
            layer_to_be_redistributed_count += row[0]
    if layer_to_be_redistributed_count == redistributed_count:
        jj.log("      Pass")
    else:
        jj.log("      Fail: sum of dewllings is not equal for layer_to_be_redistributed (%s) and output (%s)" % (layer_to_be_redistributed_count, redistributed_count))
    jj.log("  Testing area method:")
    redistributePolygonInputs["distribution_method"] = 1
    jj.redistributePolygon(redistributePolygonInputs)
    for row in arcpy.da.SearchCursor(redistributePolygonInputs["output_filename"], ['Dwelling_1']):
        if row[0] == 4:
            jj.log("    Pass")
        else:
            jj.log("    Fail: Dwelling_1 should be 4")
    jj.log("    Testing sums are equal:")
    # Recalculate redistributed_count:
    redistributed_count = 0
    with arcpy.da.SearchCursor(redistributePolygonInputs["output_filename"], "Dwelling_1") as cursor:
        for row in cursor:
            redistributed_count += row[0]
    if layer_to_be_redistributed_count == redistributed_count:
        jj.log("      Pass")
    else:
        jj.log("      Fail: sum of dewllings is not equal for layer_to_be_redistributed (%s) and output (%s)" % (layer_to_be_redistributed_count, redistributed_count))
    jj.log("    Testing for rounding:")
    gm_test_area = jj.create_basic_polygon(output="gm_test_area", left_x=479580, lower_y=7871650, right_x=479770, upper_y=7871700)
    arcpy.AddField_management(gm_test_area, "Dwelling_1", "LONG")
    arcpy.CalculateField_management(in_table=gm_test_area, field="Dwelling_1", expression="1", expression_type="PYTHON_9.3", code_block="")
    redistribution_areas = jj.create_polygon("redistribution_areas", [(479580, 7871650), (479580, 7871700), (479644, 7871700), (479644, 7871650), (479580, 7871650)], [(479644, 7871650), (479644, 7871700), (479707, 7871700), (479707, 7871650), (479644, 7871650)], [(479707, 7871650), (479707, 7871700), (479770, 7871700), (479770, 7871650), (479707, 7871650)])
    redistributePolygonInputs["distribution_method"] = 1
    redistributePolygonInputs["layer_to_redistribute_to"] = redistribution_areas
    redistributePolygonInputs["layer_to_be_redistributed"] = gm_test_area
    redistributePolygonInputs["output_filename"] = "redistributed"
    redistributePolygonInputs["fields_to_be_distributed"] = ["Dwelling_1"]
    jj.redistributePolygon(redistributePolygonInputs)
    total_dwellings = jj.get_sum("Dwelling_1", redistributePolygonInputs["output_filename"])
    if total_dwellings == 1:
        jj.log("      Pass")
    elif total_dwellings == 0:
        jj.log("      Fail: total dwellings in output was 0. This means that rounding errors are accumulating.")
    else:
        jj.log("      Fail: total dwellings in %s should be 1, but was %s" % (redistributePolygonInputs["output_filename"], total_dwellings))
    jj.log("    Testing for integerising:")
    # TODO: create a situation that would produce and error if the values were integerised instead of rounded.
    gm_test_area = jj.create_basic_polygon(output="gm_test_area", left_x=479580, lower_y=7871650, right_x=479770, upper_y=7871700)
    arcpy.AddField_management(gm_test_area, "Dwelling_1", "LONG")
    arcpy.CalculateField_management(in_table=gm_test_area, field="Dwelling_1", expression="1", expression_type="PYTHON_9.3", code_block="")
    redistribution_areas = jj.create_polygon(
        "redistribution_areas",
        [(479580, 7871650), (479580, 7871700), (479707, 7871700), (479707, 7871650), (479580, 7871650)],
        [(479707, 7871650), (479707, 7871700), (479770, 7871700), (479770, 7871650), (479707, 7871650)])
    redistributePolygonInputs["distribution_method"] = 1
    redistributePolygonInputs["layer_to_redistribute_to"] = redistribution_areas
    redistributePolygonInputs["layer_to_be_redistributed"] = gm_test_area
    redistributePolygonInputs["output_filename"] = "redistributed"
    redistributePolygonInputs["fields_to_be_distributed"] = ["Dwelling_1"]
    jj.redistributePolygon(redistributePolygonInputs)
    total_dwellings = jj.get_sum("Dwelling_1", redistributePolygonInputs["output_filename"])
    if total_dwellings == 1:
        jj.log("      Pass")
    elif total_dwellings == 0:
        jj.log("      Fail: total dwellings in output was 0. This means that decimas are being integerised, not rounded")
    else:
        jj.log("      Fail: total dwellings in %s should be 1, but was %s. This error was unexpected and needs to be investigated." % (redistributePolygonInputs["output_filename"], total_dwellings))
    jj.log("------")


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


def test_create_basic_polygon():
    print "Testing create_basic_polygon..."
    print "  Testing a polygon is created with default params..."
    output = arcpy.env.workspace + "\\test_create_polygon"
    jj.create_basic_polygon()
    number_of_features = jj.get_sum("OBJECTID", output)
    if number_of_features==1:
        print "    Pass"
    else:
        print "    Fail: creates %s features by default, should be 1" % number_of_features
    print "------"


def test_for_each_feature():
    print "Testing test_for_each_features..."
    def error_throwing_cb():
        print "Fail, features not containing an argument is called"
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
    print "check cb takes 1 argument..."
    try:
        jj.for_each_feature(for_each_test_feature_class, error_throwing_cb)
        print "    Fail, no exception thrown"
    except TypeError as e:
        print "    Pass, exception thrown if cb takes no argument"
    print "------"


def test_join_csv():
    print "Testing join_csv joins fields..."
    csv_file = open(".\\test.csv", "w")
    csv_file.write("character,species\njake,dog\nfinn,human")
    csv_file.close()
    polygon = jj.create_basic_polygon()
    arcpy.AddField_management(
        in_table=polygon,
        field_name="character",
        field_type="TEXT")
    arcpy.CalculateField_management(
        in_table=polygon,
        field="character",
        expression='"finn"',
        expression_type="PYTHON_9.3",
        code_block="")
    jj.join_csv(
        in_data=polygon,
        in_field="character",
        csv=".\\test.csv",
        csv_field="character")
    if jj.field_in_feature_class("species", polygon):
        print "  Pass"
    else:
        print "  Fail: %s field not found in %s" % ("species", polygon)
        print "  The following fields were found: "
        for f in arcpy.ListFields(polygon):
            print "    %s" % f.name
    print "Testing join_csv raises error if csv_field starts with digit..."
    csv_file = open(".\\test.csv", "w")
    csv_file.write("1character,species\njake,dog\nfinn,human")
    csv_file.close()
    polygon = jj.create_basic_polygon()
    arcpy.AddField_management(
        in_table=polygon,
        field_name="character",
        field_type="TEXT")
    arcpy.CalculateField_management(
        in_table=polygon,
        field="character",
        expression='"finn"',
        expression_type="PYTHON_9.3",
        code_block="")
    try:
        jj.join_csv(
            in_data=polygon,
            in_field="character",
            csv=".\\test.csv",
            csv_field="1character")
        print "  Fail: no error was raised, even though csv file started with a digit"
    except ValueError as e:
        print("  Pass")
    except Exception as e:
        print "  Fail: an unexpected error was raised."
    # TODO: test all fields in csv file. If any start with a digit, they won't be joined.
    print "------"


def test_get_sum():
    print "TODO: Testing get_sum..."
    pass # TODO
    print "------"


if __name__ == '__main__':
    try:
        jj.log("Running tests")
        jj.log("")
        # test_delete_if_exists()
        # test_arguments_exist()
        # test_field_in_feature_class()
        # test_return_tuple_of_args()
        # test_calculate_external_field()
        # test_get_file_from_path()
        # test_get_directory_from_path()
        # test_renameFieldMap()
        # test_redistributePolygon()
        # test_for_each_feature()
        # test_create_polygon()
        # test_for_each_feature()
        test_join_csv()
        # test_create_basic_polygon()
        # test_get_sum()
    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
        logging.exception(arcpy.GetMessages(2))
    except Exception as e:
        print e.args[0]
        logging.exception(e.args[0])

    os.system('pause')
