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

# arcpy.env.workspace = r'O:\Data\Planning_IP\Admin\Staff\Jared\GIS\Tools\arcpyScripts\TestingDataset.gdb'
arcpy.env.workspace = arcpy.env.scratchGDB
# testing = True
testing = False

logging.basicConfig(filename='jj_tests.log',
    level=logging.DEBUG,
    format='%(asctime)s @ %(lineno)d: %(message)s',
    datefmt='%Y-%m-%d,%H:%M:%S')


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
    one_field = jj.create_basic_polygon()
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
    log("Testing redistributePolygon...")
    left_x = 479582.11
    right_x = 479649.579
    lower_y = 7871595.813
    upper_y = 7871628.886
    array = [(left_x,lower_y),
         (left_x,upper_y),
         (right_x,upper_y),
         (right_x,lower_y),
         (left_x,lower_y)]
    # This array creates an area that is around 40% of the growth model polygon.
    redistribution_test = arcpy.env.workspace + "\\redistribution_test_layer"
    jj.delete_if_exists(redistribution_test)
    jj.create_polygon(redistribution_test, array)
    left_x = 479582.11
    right_x = 479773.05
    lower_y = 7871595.813
    upper_y = 7871628.886
    array = [(left_x,lower_y),
         (left_x,upper_y),
         (right_x,upper_y),
         (right_x,lower_y),
         (left_x,lower_y)]
    growth_model_polygon_test = arcpy.env.workspace + "\\growth_model_polygon_test"
    jj.delete_if_exists(growth_model_polygon_test)
    jj.create_polygon(growth_model_polygon_test, array)
    arcpy.AddField_management(growth_model_polygon_test, "Dwelling_1", "LONG")
    arcpy.CalculateField_management(growth_model_polygon_test,  "Dwelling_1", "get_10()", "PYTHON_9.3", """def get_10():
            return 10""")
    redistributePolygonInputs = {}
    redistributePolygonInputs["layer_to_redistribute_to"] = redistribution_test
    redistributePolygonInputs["layer_to_be_redistributed"] = growth_model_polygon_test
    redistributePolygonInputs["output_filename"] = "redistributed"
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
                if re.match('distribution method must be either 1, 2 or 3', e.args[0]):
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
        log("    Testing simple distribution:")
        redistributePolygonInputs["fields_to_be_distributed"] = ["Dwelling_1"]
        redistributePolygonInputs["distribution_method"] = 2
        jj.redistributePolygon(redistributePolygonInputs)
        with arcpy.da.SearchCursor(redistributePolygonInputs["output_filename"], ['Dwelling_1']) as cursor:
            for row in cursor:
                if row[0] == 10:
                    log("    Pass")
                else:
                    log("    Fail: Dwelling_1 should be 10")
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


    def testing_area_method():
        log("  Testing area method:")
        log("    Testing 40% of area yeilds 40% of population:")
        redistributePolygonInputs["distribution_method"] = 1
        jj.redistributePolygon(redistributePolygonInputs)
        for row in arcpy.da.SearchCursor(redistributePolygonInputs["output_filename"], ['Dwelling_1']):
            if row[0] == 4:
                log("      Pass")
            else:
                log("      Fail: Dwelling_1 should be 4")


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
            log("    Fail: total dwellings in output was 0. This means that decimas are being integerised, not rounded")
        else:
            log("    Fail: total dwellings in %s should be 1, but was %s. This error was unexpected and needs to be investigated." % (redistributePolygonInputs["output_filename"], total_dwellings))


    testing_number_of_fields()
    testing_invalid_distribution_method_is_caught()
    testing_invalid_field_is_caught()
    testing_number_of_properties_method()
    testing_area_method()
    testing_for_rounding()
    testing_for_integerising()
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
        logging.info("Running tests")
        logging.info("")
        # test_delete_if_exists()
        # test_arguments_exist()
        # test_field_in_feature_class()
        # test_return_tuple_of_args()
        # test_calculate_external_field()
        # test_get_file_from_path()
        # test_get_directory_from_path()
        # test_renameFieldMap()
        # test_redistributePolygon()
        test_create_point()
        # test_create_points()
        # test_create_polygon()
        # test_create_basic_polygon()
        # test_for_each_feature()
        # test_join_csv()
        # test_create_basic_polygon()
        # test_get_sum()
    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
        logging.exception(arcpy.GetMessages(2))
    except Exception as e:
        logging.exception(e.args[0])
        print e.args[0]

    os.system('pause')
