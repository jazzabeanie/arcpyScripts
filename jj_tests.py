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
    print "Testing redistributePolygon..."
    redistributePolygonInputs = {}
    redistributePolygonInputs["redistribution_layer_name"] = "mesh_intersect"
    redistributePolygonInputs["growth_model_polygon"] = "MB_2015_TSV"
    redistributePolygonInputs["output_filename"] = "redistributed"
    redistributePolygonInputs["intersect_join_field"] = "MB_CODE16"
    redistributePolygonInputs["growth_join_field"] = "MB_CODE16"
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
    print "TODO: check for success"
    # if ():
    #     print "  pass"
    # else:
    #     print "  fail"
    print "------"

def test_create_polygon():
    print "Testing create_polygon..."
    array = [(471966.2812500,7858694.5000000),
             (471895.5000000,7858701.0000000),
             (471865.5000000,7858703.5000000),
             (471844.0312500,7858706.0000000),
             (471622.6875000,7858726.0000000),
             (471389.3750000,7858747.5000000),
             (469967.9687500,7858874.5000000),
             (469973.7812500,7858974.5000000),
             (469972.3125000,7858999.0000000),
             (469971.6875000,7859029.0000000),
             (469975.3125000,7859051.0000000),
             (469980.9062500,7859076.0000000),
             (469976.3125000,7859121.5000000),
             (469971.6875000,7859153.0000000),
             (469970.0625000,7859174.0000000),
             (469974.3437500,7859201.5000000),
             (469998.0312500,7859241.0000000),
             (470036.7812500,7859313.0000000),
             (470047.4062500,7859344.0000000),
             (470069.3750000,7859444.0000000),
             (470073.0937500,7859478.0000000),
             (470075.0625000,7859514.5000000),
             (470074.8125000,7859556.0000000),
             (470073.5625000,7859620.0000000),
             (470067.9062500,7859716.0000000),
             (470046.4062500,7859801.5000000),
             (470010.3750000,7859843.5000000),
             (469898.5312500,7859872.5000000),
             (469845.2187500,7859882.0000000),
             (469831.9062500,7859899.0000000),
             (469831.1562500,7859915.0000000),
             (469830.7500000,7859925.0000000),
             (469847.1875000,7859991.0000000),
             (469849.1875000,7860075.0000000),
             (469851.6562500,7860109.0000000),
             (469847.4375000,7860172.0000000),
             (469838.5625000,7860231.0000000),
             (469840.0312500,7860251.5000000),
             (469818.8125000,7860315.0000000),
             (469801.7812500,7860347.0000000),
             (469815.8437500,7860404.0000000),
             (469832.2187500,7860506.5000000),
             (469837.5000000,7860506.0000000),
             (470369.8750000,7860453.5000000),
             (470400.2812500,7860773.0000000),
             (470480.0937500,7860765.5000000),
             (470515.1250000,7860762.0000000),
             (470538.5312500,7860760.0000000),
             (470558.4375000,7860758.0000000),
             (470578.3437500,7860756.0000000),
             (470598.2500000,7860754.5000000),
             (470618.1562500,7860752.5000000),
             (470638.0625000,7860750.5000000),
             (470657.9687500,7860748.5000000),
             (470677.8750000,7860747.0000000),
             (470697.7812500,7860745.0000000),
             (470717.6875000,7860743.0000000),
             (470737.5937500,7860741.0000000),
             (470757.5000000,7860739.5000000),
             (470777.4062500,7860737.5000000),
             (470797.3125000,7860735.5000000),
             (470795.4375000,7860715.5000000),
             (470794.0312500,7860700.5000000),
             (470793.3125000,7860693.0000000),
             (470792.8750000,7860688.5000000),
             (470792.0937500,7860680.0000000),
             (470790.9375000,7860668.0000000),
             (470789.0625000,7860648.0000000),
             (470828.8750000,7860644.0000000),
             (470848.7812500,7860642.5000000),
             (470868.6875000,7860640.5000000),
             (470888.5937500,7860638.5000000),
             (470908.4687500,7860636.5000000),
             (470928.3750000,7860635.0000000),
             (470948.2812500,7860633.0000000),
             (470973.3125000,7860630.5000000),
             (470975.9375000,7860658.5000000),
             (470976.1875000,7860661.0000000),
             (470987.2812500,7860672.5000000),
             (470995.2187500,7860757.5000000),
             (471005.2500000,7860756.5000000),
             (471035.1875000,7860753.5000000),
             (471067.5312500,7860750.5000000),
             (471077.6562500,7860749.5000000),
             (471086.9687500,7860845.0000000),
             (471162.7812500,7860838.0000000),
             (471251.1250000,7860842.0000000),
             (471258.9687500,7860704.0000000),
             (471344.4062500,7860709.0000000),
             (471351.2187500,7860594.5000000),
             (471357.3437500,7860560.5000000),
             (471362.5000000,7860542.0000000),
             (471371.6875000,7860518.0000000),
             (471385.0625000,7860487.0000000),
             (471400.4062500,7860457.5000000),
             (471411.0937500,7860441.5000000),
             (471420.4375000,7860429.5000000),
             (471431.9375000,7860417.0000000),
             (471448.7500000,7860403.5000000),
             (471465.8437500,7860392.5000000),
             (471492.5625000,7860381.0000000),
             (471534.2187500,7860371.5000000),
             (471561.5000000,7860370.5000000),
             (471590.6250000,7860372.0000000),
             (471619.5625000,7860379.5000000),
             (471642.4375000,7860389.5000000),
             (471872.5312500,7860509.5000000),
             (471989.6875000,7860139.0000000),
             (472010.8125000,7860053.0000000),
             (472027.3125000,7859953.5000000),
             (472037.2812500,7859795.5000000),
             (472004.7500000,7859272.5000000),
             (471964.3437500,7858942.5000000),
             (471959.8750000,7858871.5000000),
             (471959.3125000,7858801.0000000),
             (471962.7812500,7858728.0000000),
             (471966.2812500,7858694.5000000)]
    output = arcpy.env.workspace + "\\test_create_polygon"
    jj.delete_if_exists(output)
    jj.create_polygon(output, array)
    print "TODO: confirm results"
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
    # test_redistributePolygon()
    test_create_polygon()

    os.system('pause')
