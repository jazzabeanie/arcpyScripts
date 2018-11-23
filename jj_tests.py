from __future__ import division
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
import sys # noqa
import arcpy
import logging
import json
import csv
import imp
import re
import jj_methods as jj
from datetime import datetime



def _bar(itterable):
    return itterable

jj.bar = _bar # to disable progress bar

# arcpy.env.workspace = r'O:\Data\Planning_IP\Admin\Staff\Jared\GIS\Tools\arcpyScripts\TestingDataset.gdb'
arcpy.env.workspace = arcpy.env.scratchGDB
# testing = True
testing = False

logging.basicConfig(filename='jj_tests.log',
    level=logging.DEBUG,
    format='%(asctime)s @ %(lineno)d: %(message)s',
    datefmt='%Y-%m-%d,%H:%M:%S')

logging.debug("workspace = %s" % arcpy.env.scratchGDB)

def log(text):
    print(text)
    logging.debug(text)


def test_delete_if_exists():
    print "Testing delete_if_exists..."
    basic_polygon = jj.create_basic_polygon()
    jj.delete_if_exists(basic_polygon)
    if arcpy.Exists(basic_polygon):
        print "  delete_if_exists failed. Layer not deleted."
    else:
        print "  pass"
    print "------"


def test_is_polygon():
    print "Testing is_polygon..."
    basic_polygon = jj.create_basic_polygon()
    if jj.is_polygon(basic_polygon):
        print "  Pass"
    else:
        print "  Fail: is_polygon did not return true when passed a polygon"
    basic_point = jj.create_point()
    try:
        if jj.is_polygon(basic_point):
            print("  Fail: is polygon returned True for a point")
        else:
            print("  Pass")
    except Error as e:
        print("  Fail: An error was encountered")
        print(e.args)
    print "Testing is_polygon with logical operators..."
    if not (jj.is_polygon(basic_polygon) and jj.is_polygon(basic_point)):
        print("  Pass")
    else:
        print("  Fail: both is_polygon(basic_polygon) and is_polygon(basic_point) returned true")



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

def test_add_external_area_field():
    print("Testing add_external_area_field...")
    left_x = 479560  # TODO: use this in the test dataset
    mid_left_x = 479580
    mid_right_x = 479600
    right_x = 479620
    lower_y = 7871500
    upper_y = 7871600
    source_data = jj.create_polygon(
        "add_external_area_field_in_features", [
            (mid_left_x, lower_y),
            (mid_left_x, upper_y),
            (right_x, upper_y),
            (right_x, lower_y),
            (mid_left_x, lower_y)])
    layer_with_area_to_grab = jj.create_polygon(
        "area_to_grab", [
            (left_x, lower_y),
            (left_x, upper_y),
            (mid_right_x, upper_y),
            (mid_right_x, lower_y),
            (left_x, lower_y)])
    basic_point = jj.create_point()
    print("  Testing point inputs raises an error...")
    try:
        output = jj.add_external_area_field(
            source_data,
            "external_area",
            # "add_external_area_field_invalid_input",
            basic_point,
            dissolve=False)
        print("    Fail: no error was raised.")
    except AttributeError as e:
        print("    Pass")

    print("  Testing basic inputs...")
    output = jj.add_external_area_field(
        source_data,
        "external_area",
        layer_with_area_to_grab,
        dissolve=False)
    print("    Testing new field is added...")
    if jj.field_in_feature_class("external_area", output):
        print("      Pass")
    else:
        print("      Fail: %s does not contain the new field" % output)
    print("    Testing new field contains the expected values...")
    with arcpy.da.SearchCursor(output, ["external_area"]) as cursor:
        for row in cursor:
            if row[0] == 2000:
                print("      Pass")
            else:
                print("      Fail: external area should have been 2000, but was %s" % row[0])
    print("    Testing tool returns new dataset")
    if str(output) == str(source_data):
        print("      Fail: output and source_data should not be the same file (output=%s, source_data=%s)" % (output, source_data))
    else:
        print("      Pass")
    print("  Testing conflicting filename is not an issue")
    # conflicting_file = jj.create_basic_polygon(
    #     output = "add_external_area_field_in_features_with_new_field")
    # output = jj.add_external_area_field(
    #     source_data,
    #     "external_area",
    #     layer_with_area_to_grab,
    #     dissolve=False)
    print("    TODO")
    print("  Testing dissolve make tool calculate correctly")
    print("    Testing area that needs dissolving, but didn't get it")
    layer_with_area_to_grab_divided = jj.create_polygon(
        "area_to_grab_divided",
        [
            (left_x, lower_y),
            (left_x, upper_y-50),
            (mid_right_x, upper_y-50),
            (mid_right_x, lower_y),
            (left_x, lower_y)
        ], [
            (left_x, upper_y-50),
            (left_x, upper_y),
            (mid_right_x, upper_y),
            (mid_right_x, upper_y-50),
            (left_x, upper_y-50)
        ])
    output = jj.add_external_area_field(
        source_data,
        "external_area",
        layer_with_area_to_grab_divided,
        dissolve=False)
    with arcpy.da.SearchCursor(output, ["external_area"]) as cursor:
        for row in cursor:
            if row[0] == 2000:
                print("      Fail: this should not have produced the correct output since dissolve was set to False")
            else:
                # Should fail because dissolve is required
                print("      Pass")
    print("    Testing area that needs dissolving, and gets it")
    output = jj.add_external_area_field(
        source_data,
        "external_area",
        layer_with_area_to_grab_divided,
        dissolve=True)
    with arcpy.da.SearchCursor(output, ["external_area"]) as cursor:
        for row in cursor:
            if row[0] == 2000:
                print("      Pass")
            else:
                # Should pass here
                print("      Fail: external area should have been 2000, but was %s" % row[0])
    print("  Testing 1/1 external area outside in_features adds 0, not Null")
    in_features_not_overlapping = jj.create_polygon(
        "in_features_not_overlapping", [
            (left_x, lower_y),
            (left_x, upper_y),
            (mid_left_x, upper_y),
            (mid_left_x, lower_y),
            (left_x, lower_y)])
    non_intersecting_area = jj.create_polygon(
        "non_intersecting_area", [
            (mid_right_x, lower_y),
            (mid_right_x, upper_y),
            (right_x, upper_y),
            (right_x, lower_y),
            (mid_right_x, lower_y)])
    output = jj.add_external_area_field(
        in_features_not_overlapping,
        "external_area",
        non_intersecting_area,
        dissolve=False)
    with arcpy.da.SearchCursor(output, ["external_area"]) as cursor:
        for row in cursor:
            if row[0] == 0:
                print("      Pass")
            else:
                print("      Fail: external area should have been 0, but was %s" % row[0])
    print("  Testing 1/2 external area outside in_features adds 0, not Null")
    in_features_some_overlapping = jj.create_polygon(
        "in_features_some_overlapping",
        [
            (left_x, lower_y),
            (left_x, upper_y),
            (mid_left_x, upper_y),
            (mid_left_x, lower_y),
            (left_x, lower_y)
        ],
        [
            (mid_left_x, lower_y),
            (mid_left_x, upper_y),
            (mid_right_x+10, upper_y),
            (mid_right_x+10, lower_y),
            (mid_left_x, lower_y)
        ])
    singular_intersecting_area = jj.create_polygon(
        "singular_intersecting_area", [
            (mid_right_x, lower_y),
            (mid_right_x, upper_y),
            (right_x, upper_y),
            (right_x, lower_y),
            (mid_right_x, lower_y)])
    output = jj.add_external_area_field(
        in_features_some_overlapping,
        "external_area",
        singular_intersecting_area,
        dissolve=False)
    with arcpy.da.SearchCursor(output, ["external_area"]) as cursor:
        for row in cursor:
            if row[0] in (0, 1000.0):
                print("      Pass")
            else:
                print("      Fail: external area should have been 0 or 1000, but was %s" % row[0])
    # This was created to test a known problem, but it's passing. Not sure what's going on.
    print("  Testing with known problematic dataset")
    wingate = r'O:\Data\Planning_IP\Admin\Staff\Jared\Land_Use_Monitoring\tools\distribute_growth\testing_datasets.gdb\add_external_area_in_features'
    nda = r'O:\Data\Planning_IP\Admin\Staff\Jared\Land_Use_Monitoring\tools\distribute_growth\testing_results.gdb\net_developable_area'
    output = jj.add_external_area_field(
        in_features=wingate,
        new_field_name="external_area",
        layer_with_area_to_grab=nda,
        dissolve=True)
    with arcpy.da.SearchCursor(output, ["external_area"]) as cursor:
        for row in cursor:
            if int(row[0]) == 833883:
                print("      Pass")
            else:
                print("      Fail: external area should have been 833883, but was %s" % row[0])

def test_arguments_exist():
    print "Testing arguments_exist..."
    if jj.arguments_exist():
        print "  This file was called with arguments"
    else:
        print "  This file was not called with arguments"
    print "------"

# def test_return_tuple_of_args():
#     # I don't think this function is actually used.
#     print "Testing return_tuple_of_args..."
#     print "  Here are the passed in args: " + str(jj.return_tuple_of_args())
#     print "------"

def test_calculate_external_field():
    print "Testing calculate_external_field..."
    print "  Testing external field is joined..."
    one_field = jj.create_basic_polygon(output="calculate_external_one_field")
    arcpy.AddField_management(one_field, "first", "TEXT")
    arcpy.CalculateField_management(one_field,  "first", "get_text()", "PYTHON_9.3", """def get_text():
            return 'from one_field'""")
    two_fields = jj.create_basic_polygon()
    arcpy.AddField_management(two_fields, "first", "TEXT")
    arcpy.AddField_management(two_fields, "second", "TEXT")
    # arcpy.CalculateField_management(in_table, field, expression, {expression_type}, {code_block})
    arcpy.CalculateField_management(two_fields,  "first", "get_text()", "PYTHON_9.3", """def get_text():
            return 'from two_fields'""")
    arcpy.CalculateField_management(two_fields,  "second", "get_text()", "PYTHON_9.3", """def get_text():
            return 'from two_fields'""")
    output = "testing_calculate_external_field"
    jj.calculate_external_field(one_field, "first", two_fields, "first", output)
    with arcpy.da.SearchCursor(output, "first") as cursor:
        for row in cursor:
            regexp = re.compile('from two_fields')
            assert(regexp.match("%s" % row))
    print "    pass"
    print "  Testing tmp_field_name is deleted..."
    output = "testing_join_field_is_deleted"
    conflicting_layer = jj.create_basic_polygon(output="calculate_external_conflicting_layer")
    arcpy.AddField_management(conflicting_layer, "first", "TEXT")
    arcpy.AddField_management(conflicting_layer, "second", "TEXT")
    arcpy.AddField_management(conflicting_layer, "delete_me", "TEXT")
    arcpy.CalculateField_management(
        conflicting_layer,
        "first",
        "get_text()",
        "PYTHON_9.3",
        """def get_text():
            return 'from conflicting_layer'""")
    arcpy.CalculateField_management(
        conflicting_layer,
        "second",
        "get_text()",
        "PYTHON_9.3",
        """def get_text():
            return 'from conflicting_layer'""")
    arcpy.CalculateField_management(
        conflicting_layer,
        "delete_me",
        "get_text()",
        "PYTHON_9.3",
        """def get_text():
            return 'this text should not be visible'""")
    jj.delete_if_exists(output)
    try:
        output = jj.calculate_external_field(one_field, "first", conflicting_layer, "delete_me", output)
        print("    fail: no error was raised")
    except AttributeError as e:
        print("    pass")
    except Exception as e:
        print("    fail: some other error %s" % e.args[0])
    jj.log("  Testing output must be provided...")
    try:
        output = jj.calculate_external_field(one_field, "first", conflicting_layer, "delete_me")
        print("    fail: no execption raised")
    except TypeError as e:
        print("    pass: exception raised")
    jj.log("  Testing using distance_field_name options raises an error...")
    try:
        output = jj.calculate_external_field(one_field, "first", two_fields, "first", output="testing_kwargs", match_option="CLOSEST", distance_field_name="distance_to", search_radius=100)
        print("    fail - no error was raised")
    except AttributeError as e:
        print("    pass")
    print "  Testing output=None changes target_layer in place..."
    output = jj.calculate_external_field(one_field, "first", two_fields, "first", output=None)
    with arcpy.da.SearchCursor(one_field, "first") as cursor:
        for row in cursor:
            regexp = re.compile('from two_fields')
            assert(regexp.match("%s" % row))
    print "    pass"
    jj.log("  Testing Spatial Join keyword arguments affect join behaviour...")
    test_join_method = jj.create_basic_polygon(output="test_join_method")
    # create a new field to calculate
    arcpy.AddField_management(test_join_method, "no_data", "TEXT")
    arcpy.CalculateField_management(test_join_method,  "no_data", "get_none()", "PYTHON_9.3", """def get_none():
            return None""")
    shape_near_by = jj.create_basic_polygon(output="shape_near_by", left_x=479570, lower_y=7871450, right_x=479572, upper_y=7871452)
    # create a new field to get data form
    arcpy.AddField_management(shape_near_by, "some_data", "TEXT")
    arcpy.CalculateField_management(shape_near_by,  "some_data", "get_text()", "PYTHON_9.3", """def get_text():
            return 'wazoo'""")
    jj.delete_if_exists("no_data_joined")
    jj.delete_if_exists("data_joined")
    no_data_joined = jj.calculate_external_field(test_join_method, "no_data", shape_near_by, "some_data", output="no_data_joined")
    data_joined = jj.calculate_external_field(test_join_method, "no_data", shape_near_by, "some_data", output="data_joined", search_radius=100)
    with arcpy.da.SearchCursor(no_data_joined, "no_data") as cursor:
        for row in cursor:
            assert(row[0] == None)
    with arcpy.da.SearchCursor(data_joined, "no_data") as cursor:
        for row in cursor:
            regexp = re.compile('wazoo')
            assert(regexp.match("%s" % row))
    print "    pass"
    print "------"


def test_get_file_from_path():
    print "  Testing get_file_from_path..."
    some_path = r'C:\TempArcGIS\testing.gdb\foobar'
    if (jj.get_file_from_path(some_path) == "foobar"):
        print "    pass"
    else:
        print "    fail"
    print "  Testing get_file_from_path with where \\ not found in string..."
    some_string = r'foobar'
    if (jj.get_file_from_path(some_string) == "foobar"):
        print "    pass"
    else:
        print "    fail. results = %s" % jj.get_directory_from_path(some_string)
    print "  Testing get_file_from_path for non string..."
    some_non_string = 2016
    try:
        if (jj.get_file_from_path(some_non_string) == "2016"):
            print "    pass"
        else:
            print "    fail. results = %s" % jj.get_directory_from_path(some_non_string)
    except Exception as e:
        print "    fail. Exception caught."
        print "    %s" % e.arge[0]
    print "------"


def test_get_directory_from_path():
    print "Testing get_directory_from_path..."
    print "  Testing get_directory_from_path with standard path..."
    some_path = r'C:\TempArcGIS\testing.gdb\foobar'
    if (jj.get_directory_from_path(some_path) == "C:\\TempArcGIS\\testing.gdb"):
        print "    pass"
    else:
        print "    fail. results = %s" % jj.get_directory_from_path(some_path)
    print "  Testing get_directory_from_path with where \\ not found in string..."
    some_string = r'foobar'
    try:
        path = jj.get_directory_from_path(some_string)
        if (path == ""):
            print "    fail, path was an empty string. No error raised even though there was no path in the string"
        else:
            print "    fail. Should raise an error. path = %s" % path
        print "------"
    except AttributeError as e:
        print("    pass. get_directory_from_path raises an error")


def test_renameFieldMap():
    print "Testing renameFieldMap"
    print "TODO"
    print "------"


def test_add_layer_count():
    print "Testing add_layer_count..."
    far_left_x = 479580
    left_x = 479587.5
    mid_x = 479595
    right_x = 479600
    far_right_x =479610
    bottom_y = 7871600
    top_y = 7871590
    boundary_layer_mod = jj.create_basic_polygon(
        output="boundary_layer_mod",
        left_x = far_left_x,
        lower_y = bottom_y,
        right_x = 479602,
        upper_y = top_y)
    boundary_layer = jj.create_basic_polygon(
        output="boundary_layer",
        left_x = far_left_x,
        lower_y = bottom_y,
        right_x = 479602,
        upper_y = top_y)
    far_left_shape = [
        (far_left_x, bottom_y),
        (far_left_x, top_y),
        (left_x, top_y),
        (left_x, bottom_y),
        (far_left_x, bottom_y)]
    left_shape = [
        (left_x, bottom_y),
        (left_x, top_y),
        (mid_x, top_y),
        (mid_x, bottom_y),
        (left_x, bottom_y)]
    mid_shape = [
        (mid_x, bottom_y),
        (mid_x, top_y),
        (right_x, top_y),
        (right_x, bottom_y),
        (mid_x, bottom_y)]
    right_shape = [
        (right_x, bottom_y),
        (right_x, top_y),
        (far_right_x, top_y),
        (far_right_x, bottom_y),
        (right_x, bottom_y)]
    count_layer = "count_layer"
    jj.delete_if_exists(count_layer)
    count_layer = jj.create_polygon(count_layer, far_left_shape, left_shape, mid_shape, right_shape)
    count_field_name = "count_field"

    def test_by_area():
        result = jj.add_layer_count(boundary_layer, count_layer, count_field_name, by_area=True)
        def test_adds_a_field():
            print "  Testing add_layer_count adds a field..."
            fields = [field.name for field in arcpy.ListFields(result)]
            if count_field_name in fields:
                print "    Pass"
            else:
                print "    Fail: %s not found in results. The following fiels were found: %s" % (count_field_name, fields)

        def test_counts_correctly_by_area():
            print("  Testing: newly added field counts the number of occurences of")
            print("  count_layer that are inside the input boundary_layer by total amount")
            print("  of area that falls within each shape...")
            with arcpy.da.SearchCursor(result, count_field_name) as cursor:
                for row in cursor:
                    if int(row[0]*10)/10 == 3.2:
                        print("    Pass")
                    else:
                        print("    Fail: result was %s. Should have been 1.3" %
                                row[0])

        def test_points_raises_an_error():
            print("  Testing: if add_layer_count is called with the by_area")
            print("  method set to true, and point feature classes are")
            print("  passed in, an error should be raised...")
            point_1 = jj.create_point(output="point_1")
            point_2 = jj.create_point(output="point_2")
            polygon_1 = jj.create_basic_polygon(output="polygon_1")
            try:
                jj.add_layer_count(point_1, point_2, "some_field", by_area=True)
                print("    Fail: no error raised.")
            except AttributeError as e:
                print("    Pass")
            except Exception as e:
                print("    Fail: some other error raised. See logs for details")
                logging.exception(e.args[0])
            try:
                jj.add_layer_count(polygon_1, point_2, "some_field", by_area=True)
                print("    Fail: no error raised.")
            except AttributeError as e:
                print("    Pass")
            except Exception as e:
                print("    Fail: some other error raised. See logs for details")
                logging.exception(e.args[0])
            try:
                jj.add_layer_count(point_1, polygon_1, "some_field", by_area=True)
                print("    Fail: no error raised.")
            except AttributeError as e:
                print("    Pass")
            except Exception as e:
                print("    Fail: some other error raised. See logs for details")
                logging.exception(e.args[0])


        test_points_raises_an_error()
        test_adds_a_field()
        test_counts_correctly_by_area()

    def test_by_centroid():
        result = jj.add_layer_count(boundary_layer_mod, count_layer, count_field_name)

        def test_counts_correctly_by_centroid():
            print("  Testing: newly added field counts the number of occurences of")
            print("  count_layer that are inside the input boundary_layer_mod by each centroid")
            print("  that falls within each shape...")
            with arcpy.da.SearchCursor(result, count_field_name) as cursor:
                for row in cursor:
                    if int(row[0]*10)/10 == 3.0:
                        print("    Pass")
                    else:
                        print("    Fail: result was %s. Should have been 3.0" % row[0])
            print("  Testing: real dataset")
            real_result = jj.add_layer_count(
                in_features=r'O:\Data\Planning_IP\Admin\Staff\Jared\Land_Use_Monitoring\Residential_Estates\residential_estates.gdb\residential_estate_extents',
                count_features=r'O:\Data\Planning_IP\Spatial\Base Layers\Snapshots.gdb\Land_2016_July',
                new_field_name="properties_2016",
                output="estates_with_consumption")
            with arcpy.da.SearchCursor(real_result, "properties_2016", "estate_name = 'Bushland Beach'") as cursor:
                for row in cursor:
                    if row[0] == 1:
                        jj.log("    pass")
                    else:
                        jj.log("    fail: number of joined features should have been 1 but was %s" % row[0])

        def test_points_can_be_used_as_count_layer():
            print("  Testing: point can be used as the count_layer if by_area is")
            print("  not set to True...")
            point_1 = jj.create_point(output="point_1")
            point_2 = jj.create_point(output="point_2")
            polygon_1 = jj.create_basic_polygon(output="polygon_1")
            try:
                jj.add_layer_count(polygon_1, point_1, "some_field")
                print("    TODO: write tests")
            except AttributeError as e:
                print("    Fail: an Attribute error was raised")

        def test_original_layer_is_modified():
            print("  Testing that the input layer is not modified when no output provided")
            if jj.field_in_feature_class(count_field_name, boundary_layer_mod):
                print("    pass")
            else:
                print("    fail")

        result_w_output = jj.add_layer_count(boundary_layer, count_layer, count_field_name, output="add_layer_count_w_output")

        def test_original_layer_is_not_modified():
            print("  Testing that the input layer is not modified when output provided")
            if jj.field_in_feature_class(count_field_name, boundary_layer):
                print("    fail")
            else:
                print("    pass")


        def test_new_field_already_exists():
            print("  Testing that if the field being added already exists, an error is raised")
            layer_with_field = jj.create_basic_polygon()
            arcpy.AddField_management(
                in_table=layer_with_field,
                field_name="existing_field",
                field_type="TEXT")
            try:
                jj.add_layer_count(
                    in_features=layer_with_field,
                    count_features=count_layer,
                    new_field_name="existing_field")
                print("    fail: no AttributeError was raised")
            except AttributeError as e:
                print("    pass")

        def test_invalid_existing_fields_are_caught():
            print("  Testing that if any fields used by the tool already exist, they are address, or an error is raised.")
            # boundary_layer
            # count_layer
            boundary_layer_w_TARGET_FID = jj.create_basic_polygon()
            arcpy.AddField_management(
                in_table=boundary_layer_w_TARGET_FID,
                field_name="TARGET_FID",
                field_type="TEXT")

            try:
                jj.add_layer_count(
                    in_features=boundary_layer_w_TARGET_FID,
                    count_features=count_layer,
                    new_field_name="some_count")
                print("    fail: no AttributeError was raised")
            except AttributeError as e:
                if re.match('.*TARGET_FID.*', e.args[0]):
                    log("    Pass")
                else:
                    log("    Fail: appropriate error not raised when TARGET_FID already existed")
                    log(e.args[0])

            boundary_layer_w_JOIN_FID = jj.create_basic_polygon()
            arcpy.AddField_management(
                in_table=boundary_layer_w_JOIN_FID,
                field_name="JOIN_FID",
                field_type="TEXT")
            try:
                jj.add_layer_count(
                    in_features=boundary_layer_w_JOIN_FID,
                    count_features=count_layer,
                    new_field_name="some_count")
                print("    fail: no AttributeError was raised")
            except AttributeError as e:
                if re.match('.*JOIN_FID.*', e.args[0]):
                    log("    Pass")
                else:
                    log("    Fail: appropriate error not raised when JOIN_FID already existed")
                    log(e.args[0])

            boundary_layer_w_Join_Count = jj.create_basic_polygon()
            arcpy.AddField_management(
                    in_table=boundary_layer_w_Join_Count,
                    field_name= "Join_Count",
                    field_type="TEXT")
            try:
                jj.add_layer_count(
                    in_features=boundary_layer_w_Join_Count,
                    count_features=count_layer,
                    new_field_name="some_count")
                print("    fail: no AttributeError was raised")
            except AttributeError as e:
                if re.match('.*Join_Count.*', e.args[0]):
                    log("    Pass")
                else:
                    log("    Fail: appropriate error not raised when Join_Count already existed")
                    log(e.args[0])

            boundary_layer_w_FREQUENCY = jj.create_basic_polygon()
            arcpy.AddField_management(
                    in_table=boundary_layer_w_FREQUENCY,
                    field_name= "FREQUENCY",
                    field_type="TEXT")
            try:
                jj.add_layer_count(
                    in_features=boundary_layer_w_FREQUENCY,
                    count_features=count_layer,
                    new_field_name="some_count")
                print("    fail: no AttributeError was raised")
            except AttributeError as e:
                if re.match('.*FREQUENCY.*', e.args[0]):
                    log("    Pass")
                else:
                    log("    Fail: appropriate error not raised when FREQUENCY already existed")
                    log(e.args[0])


        test_counts_correctly_by_centroid()
        test_points_can_be_used_as_count_layer()
        test_original_layer_is_modified()
        test_original_layer_is_not_modified()
        test_new_field_already_exists()
        # test_invalid_existing_fields_are_caught()

    # test_by_area()
    test_by_centroid()

def test_redistributePolygon():
    # TODO: improve the tests for this method. All input data should be created on the fly, more tests should be added, more polygons should be added, etc.
    log("Testing redistributePolygon...")
    left_x = 479582.11
    mid_x = 479649.579
    right_x = 479773.05
    lower_y = 7871640
    upper_y = 7871680
    layer_to_redistribute_to = arcpy.env.workspace + "\\layer_to_redistribute_to"
    jj.delete_if_exists(layer_to_redistribute_to)
    # This array creates an area that is around 40% of the growth model polygon.
    jj.create_polygon(layer_to_redistribute_to, [
         (left_x,lower_y),
         (left_x,upper_y),
         (mid_x,upper_y),
         (mid_x,lower_y),
         (left_x,lower_y)], [
         (mid_x,lower_y),
         (mid_x, upper_y),
         (right_x, upper_y),
         (right_x, lower_y),
         (mid_x, lower_y)
         ])
    layer_to_be_redistributed = arcpy.env.workspace + "\\layer_to_be_redistributed"
    jj.delete_if_exists(layer_to_be_redistributed)
    jj.create_polygon(layer_to_be_redistributed, [
         (left_x,lower_y),
         (left_x,upper_y),
         (right_x,upper_y),
         (right_x,lower_y),
         (left_x,lower_y)])
    arcpy.AddField_management(layer_to_be_redistributed, "Dwelling_1", "SHORT")
    arcpy.CalculateField_management(layer_to_be_redistributed,  "Dwelling_1", "get_12()", "PYTHON_9.3", """def get_12():
            return 12""")
    redistributePolygonInputs = {}
    redistributePolygonInputs["layer_to_redistribute_to"] = layer_to_redistribute_to
    redistributePolygonInputs["layer_to_be_redistributed"] = layer_to_be_redistributed
    redistributePolygonInputs["output_filename"] = "output"
    redistributePolygonInputs["fields_to_be_distributed"] = ["Dwelling_1"]


    def testing_number_of_fields():
        log("  Testing number of fields")
        redistributePolygonInputs["distribution_method"] = 2
        redistribution_layer_fields = [f.name for f in
            arcpy.ListFields(redistributePolygonInputs["layer_to_redistribute_to"])]
        layer_to_be_redistributed_fields = [f.name for f in
            arcpy.ListFields(redistributePolygonInputs["layer_to_be_redistributed"])]
        logging.debug("    Fields in %s" % redistributePolygonInputs["layer_to_redistribute_to"])
        for field in redistribution_layer_fields:
            logging.debug("      %s" % field)
        logging.debug("    Fields in %s" % redistributePolygonInputs["layer_to_be_redistributed"])
        for field in layer_to_be_redistributed_fields:
            logging.debug("      %s" % field)
        jj.redistributePolygon(redistributePolygonInputs)
        output_fields = [f.name for f in arcpy.ListFields(redistributePolygonInputs["output_filename"])]
        logging.debug("    Fields in %s" % redistributePolygonInputs["output_filename"])
        for field in output_fields:
            logging.debug("      %s" % field)
        if (len(redistribution_layer_fields)-4 + len(layer_to_be_redistributed_fields)-4 == len(output_fields)-6):  # every feature class has OBJECTID, Shape, Shape_Length, and Shape_Area. The output also has Join_Count, and TARGET_FID
            log("    Pass")
        else:
            log("    Fail: the output has an unexpected number of fields")


    def testing_invalid_distribution_method_is_caught():
        log("  Testing invalid distribution method is caught")
        for method in [0, "blah", 6.5]:
            redistributePolygonInputs["distribution_method"] = method
            try:
                jj.redistributePolygon(redistributePolygonInputs)
            except AttributeError as e:
                if re.match('distribution method must be either 1, 2, 3, or the path to a feature class', e.args[0]):
                    log("    Pass")
                else:
                    log("    Fail: an invalid distribution method did not raise an AttributeError")
            except Exception as e:
                log("    Fail:")
                log("      " + e.args[0])


    def testing_invalid_field_is_caught():
        log("  Testing invalid field is caught")
        redistributePolygonInputs["fields_to_be_distributed"] = ["nonexistent_field"]
        try:
            jj.redistributePolygon(redistributePolygonInputs)
            raise ValueError
        except AttributeError as e:
            if re.match('.*does not exist.*', e.args[0]):
                log("    Pass")
            else:
                log("    Fail: wrong error message")
                log("      " + e.args[0])
        except ValueError as e:
            log("    Fail: redistributePolygon tool raises no error if pased a field that doesn't exist.")
        except Exception as e:
            log("    Fail: Some other exception raised")
            log("      " + e.args[0])


    def testing_number_of_properties_method():
        log("  Testing number of properties method:")
        log("    Testing simple distribution with no properties_layer provided:")
        redistributePolygonInputs["fields_to_be_distributed"] = ["Dwelling_1"]
        redistributePolygonInputs["distribution_method"] = 2
        jj.redistributePolygon(redistributePolygonInputs)
        with arcpy.da.SearchCursor(redistributePolygonInputs["output_filename"], ['OBJECTID', 'Dwelling_1']) as cursor:
            for row in cursor:
                if row[0] == 1 and row[1] == 9:
                    log("    Pass")
                elif row[0] == 2 and row[1] == 3:
                    log("    Pass")
                else:
                    log("    Fail: For Dwelling_1 should be 9 or 3, but was %s (for OBJECTID = %s)" % (row[1], row[0]))
        log("    Testing that the sum of dwelling in the input and output layers are equal:")
        #
        redistributed_count = 0
        with arcpy.da.SearchCursor(redistributePolygonInputs["output_filename"], "Dwelling_1") as cursor:
            for row in cursor:
                redistributed_count += row[0]
        #
        layer_to_be_redistributed_count = 0
        with arcpy.da.SearchCursor(redistributePolygonInputs["layer_to_be_redistributed"], "Dwelling_1") as cursor:
            for row in cursor:
                layer_to_be_redistributed_count += row[0]
        if layer_to_be_redistributed_count == redistributed_count:
            log("      Pass")
        else:
            log("      Fail: sum of dewllings is not equal for layer_to_be_redistributed (%s) and output (%s)" % (layer_to_be_redistributed_count, redistributed_count))
            log("  layer_to_be_redistributed = %s" % redistributePolygonInputs["layer_to_be_redistributed"])
            log("  output_filename = %s" % redistributePolygonInputs["output_filename"])


    def testing_custom_properties_layer():
        log("  Testing number of properties method with custom properties layer:")
        redistributePolygonInputs["fields_to_be_distributed"] = ["Dwelling_1"]
        redistributePolygonInputs["distribution_method"] = 2
        custom_properties_layer = jj.create_polygon(
            "testing_custom_properties",
            [
                (left_x+10, lower_y+10),
                (left_x+10, upper_y-10),
                (left_x+20, upper_y-10),
                (left_x+20, lower_y+10),
                (left_x+10, lower_y+10)
            ], [
                (left_x+20, lower_y+10),
                (left_x+20, upper_y-10),
                (left_x+30, upper_y-10),
                (left_x+30, lower_y+10),
                (left_x+20, lower_y+10)
            ], [
                (mid_x+20, lower_y+10),
                (mid_x+20, upper_y-10),
                (mid_x+30, upper_y-10),
                (mid_x+30, lower_y+10),
                (mid_x+20, lower_y+10)
            ])
        redistributePolygonInputs["properties_layer"] = custom_properties_layer
        jj.redistributePolygon(redistributePolygonInputs)
        with arcpy.da.SearchCursor(redistributePolygonInputs["output_filename"], ['OBJECTID', 'Dwelling_1']) as cursor:
            for row in cursor:
                if row[0] == 1 and row[1] == 8:
                    log("    Pass")
                elif row[0] == 2 and row[1] == 4:
                    log("    Pass")
                else:
                    log("    Fail: For Dwelling_1 should be 8 or 4, but was %s (for OBJECTID = %s)" % (row[1], row[0]))


    def testing_area_method():
        log("  Testing area method:")
        log("    Testing 40% of area yeilds 40% of population:")
        redistributePolygonInputs["distribution_method"] = 1
        jj.redistributePolygon(redistributePolygonInputs)
        with arcpy.da.SearchCursor(redistributePolygonInputs["output_filename"], ['OBJECTID', 'Dwelling_1']) as cursor:
            for row in cursor:
                if row[0] == 1 and row[1] == 4:
                    log("      Pass")
                elif row[0] == 2 and row[1] == 8:
                    log("      Pass")
                else:
                    log("      Fail: Dwelling_1 should be 4, but was %s" % row[0])

    def testing_generic_distribution_method():
        def generic_distribution():
            log("  Testing even distribution for generic distribution method (distribution method provided by another feature class):")
            net_developable_area = jj.create_polygon(
                "net_developable_area",
                [(mid_x-10, lower_y),
                (mid_x-10, upper_y),
                (mid_x+10, upper_y),
                (mid_x+10, lower_y),
                (mid_x-10, lower_y)])
            redistributePolygonInputs["distribution_method"] = net_developable_area
            jj.redistributePolygon(redistributePolygonInputs)
            with arcpy.da.SearchCursor(
                    redistributePolygonInputs["output_filename"],
                    ['Dwelling_1']
            ) as cursor:
                for row in cursor:
                    if row[0] == 6:
                        log("      Pass")
                    else:
                        log("      Fail: Dwelling_1 should be 6 in each area, but was %s" % row[0])

        def unever_distribution():
            log("  Testing uneven distribution method:")
            net_developable_area = jj.create_polygon(
                "net_developable_area",
                [(mid_x-5, lower_y),
                (mid_x-5, upper_y),
                (mid_x+15, upper_y),
                (mid_x+15, lower_y),
                (mid_x-5, lower_y)])
            redistributePolygonInputs["distribution_method"] = net_developable_area
            jj.redistributePolygon(redistributePolygonInputs)
            with arcpy.da.SearchCursor(
                    redistributePolygonInputs["output_filename"],
                    ['Dwelling_1']
            ) as cursor:
                for row in cursor:
                    if row[0] in (3, 9):
                        log("      Pass")
                    else:
                        log("      Fail: Dwelling_1 should be 3 and 9, in each area, but was %s" % row[0])

        def all_to_one():
            log("  Testing all distribution to one polygon:")
            net_developable_area = jj.create_polygon(
                "net_developable_area",
                [(mid_x+5, lower_y),
                (mid_x+5, upper_y),
                (mid_x+15, upper_y),
                (mid_x+15, lower_y),
                (mid_x+5, lower_y)])
            redistributePolygonInputs["distribution_method"] = net_developable_area
            jj.redistributePolygon(redistributePolygonInputs)
            with arcpy.da.SearchCursor(
                    redistributePolygonInputs["output_filename"],
                    ['Dwelling_1']
            ) as cursor:
                for row in cursor:
                    if row[0] in (12, 0):
                        log("      Pass")
                    else:
                        log("      Fail: Dwelling_1 should be 12 and 0, in each area, but was %s" % row[0])

        def no_exteral_but_with_properties():
            log("  Testing areas with no external areas, but with properties:")
            # This tests the case where data is to be distributed based on the area
            # of some feature class, but that feature class doesn't cover every
            # polygon. The case that this test was designed for was when growth was
            # to be distributed by Net Developable Area. In the case where growth
            # exists, but there is no net developable area, it should be assumed
            # that the growth will occur due to increased density. In this case
            # distribution should be performed by number of properties.

            # In the future, the distribution method should be provided as a list
            # of priorities. For example, you might want to first distribute by Net
            # Developable Area (by area), then by properties (by centroid), then by
            # area.
            sample_properties = jj.create_polygon(
                    "one_property_in_each",
                    [
                        (mid_x-20, lower_y+10),
                        (mid_x-20, upper_y-10),
                        (mid_x-10, upper_y-10),
                        (mid_x-10, lower_y+10),
                        (mid_x-20, lower_y+10)
                    ], [
                        (mid_x+10, lower_y+10),
                        (mid_x+10, upper_y-10),
                        (mid_x+20, upper_y-10),
                        (mid_x+20, lower_y+10),
                        (mid_x+10, lower_y+10)
                    ])
            net_developable_area_outside_inputs = jj.create_polygon(
                "net_developable_area_outside_inputs",
                [
                    (mid_x-5, upper_y+10),
                    (mid_x-5, upper_y+20),
                    (mid_x+15, upper_y+20),
                    (mid_x+15, upper_y+10),
                    (mid_x-5, upper_y+10)
                ])
            redistributePolygonInputs["distribution_method"] = net_developable_area_outside_inputs
            redistributePolygonInputs["properties_layer"] = sample_properties
            jj.redistributePolygon(redistributePolygonInputs)
            with arcpy.da.SearchCursor(
                    redistributePolygonInputs["output_filename"],
                    ['Dwelling_1']
            ) as cursor:
                for row in cursor:
                    if row[0] == 6:
                        log("      Pass")
                    else:
                        log("      Fail: Dwelling_1 should be 6 in each area, but was %s" % row[0])

        def custom_properties_docs_example():
            log("  Testing areas with no external areas, but with properties (docs example):")
            # This test the example given in the docs under the explanation of the
            # properties_layer attribute.
            redistributePolygonInputs["layer_to_redistribute_to"] = jj.create_polygon(
                    'no_external_but_w_prop_docs_to',
                    [
                        (479568.031311, 7871494.1203),
                        (479578.031311, 7871494.1203),
                        (479578.031311, 7871484.1203),
                        (479568.031311, 7871484.1203),
                        (479568.031311, 7871494.1203)
                    ], [
                        (479578.031311, 7871494.1203),
                        (479588.031311, 7871494.1203),
                        (479588.031311, 7871484.1203),
                        (479578.031311, 7871484.1203),
                        (479578.031311, 7871494.1203)
                    ]
                    )
            redistributePolygonInputs["layer_to_be_redistributed"] = jj.create_polygon(
                    'no_external_but_w_prop_docs_from',
                    [
                        (479578.031311, 7871494.1203),
                        (479583.031311, 7871494.1203),
                        (479583.031311, 7871484.1203),
                        (479578.031311, 7871484.1203),
                        (479573.031311, 7871484.1203),
                        (479573.031311, 7871494.1203),
                        (479578.031311, 7871494.1203)
                    ], [
                        (479583.031311, 7871484.1203),
                        (479583.031311, 7871494.1203),
                        (479588.031311, 7871494.1203),
                        (479593.031311, 7871494.1203),
                        (479593.031311, 7871484.1203),
                        (479588.031311, 7871484.1203),
                        (479583.031311, 7871484.1203)
                    ]
                    )
            arcpy.AddField_management(redistributePolygonInputs["layer_to_be_redistributed"], "Dwelling_1", "SHORT")
            arcpy.CalculateField_management(redistributePolygonInputs["layer_to_be_redistributed"],  "Dwelling_1", "get_number()", "PYTHON_9.3", """def get_number():
                return 16""")
            redistributePolygonInputs["distribution_method"] = 2
            redistributePolygonInputs["properties_layer"] = jj.create_polygon(
                    'no_external_but_w_prop_docs_properties',
                    [
                        (479576.022888, 7871487.88507),
                        (479576.022888, 7871489.88507),
                        (479578.022888, 7871489.88507),
                        (479582.022888, 7871489.88507),
                        (479582.022888, 7871487.88507),
                        (479578.022888, 7871487.88507),
                        (479576.022888, 7871487.88507)
                    ])
            redistributePolygonInputs["fields_to_be_distributed"] = ["Dwelling_1"]
            jj.redistributePolygon(redistributePolygonInputs)
            with arcpy.da.SearchCursor(redistributePolygonInputs["output_filename"], ['OBJECTID', 'Dwelling_1']) as cursor:
                for row in cursor:
                    if row[0] == 1 and row[1] == None:
                        log("    pass")
                    elif row[0] == 2 and row[1] == 24:
                        log("    pass")
                    else:
                        log("    fail: population should be either 0 or 24, but was %s" % row[1])

        def feature_layer_docs_example():
            log("  Testing feature layer distribution method (docs example):")
            log("       This tests the example given in the docs under the feature layer parameter section.")
            redistributePolygonInputs["layer_to_redistribute_to"] = jj.create_polygon(
                    'docs_layer_to_redistribute_to',
                    [
                        (479568.031311, 7871494.1203),
                        (479578.031311, 7871494.1203),
                        (479578.031311, 7871484.1203),
                        (479568.031311, 7871484.1203),
                        (479568.031311, 7871494.1203)
                    ], [
                        (479578.031311, 7871494.1203),
                        (479588.031311, 7871494.1203),
                        (479588.031311, 7871484.1203),
                        (479578.031311, 7871484.1203),
                        (479578.031311, 7871494.1203)
                    ]
                    )
            redistributePolygonInputs["layer_to_be_redistributed"] = jj.create_polygon(
                    'docs_layer_to_be_redistributed',
                    [
                        (479578.031311, 7871494.1203),
                        (479583.031311, 7871494.1203),
                        (479583.031311, 7871484.1203),
                        (479578.031311, 7871484.1203),
                        (479573.031311, 7871484.1203),
                        (479573.031311, 7871494.1203),
                        (479578.031311, 7871494.1203)
                    ], [
                        (479583.031311, 7871484.1203),
                        (479583.031311, 7871494.1203),
                        (479588.031311, 7871494.1203),
                        (479593.031311, 7871494.1203),
                        (479593.031311, 7871484.1203),
                        (479588.031311, 7871484.1203),
                        (479583.031311, 7871484.1203)
                    ]
                    )
            arcpy.AddField_management(redistributePolygonInputs["layer_to_be_redistributed"], "Dwelling_1", "SHORT")
            arcpy.CalculateField_management(redistributePolygonInputs["layer_to_be_redistributed"],  "Dwelling_1", "get_number()", "PYTHON_9.3", """def get_number():
                return 12""")
            redistributePolygonInputs["distribution_method"] = jj.create_polygon(
                    'docs_nda',
                    [
                        (479576.022888, 7871487.88507),
                        (479576.022888, 7871489.88507),
                        (479578.022888, 7871489.88507),
                        (479582.022888, 7871489.88507),
                        (479582.022888, 7871487.88507),
                        (479578.022888, 7871487.88507),
                        (479576.022888, 7871487.88507)
                    ])
            redistributePolygonInputs["fields_to_be_distributed"] = ["Dwelling_1"]
            jj.redistributePolygon(redistributePolygonInputs)
            with arcpy.da.SearchCursor(redistributePolygonInputs["output_filename"], ['OBJECTID', 'Dwelling_1']) as cursor:
                for row in cursor:
                    if row[0] == 1 and row[1] == 4:
                        log("    pass. OBJECTID 1 = 4")
                    elif row[0] == 2 and row[1] == 14:
                        log("    pass. OBJECTID 2 = 14")
                    else:
                        log("    fail: population should be either 4 or 14, but was %s. I think this might be an example of a rounding or decimal point loss error." % row[1])

        def feature_layer_as_properties_docs_example():
            log("  Testing an alternative properties layer (docs example):")
            log("       This tests the example given in the docs under the properties_layer (optional) section.")
            redistributePolygonInputs["layer_to_redistribute_to"] = jj.create_polygon(
                    'docs_layer_to_redistribute_to',
                    [
                        (479568.031311, 7871494.1203),
                        (479578.031311, 7871494.1203),
                        (479578.031311, 7871484.1203),
                        (479568.031311, 7871484.1203),
                        (479568.031311, 7871494.1203)
                    ], [
                        (479578.031311, 7871494.1203),
                        (479588.031311, 7871494.1203),
                        (479588.031311, 7871484.1203),
                        (479578.031311, 7871484.1203),
                        (479578.031311, 7871494.1203)
                    ]
                    )
            redistributePolygonInputs["layer_to_be_redistributed"] = jj.create_polygon(
                    'docs_layer_to_be_redistributed',
                    [
                        (479578.031311, 7871494.1203),
                        (479583.031311, 7871494.1203),
                        (479583.031311, 7871484.1203),
                        (479578.031311, 7871484.1203),
                        (479573.031311, 7871484.1203),
                        (479573.031311, 7871494.1203),
                        (479578.031311, 7871494.1203)
                    ], [
                        (479583.031311, 7871484.1203),
                        (479583.031311, 7871494.1203),
                        (479588.031311, 7871494.1203),
                        (479593.031311, 7871494.1203),
                        (479593.031311, 7871484.1203),
                        (479588.031311, 7871484.1203),
                        (479583.031311, 7871484.1203)
                    ]
                    )
            arcpy.AddField_management(redistributePolygonInputs["layer_to_be_redistributed"], "Dwelling_1", "SHORT")
            arcpy.CalculateField_management(redistributePolygonInputs["layer_to_be_redistributed"],  "Dwelling_1", "get_number()", "PYTHON_9.3", """def get_number():
                return 12""")
            redistributePolygonInputs["distribution_method"] = 2
            redistributePolygonInputs["properties_layer"] = jj.create_polygon(
                    'docs_nda_as_properties',
                    [
                        (479576.022888, 7871487.88507),
                        (479576.022888, 7871489.88507),
                        (479578.022888, 7871489.88507),
                        (479582.022888, 7871489.88507),
                        (479582.022888, 7871487.88507),
                        (479578.022888, 7871487.88507),
                        (479576.022888, 7871487.88507)
                    ])
            redistributePolygonInputs["fields_to_be_distributed"] = ["Dwelling_1"]
            jj.redistributePolygon(redistributePolygonInputs)
            with arcpy.da.SearchCursor(redistributePolygonInputs["output_filename"], ['OBJECTID', 'Dwelling_1']) as cursor:
                for row in cursor:
                    if row[0] == 1 and row[1] == 0:
                        log("    pass. OBJECTID 1 = 0")
                    elif row[0] == 2 and row[1] == 18:
                        log("    pass. OBJECTID 2 = 18")
                    else:
                        log("    fail: population should be either None or 18, but was %s." % row[1])

        def no_external_or_properties():
            log("  Testing areas where the net nevelopable area and the properties are both outside the input layer extents:")
            net_developable_area_outside_inputs = jj.create_polygon(
                "net_developable_area_outside_inputs",
                [
                    (mid_x-5, upper_y+10),
                    (mid_x-5, upper_y+20),
                    (mid_x+15, upper_y+20),
                    (mid_x+15, upper_y+10),
                    (mid_x-5, upper_y+10)
                ])
            redistributePolygonInputs["distribution_method"] = net_developable_area_outside_inputs
            sample_properties_outside = jj.create_polygon(
                    "properties_outside",
                    [
                        (mid_x-20, upper_y+10),
                        (mid_x-20, upper_y+20),
                        (mid_x-10, upper_y+20),
                        (mid_x-10, upper_y+10),
                        (mid_x-20, upper_y+10)
                    ], [
                        (mid_x+10, upper_y+10),
                        (mid_x+10, upper_y+20),
                        (mid_x+20, upper_y+20),
                        (mid_x+20, upper_y+10),
                        (mid_x+10, upper_y+10)
                    ])
            redistributePolygonInputs["properties_layer"] = sample_properties_outside
            jj.redistributePolygon(redistributePolygonInputs)
            with arcpy.da.SearchCursor(redistributePolygonInputs["output_filename"], ['OBJECTID', 'Dwelling_1']) as cursor:
                for row in cursor:
                    if row[0] == 1 and row[1] == 4:
                        log("      Pass")
                    elif row[0] == 2 and row[1] == 8:
                        log("      Pass")
                    else:
                        log("      Fail: Dwelling_1 should be 4 or 8, but was %s (for OBJECTID = %s)" % (row[1], row[0]))
                        log("      Actually, I think that the tool is behaving correctly and my test is wrong.")  # TODO: run this test in ArcMap to visually check the results

        # generic_distribution()
        # unever_distribution()
        # all_to_one()
        # no_exteral_but_with_properties()
        # custom_properties_docs_example()
        # feature_layer_docs_example()
        # feature_layer_as_properties_docs_example()
        no_external_or_properties()

    def testing_for_rounding():
        log("  Testing for rounding:")
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
            log("    Pass")
        elif total_dwellings == 0:
            log("    Fail: total dwellings in output was 0. This means that rounding errors are accumulating.")
        else:
            log("    Fail: total dwellings in %s should be 1, but was %s" % (redistributePolygonInputs["output_filename"], total_dwellings))


    def testing_for_integerising():
        log("  Testing for integerising:")
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
            log("    Pass")
        elif total_dwellings == 0:
            log("    Fail: total dwellings in output was 0. This means that decimals are being integerised, not rounded")
        else:
            log("    Fail: total dwellings in %s should be 1, but was %s. This error was unexpected and needs to be investigated." % (redistributePolygonInputs["output_filename"], total_dwellings))

    def testing_that_output_contains_full_path():
        log("  Testing that the output_filename value of the resulting dictionary contains the full path to the output layer...")
        if os.path.dirname(redistributePolygonInputs["output_filename"]):
            log("    Pass")
        else:
            log("    Fail: output_filename was not the full path (%s)" % redistributePolygonInputs["output_filename"])


    # testing_number_of_fields()
    # testing_invalid_distribution_method_is_caught()
    # testing_invalid_field_is_caught()
    # testing_number_of_properties_method()
    # testing_custom_properties_layer()
    # testing_area_method()
    testing_generic_distribution_method()
    # # testing_for_rounding() # tool currently has no way to combat this
    # testing_for_integerising()
    # testing_that_output_contains_full_path()
    log("------")


def test_create_point():
    print("Testing create_point...")
    print("  Testing defaults...")
    try:
        point = jj.create_point()
        if int(arcpy.GetCount_management(point).getOutput(0)) == 1:
            print("    pass")
        else:
            print("    fail: %s features created instead of 1" % int(arcpy.GetCount_management(points).getOutput(0)))
    except Exception as e:
        print("    fail")
        print e.args[0]
    #
    print("  Testing takes coordinates...")
    try:
        jj.create_point(523, 5223)
        print("    pass")
    except Exception as e:
        print("    fail: %s" % e.args[0])
    #
    print("  Testing takes output...")
    try:
        jj.delete_if_exists("somefile")
        jj.create_point(output="somefile")
        if arcpy.Exists("somefile"):
            print("    pass")
        else:
            print("    fail: 'somefile' not created")
    except Exception as e:
        print("    fail: %s" % e.args[0])
    print "------"


def test_create_points():
    print("Testing create_points...")
    print("  Testing arguments are compulsory...")
    try:
        jj.create_points()
    except AttributeError as e:
        print("    pass")
    try:
        jj.create_points(output="blah")
    except AttributeError as e:
        print("    pass")
    #
    print("  Testing invalid coordinates raises an error...")
    try:
        jj.create_points(1)
    except AttributeError as e:
        print("    pass")
    try:
        jj.create_points(((1, 5), 3))
    except AttributeError as e:
        print("    pass")
    #
    print("  Testing single list of coordinates creates a point...")
    try:
        points = jj.create_points(((1, 2), (2, 3)))
        if int(arcpy.GetCount_management(points).getOutput(0)) == 2:
            print("    pass")
        else:
            print("    fail: %s features created instead of 2" % int(arcpy.GetCount_management(points).getOutput(0)))
    except Exception as e:
        print("    fail")
        print e.args[0]
    #
    print("  Testing take an output filename")
    try:
        jj.create_points(((1, 2), (4, 5)), output="some_filename")
        if arcpy.Exists("some_filename"):
            print("    pass")
        else:
            print("    fail: some_filename not created")
    except Exception as e:
        print("    fail: %s" % e.args[0])
    #
    print("  Testing take an output path")
    try:
        jj.create_points(((2345, 523), (423, 2)), output="%s\\some_filename" % arcpy.env.scratchGDB)
        if arcpy.Exists("%s\\some_filename" % arcpy.env.scratchGDB):
            print("    pass")
        else:
            print("    fail: %s\\some_filename not created" % arcpy.env.scratchGDB)
    except Exception as e:
        print("    fail: %s" % e.args[0])
    print("  pass")
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
    point = jj.create_point(479520, 7871470)
    arcpy.SelectLayerByLocation_management(feature_layer, "INTERSECT", point)
    selected = arcpy.Describe(feature_layer).FIDSet
    if selected:
        print "    Pass"
    else:
        print "    Fail: tool doesn't create shape in expected location or doens't create shape at all (%s)" % output
    #
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
    point = jj.create_point(479520, 7871470)
    arcpy.SelectLayerByLocation_management(feature_layer, "INTERSECT", point)
    print "    Selected: %s" % arcpy.Describe(feature_layer).FIDSet
    selected = arcpy.Describe(feature_layer).FIDSet
    if selected == "":
        print "    Pass"
    else:
        print "    Fail: tool doesn't create shape in expected location or selection feature location has changed (%s)" % output
    print("  Testing create_polygon returns unicode string...")
    result = jj.create_polygon("create_polygon_output_type_test", array)
    if type(result) == type(u'blah'):
        print("    Pass")
    else:
        print("    Fail: type of result should have been 'unicode' but was %s" % type(result))
    print "------"


def test_create_basic_polygon():
    print "Testing create_basic_polygon..."
    print "  Testing a polygon is created with default params..."
    output = arcpy.env.workspace + "\\test_create_polygon"
    jj.delete_if_exists(output)
    jj.create_basic_polygon(output)
    number_of_features = jj.get_sum("OBJECTID", output)
    if number_of_features==1:
        print "    Pass"
    else:
        print "    Fail: creates %s features by default, should be 1" % number_of_features
    print("  Testing create_polygon returns a unicode string...")
    result = jj.create_basic_polygon()
    if type(result) == type(u'blah'):
        print("    Pass")
    else:
        print("    Fail: type of result should have been 'unicode' but was %s" % type(result))
    print "------"


def test_for_each_feature():
    print "Testing test_for_each_features..."
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
    for_each_test_feature_class = r'for_each_test_feature_class'
    jj.delete_if_exists(for_each_test_feature_class)
    jj.create_polygon(for_each_test_feature_class, shape1, shape2, shape3)


    def testing_callback_called_with_only_1_object_seleted():
        print "  testing callback called with only 1 object seleted..."


        def check_only_1_feature(feature_layer):
            feature_count = arcpy.GetCount_management(feature_layer)
            if int(feature_count.getOutput(0)) == 1:
                print "    Pass"
            else:
                print "    Fail: multiple objects selected in %s" % feature_layer

        jj.for_each_feature(for_each_test_feature_class, check_only_1_feature)


    def testing_every_feature_is_itterated_over():
        print "  testing every feature is itterated over..."


        def increase(feature_layer):
            global count
            count+=1

        global count
        count = 0
        jj.for_each_feature(for_each_test_feature_class, increase)
        if count == 3:
            print "    Pass"
        else:
            print "    Fail, count = %s (supposed to be 3)" % count


    def testing_callback_function_must_take_1_argument():
        print "  testing callback function must take 1 argument..."


        def error_throwing_cb():
            print "Fail, features not containing an argument is called"

        try:
            jj.for_each_feature(for_each_test_feature_class, error_throwing_cb)
            print "    Fail, no exception thrown"
        except TypeError as e:
            print "    Pass, exception thrown if cb takes no argument"


    def testing_extra_args_are_passed_to_cb():
        print "  testing extra args are passed to cb..."


        def checks_extra_args(feature_layer, check=False):
            if check is True:
                print "    Pass"
            else:
                print "    Fail: extra True argument not passed to callback function"

        jj.for_each_feature(for_each_test_feature_class, checks_extra_args, True)


    def test_where_clause_argument():
        print "  testing where_clause argument is used..."


        def checks_object_id_of_feature_passed_in(feature_layer):
            with arcpy.da.SearchCursor(feature_layer, "OBJECTID") as cursor:
                for row in cursor:
                    if row[0] == 1:
                        print "    Pass"
                    else:
                        print "    Fail: where_clause was not used"

        jj.for_each_feature(
                for_each_test_feature_class,
                checks_object_id_of_feature_passed_in,
                where_clause="OBJECTID=1")

    test_where_clause_argument()
    testing_extra_args_are_passed_to_cb()
    testing_every_feature_is_itterated_over()
    testing_callback_called_with_only_1_object_seleted()
    testing_callback_function_must_take_1_argument()
    print "------"


def test_join_csv():
    print("Testing join_csv...")
    print "  Testing join_csv returns new features class when output is provided..."
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
    jj.delete_if_exists("blah")
    output = jj.join_csv(
        in_data=polygon,
        in_field="character",
        csv=".\\test.csv",
        csv_field="character",
        output="blah")
    if jj.field_in_feature_class("species", polygon):
        print("    fail: csv was joined to the original layer")
    else:
        print("    pass")

    print "  Testing join_csv joins fields..."
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
        with arcpy.da.SearchCursor(polygon, field_names=["species"]) as cursor:
            for row in cursor:
                if row[0] in ("dog", "human"):
                    print("    Pass - column exists and values are correct")
    else:
        print "    Fail: %s field not found in %s" % ("species", polygon)
        print "    The following fields were found: "
        for f in arcpy.ListFields(polygon):
            print "    %s" % f.name
    print "  Testing join_csv raises error if csv_field starts with digit..."
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
        print("    logs should issues a warning about csv fields")
        print "    Fail: no error was raised, even though csv file started with a digit"
    except ValueError as e:
        print("    Pass")
    except Exception as e:
        print "    Fail: an unexpected error was raised."
    print("  pass")
    print "------"
    jj.delete_if_exists(".\\test.csv")


def test_get_sum():
    print "Testing get_sum..."
    point = jj.create_points(((234, 52), (245, 542)))
    arcpy.AddField_management(point, "value", "SHORT")
    arcpy.CalculateField_management(point,  "value", "10")
    value_sum = jj.get_sum("value", point)
    try:
        assert(value_sum == 20)
        print("  pass")
    except AssertionError as e:
        print("  fail: sum was not 20 as expected")
    print "------"


def test_export_to_csv():
    print("Testing export_to_csv...")
    print("  Testing basic polygon is exported to csv file...")
    print(" arcpy.Exists('testing_export_to_csv') = %s" % arcpy.Exists('testing_export_to_csv'))
    jj.delete_if_exists("testing_export_to_csv")
    some_feature_class = jj.create_basic_polygon("testing_export_to_csv")
    output_csv = r'C:\delete_me.csv'
    jj.delete_if_exists(output_csv)
    jj.export_to_csv(some_feature_class, output_csv)
    if arcpy.Exists(output_csv):
        print("    pass")
        jj.delete_if_exists(output_csv)
    else:
        print("    fail")


def test_list_contents_of():
    print("Testing list_contents_of...")
    temp_gdb = arcpy.CreateFileGDB_management(
        out_folder_path="C:\\",
        out_name="delete_me.gdb")
    print("  Testing that workspace is preserved...")
    results = jj.list_contents_of(temp_gdb)
    if str(arcpy.env.workspace) == str(temp_gdb):
        print("    fail: workspace was changed to the listing geodatabase")
    else:
        print("    pass: workspace was not changed to the list geodatabase")
    print("  Testing that error is raised if .gdb not provided...")
    try:
        jj.list_contents_of("blah")
        print("    fail: no error raised when geodatabase string not provided")
    except AttributeError as e:
        print("    pass")
    print("  Testing that all feature classes are listed...")
    jj.create_basic_polygon("%s\\foobar" % temp_gdb)
    results = jj.list_contents_of(temp_gdb)
    if "foobar" in results:
        print("    pass")
    else:
        print("    fail: 'foobar' not found in %s" % results)
    print("  Testing wildcard...")
    jj.create_basic_polygon("%s\\foobar" % temp_gdb)
    jj.create_basic_polygon("%s\\hidden" % temp_gdb)
    results = jj.list_contents_of(temp_gdb, "foobar")
    if "foobar" in results and "hidden" not in results:
        print("    pass")
    else:
        print("    fail: wildcard not working. 'foobar' not found, or 'hidden' found in %s" % results)


def test_get_duplicates():
    jj.log("Testing get_duplicates...")
    jj.log("  testing basic example...")
    some_fc = jj.create_points(coords_list=((479578, 7871429), (479580, 7871430), (479582, 7871435), (479582, 7871445), (479582, 7871439)), output="testing_get_duplicates")
    logging.debug("adding some_field")
    arcpy.AddField_management(
        in_table=some_fc,
        field_name="some_field",
        field_type="TEXT")
    logging.debug("writing all data in some_field")
    arcpy.CalculateField_management(some_fc, "some_field", '"blah"')
    logging.debug("writing changing only first feature")
    with arcpy.da.UpdateCursor(some_fc, ["some_field"], where_clause='"OBJECTID" = 1') as cursor:
        for row in cursor:
            row[0] = "blee"
            cursor.updateRow(row)
    with arcpy.da.UpdateCursor(some_fc, ["some_field"], where_clause='"OBJECTID" = 2') as cursor:
        for row in cursor:
            row[0] = "blee"
            cursor.updateRow(row)
    with arcpy.da.UpdateCursor(some_fc, ["some_field"], where_clause='"OBJECTID" = 5') as cursor:
        for row in cursor:
            row[0] = "bloo"
            cursor.updateRow(row)
    logging.debug("printing some_field")
    # with arcpy.da.SearchCursor(some_fc, ["OBJECTID", "some_field"]) as cursor:
    #     for row in cursor:
    #         print("    %s = %s" % (row[0], row[1]))
    duplicates = jj.get_duplicates(some_fc, "some_field")
    if len(duplicates) == 2:
        print("    pass")
    else:
        print("    fail: duplicates should have been 'blah' and 'blee', but were %s" % duplicates)



if __name__ == '__main__':
    try:
        logging.info("Running tests")
        logging.info("")
        # test_delete_if_exists()
        # test_is_polygon()
        # test_arguments_exist()
        # test_field_in_feature_class()
        # test_add_external_area_field()
        # test_calculate_external_field()
        # test_get_file_from_path()
        # test_get_directory_from_path()
        # test_renameFieldMap()
        # test_add_layer_count()
        test_redistributePolygon()
        # test_create_point()
        # test_create_points()
        # test_create_polygon()
        # test_create_basic_polygon()
        # test_for_each_feature()
        # test_join_csv()
        # test_get_sum()
        # test_export_to_csv()
        # test_list_contents_of()
        # test_get_duplicates()
    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
        logging.exception(arcpy.GetMessages(2))
    except Exception as e:
        logging.exception(e.args[0])
        print e.args[0]

    os.system('pause')
