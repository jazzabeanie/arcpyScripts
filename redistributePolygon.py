# --------------------------------
# Name: redistributePolygon.py
# Purpose: To redistribute a growth model output to another shape
# Author: Jared Johnston
# Refactored: 20170926
# Copyright:   (c) TCC
# ArcGIS Version:   10.2
# Python Version:   2.7
# Source: https://blogs.esri.com/esri/arcgis/2011/08/04/pythontemplate/
# --------------------------------
import os # noqa
import sys # noqa
import arcpy
import logging
import json
import jj_methods as jj # noqa
from datetime import datetime
# m = imp.load_source('jj_methods', 'O:\Data\Planning_IP\Admin\Staff\Jared\GIS\Tools\arcpyScripts\jj_methods.py') # https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path

testing = False
now = r'%s' % datetime.now().strftime("%Y%m%d%H%M")

if testing:
    keep_method = "KEEP_COMMON"
    arcpy.env.workspace = r'C:\TempArcGIS\scratchworkspace.gdb'
    logging.basicConfig(filename='redistributePolygon.log',
                        level=logging.DEBUG,
                        format='%(asctime)s @ %(lineno)d: %(message)s',
                        datefmt='%Y-%m-%d,%H:%M:%S')
    logging.info("testing = True")
else:
    keep_method = "KEEP_ALL"
    arcpy.env.workspace = r'C:\TempArcGIS\scratchworkspace.gdb'
    # arcpy.env.workspace = "in_memory"
    logging.basicConfig(filename='redistributePolygon.log',
                        level=logging.INFO,
                        format='%(asctime)s @ %(lineno)d: %(message)s',
                        datefmt='%Y-%m-%d,%H:%M:%S')
    logging.info("testing = False")

logging.warning("------")

def create_test_area_polygon(output):
    """
    returns an array of points used to create a polygon that will be used to create the test case.
    """
    print "directory = " + jj.get_directory_from_path(output)
    print "name = " + jj.get_file_from_path(output)
    arcpy.CreateFeatureclass_management(
            jj.get_directory_from_path(output), # out_path
            jj.get_file_from_path(output), # out_name
            "POLYGON") # geometry_type
            # "#", # template
            # "DISABLED", # has_m
            # "DISABLED", # has_z
            # inputs["growth_model_polygon"]) # spatial_reference
    array = arcpy.Array([arcpy.Point(471966.2812500,7858694.5000000),
                         arcpy.Point(471895.5000000,7858701.0000000),
                         arcpy.Point(471865.5000000,7858703.5000000),
                         arcpy.Point(471844.0312500,7858706.0000000),
                         arcpy.Point(471622.6875000,7858726.0000000),
                         arcpy.Point(471389.3750000,7858747.5000000),
                         arcpy.Point(469967.9687500,7858874.5000000),
                         arcpy.Point(469973.7812500,7858974.5000000),
                         arcpy.Point(469972.3125000,7858999.0000000),
                         arcpy.Point(469971.6875000,7859029.0000000),
                         arcpy.Point(469975.3125000,7859051.0000000),
                         arcpy.Point(469980.9062500,7859076.0000000),
                         arcpy.Point(469976.3125000,7859121.5000000),
                         arcpy.Point(469971.6875000,7859153.0000000),
                         arcpy.Point(469970.0625000,7859174.0000000),
                         arcpy.Point(469974.3437500,7859201.5000000),
                         arcpy.Point(469998.0312500,7859241.0000000),
                         arcpy.Point(470036.7812500,7859313.0000000),
                         arcpy.Point(470047.4062500,7859344.0000000),
                         arcpy.Point(470069.3750000,7859444.0000000),
                         arcpy.Point(470073.0937500,7859478.0000000),
                         arcpy.Point(470075.0625000,7859514.5000000),
                         arcpy.Point(470074.8125000,7859556.0000000),
                         arcpy.Point(470073.5625000,7859620.0000000),
                         arcpy.Point(470067.9062500,7859716.0000000),
                         arcpy.Point(470046.4062500,7859801.5000000),
                         arcpy.Point(470010.3750000,7859843.5000000),
                         arcpy.Point(469898.5312500,7859872.5000000),
                         arcpy.Point(469845.2187500,7859882.0000000),
                         arcpy.Point(469831.9062500,7859899.0000000),
                         arcpy.Point(469831.1562500,7859915.0000000),
                         arcpy.Point(469830.7500000,7859925.0000000),
                         arcpy.Point(469847.1875000,7859991.0000000),
                         arcpy.Point(469849.1875000,7860075.0000000),
                         arcpy.Point(469851.6562500,7860109.0000000),
                         arcpy.Point(469847.4375000,7860172.0000000),
                         arcpy.Point(469838.5625000,7860231.0000000),
                         arcpy.Point(469840.0312500,7860251.5000000),
                         arcpy.Point(469818.8125000,7860315.0000000),
                         arcpy.Point(469801.7812500,7860347.0000000),
                         arcpy.Point(469815.8437500,7860404.0000000),
                         arcpy.Point(469832.2187500,7860506.5000000),
                         arcpy.Point(469837.5000000,7860506.0000000),
                         arcpy.Point(470369.8750000,7860453.5000000),
                         arcpy.Point(470400.2812500,7860773.0000000),
                         arcpy.Point(470480.0937500,7860765.5000000),
                         arcpy.Point(470515.1250000,7860762.0000000),
                         arcpy.Point(470538.5312500,7860760.0000000),
                         arcpy.Point(470558.4375000,7860758.0000000),
                         arcpy.Point(470578.3437500,7860756.0000000),
                         arcpy.Point(470598.2500000,7860754.5000000),
                         arcpy.Point(470618.1562500,7860752.5000000),
                         arcpy.Point(470638.0625000,7860750.5000000),
                         arcpy.Point(470657.9687500,7860748.5000000),
                         arcpy.Point(470677.8750000,7860747.0000000),
                         arcpy.Point(470697.7812500,7860745.0000000),
                         arcpy.Point(470717.6875000,7860743.0000000),
                         arcpy.Point(470737.5937500,7860741.0000000),
                         arcpy.Point(470757.5000000,7860739.5000000),
                         arcpy.Point(470777.4062500,7860737.5000000),
                         arcpy.Point(470797.3125000,7860735.5000000),
                         arcpy.Point(470795.4375000,7860715.5000000),
                         arcpy.Point(470794.0312500,7860700.5000000),
                         arcpy.Point(470793.3125000,7860693.0000000),
                         arcpy.Point(470792.8750000,7860688.5000000),
                         arcpy.Point(470792.0937500,7860680.0000000),
                         arcpy.Point(470790.9375000,7860668.0000000),
                         arcpy.Point(470789.0625000,7860648.0000000),
                         arcpy.Point(470828.8750000,7860644.0000000),
                         arcpy.Point(470848.7812500,7860642.5000000),
                         arcpy.Point(470868.6875000,7860640.5000000),
                         arcpy.Point(470888.5937500,7860638.5000000),
                         arcpy.Point(470908.4687500,7860636.5000000),
                         arcpy.Point(470928.3750000,7860635.0000000),
                         arcpy.Point(470948.2812500,7860633.0000000),
                         arcpy.Point(470973.3125000,7860630.5000000),
                         arcpy.Point(470975.9375000,7860658.5000000),
                         arcpy.Point(470976.1875000,7860661.0000000),
                         arcpy.Point(470987.2812500,7860672.5000000),
                         arcpy.Point(470995.2187500,7860757.5000000),
                         arcpy.Point(471005.2500000,7860756.5000000),
                         arcpy.Point(471035.1875000,7860753.5000000),
                         arcpy.Point(471067.5312500,7860750.5000000),
                         arcpy.Point(471077.6562500,7860749.5000000),
                         arcpy.Point(471086.9687500,7860845.0000000),
                         arcpy.Point(471162.7812500,7860838.0000000),
                         arcpy.Point(471251.1250000,7860842.0000000),
                         arcpy.Point(471258.9687500,7860704.0000000),
                         arcpy.Point(471344.4062500,7860709.0000000),
                         arcpy.Point(471351.2187500,7860594.5000000),
                         arcpy.Point(471357.3437500,7860560.5000000),
                         arcpy.Point(471362.5000000,7860542.0000000),
                         arcpy.Point(471371.6875000,7860518.0000000),
                         arcpy.Point(471385.0625000,7860487.0000000),
                         arcpy.Point(471400.4062500,7860457.5000000),
                         arcpy.Point(471411.0937500,7860441.5000000),
                         arcpy.Point(471420.4375000,7860429.5000000),
                         arcpy.Point(471431.9375000,7860417.0000000),
                         arcpy.Point(471448.7500000,7860403.5000000),
                         arcpy.Point(471465.8437500,7860392.5000000),
                         arcpy.Point(471492.5625000,7860381.0000000),
                         arcpy.Point(471534.2187500,7860371.5000000),
                         arcpy.Point(471561.5000000,7860370.5000000),
                         arcpy.Point(471590.6250000,7860372.0000000),
                         arcpy.Point(471619.5625000,7860379.5000000),
                         arcpy.Point(471642.4375000,7860389.5000000),
                         arcpy.Point(471872.5312500,7860509.5000000),
                         arcpy.Point(471989.6875000,7860139.0000000),
                         arcpy.Point(472010.8125000,7860053.0000000),
                         arcpy.Point(472027.3125000,7859953.5000000),
                         arcpy.Point(472037.2812500,7859795.5000000),
                         arcpy.Point(472004.7500000,7859272.5000000),
                         arcpy.Point(471964.3437500,7858942.5000000),
                         arcpy.Point(471959.8750000,7858871.5000000),
                         arcpy.Point(471959.3125000,7858801.0000000),
                         arcpy.Point(471962.7812500,7858728.0000000),
                         arcpy.Point(471966.2812500,7858694.5000000)])
    polygon = arcpy.Polygon(array)
    # Open an InsertCursor and insert the new geometry
    cursor = arcpy.da.InsertCursor(output, ['SHAPE@'])
    cursor.insertRow([polygon])
    del cursor
#
def calculate_field_proportion_based_on_area(field_to_calculate, total_area_field):
	"""
	Calculates the field_to_calculate for each polygon based on its percentage of the total area of the polygon to calculate from
	Arguments should be the names of the fields as strings
	"""
	logging.info("    Calculating %s field based on the proportion of the polygon area to the %s field" % (field_to_calculate, total_area_field))
	arcpy.CalculateField_management (intersecting_polygons, field_to_calculate, "return_area_proportion_of_total(!"+total_area_field+"!, !Shape_Area!, !" + field_to_calculate + "!)", "PYTHON_9.3", """def return_area_proportion_of_total(GMZ_total_area, Shape_Area, field_to_calculate):
	return Shape_Area/GMZ_total_area * int(field_to_calculate)""")
#
def calculate_field_proportion_based_on_number_of_lots(field_to_calculate, larger_properties_field, local_number_of_properties_field):
	"""
	Calculates the field_to_calculate for each polygon based on the number of lots in that polygon, compared to total number of lots on the larger polygon form which the data should be interpolated.
	Arguments should be the names of the fields as strings
	"""
	logging.info("    Calculating %s field based on the proportion of the total properties value in the %s field using %s" % (field_to_calculate, larger_properties_field, local_number_of_properties_field))
	arcpy.CalculateField_management (intersecting_polygons, field_to_calculate, "return_number_proportion_of_total(!"+larger_properties_field+"!, !"+local_number_of_properties_field+"!, !" + field_to_calculate + "!)", "PYTHON_9.3", """def return_number_proportion_of_total(total_properties, local_properties, field_to_calculate):
    new_value =  (float(local_properties)/total_properties) * int(field_to_calculate)
    return int(new_value)""")
#
def calculate_field_proportion_based_on_combination(field_to_calculate, larger_properties_field, local_number_of_properties_field, total_area_field):
	"""
	Calculates the the field based on area, and by number of lots, and assigned the average between the two as the value.
	"""
	logging.info("    Calculating %s field as the average value between area and number of lots method" % field_to_calculate)
	arcpy.CalculateField_management (intersecting_polygons, field_to_calculate, "return_average_value(!"+larger_properties_field+"!, !"+local_number_of_properties_field+"!, !" + field_to_calculate + "!, !" + total_area_field + "!, !Shape_Area!)", "PYTHON_9.3", """def return_number_proportion_of_total(total_properties, local_properties, field_to_calculate):
	new_value =  (float(local_properties)/total_properties) * int(field_to_calculate)
	return int(new_value)
def return_area_proportion_of_total(GMZ_total_area, Shape_Area, field_to_calculate):
	return Shape_Area/GMZ_total_area * int(field_to_calculate)
def return_average_value(total_properties, local_properties, field_to_calculate, GMZ_total_area, Shape_Area):
	properties = return_number_proportion_of_total(total_properties, local_properties, field_to_calculate)
	area = return_area_proportion_of_total(GMZ_total_area, Shape_Area, field_to_calculate)
	average = (area + properties) / 2
	return average""")
#
def add_property_count_to_layer_x_with_name_x(feature_class, field_name):
	"""
	Adds a field to the polygons containing the number of properties (from the SDE) in that polygon. Note that one property will get counted multiple time, once for every polygon that part of it is contained in.
	"""
	properties = r"O:\\Data\\Planning_IP\\Spatial\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Cadastral\\sde_vector.TCC.Properties"
	# see: http://gis.stackexchange.com/questions/35468/what-is-the-proper-syntax-and-usage-for-arcgis-in-memory-workspace
	properties_SpatialJoin = "properties_SpatialJoin"
	stats = "stats"
	jj.delete_if_exists(properties_SpatialJoin)
	jj.delete_if_exists(stats)
	logging.info("    joining properties to "+ feature_class +" and outputing to %s" % properties_SpatialJoin)
	arcpy.SpatialJoin_analysis(feature_class, properties, properties_SpatialJoin, "JOIN_ONE_TO_MANY", keep_method, "", "INTERSECT")
	logging.info("    Calculating statistics table at stats")
	arcpy.Statistics_analysis(properties_SpatialJoin, stats, "Join_Count SUM","TARGET_FID")
	logging.info("    joining back to intersecting_polygons")
	arcpy.JoinField_management (feature_class, "OBJECTID", stats, "TARGET_FID", "FREQUENCY")
	logging.info("    renaming 'FREQUENCY' to '%s'" % field_name)
	#arcpy.AlterField_management (feature_class, "FREQUENCY", field_name) # this tool doesn't work, waiting on a reply form Spatial Services.
	arcpy.AddField_management (feature_class, field_name, "SHORT", "#", "#", "#", "Number of Properties")
	arcpy.CalculateField_management (feature_class, field_name, "!FREQUENCY!", "PYTHON_9.3")
	arcpy.DeleteField_management (feature_class, "FREQUENCY")
#
def renameFieldMap(fieldMap, name_text):
	"""
	Sets the output fieldname of a FieldMap object. Used when creating FieldMappings.
	"""
	type_name = fieldMap.outputField
	type_name.name = name_text
	fieldMap.outputField = type_name
#
def field_exists_in_feature_class(field_name, feature_class):
	"""
	returns true if field (parameter 1), exists in feature class (parameter 2). returns false if not.
	See: https://epjmorris.wordpress.com/2015/04/22/how-can-i-check-to-see-if-an-attribute-field-exists-using-arcpy/
	"""
	fields = arcpy.ListFields(feature_class, field_name)
	if len(fields) == 1:
		return True
	else:
		return False
#
def create_intersecting_polygons():
	"""
	Creates intersecting_polygons layer by intersecting redistribution_layer (PS_Catchments) and data_layer (GMZ).
	"""
	jj.delete_if_exists(intersecting_polygons)
	logging.info("Computing the polygons that intersect both features")
	arcpy.Intersect_analysis ([redistribution_layer, data_layer], intersecting_polygons, "ALL", "", "INPUT")
	logging.info("Output: %s" % intersecting_polygons)
#
def join_growthmodel_table_to_intersecting_polygons():
	fields_to_be_joined = "" # this list may need to be edited depending on what is required of the tool. To join all fields, set this variable to an empty string (""). To specify a list of fields, use a list, eg, ["POP_2011", "Tot_2011", "POP_2016", "Tot_2016"]. Although, this list may be better set in the fields_list variable.
	logging.info("Joining growthmodel to interseting polygons")
	arcpy.JoinField_management (intersecting_polygons, "GMZ", growthmodel_table, "GMZ", fields_to_be_joined)
	logging.info("Output: %s" % intersecting_polygons)
#
def add_total_and_local_GMZ_fields():
	add_property_count_to_layer_x_with_name_x(intersecting_polygons, local_number_of_properties_field)
	data_layer_rejoined = "data_layer_rejoined" # this layer will store the intersecting polygons layer back into GMZs so that the total properties in each GMZ includes any double counting.
	fieldmappings_data = arcpy.FieldMappings()
	# map total_properties_including_double_counted_field:
	fm_total_properties_rejoined = arcpy.FieldMap()
	fm_total_properties_rejoined.addInputField(intersecting_polygons, local_number_of_properties_field)
	renameFieldMap(fm_total_properties_rejoined, total_properties_including_double_counted_field)
	fm_total_properties_rejoined.mergeRule = "Sum"
	fieldmappings_data.addFieldMap(fm_total_properties_rejoined)
	logging.info("    Creating %s layer" % data_layer_rejoined)
	jj.delete_if_exists(data_layer_rejoined)
	logging.info ("    data_layer = %s" % data_layer)
	logging.info ("    intersecting_polygons = %s" % intersecting_polygons)
	logging.info ("    data_layer_rejoined = %s" % data_layer_rejoined)
	arcpy.SpatialJoin_analysis (data_layer, intersecting_polygons, data_layer_rejoined, "JOIN_ONE_TO_ONE", "KEEP_COMMON", fieldmappings_data, "INTERSECT", -0.5)
	logging.info("    %s includes %s field" % (data_layer_rejoined, total_properties_including_double_counted_field))
	arcpy.JoinField_management (data_layer, "OBJECTID", data_layer_rejoined,  "TARGET_FID", total_properties_including_double_counted_field)
	logging.info("    %s field joined to %s" % (total_properties_including_double_counted_field, data_layer_rejoined))
#
def max_total_properties_field():
	"""
	Calculates the total_properties_including_double_counted_field to be the max of itself or the total_properties_field.
	"""
	arcpy.CalculateField_management (intersecting_polygons, total_properties_including_double_counted_field, "max([!"+total_properties_including_double_counted_field+"!, !"+total_properties_field+"!])", "PYTHON_9.3")

def setup():
    """
    Declares global variables
    """
    # TODO: should I do this?

# input params
inputs = {}
inputs["redistribution_layer_name"] = r'O:\Data\Planning_IP\Admin\Staff\Jared\Sewer Strategy Report Catchments\UpperRoss\Data.gdb\Overall_Catchments_20170720_Upper_Ross'
inputs["growth_model_polygon"] = r'R:\InfrastructureModels\Growth\Spatial\Database\GrowthModelGMZ.mdb\GMZ'
inputs["output_filename"] = r'O:\Data\Planning_IP\Admin\Staff\Jared\Sewer Strategy Report Catchments\UpperRoss\Data.gdb\UpperRoss_GrowthModelRedistributedToPSCatchments'
jj.delete_if_exists(inputs["output_filename"])
#
inputs["distribution_method"] = 3
if inputs["distribution_method"] in [1, 2, 3]:
    logging.info("distribution method %s is valid" % inputs["distribution_method"])
else:
    logging.info("distribution method = %s" % inputs["distribution_method"])
    logging.info("distribution method type = %s" % inputs["distribution_method"].type)
    raise ValueError('Distribution method must be either 1, 2 or 3')

## Local variables:
local_number_of_properties_field = "local_counted_properties"
total_properties_including_double_counted_field = "total_double_counted_properties" # the number of properties counted in the intersecting polygons, then joined back together in the GMZs (or data_layer)
total_properties_field = "total_counted_properties"
intersecting_polygons = "intersecting_polygons"
growthmodel_table = "growthmodel_table"
# TODO: remove 2011 fields from output
field_list = ["POP_2011", "Tot_2011", "POP_2016", "Tot_2016", "POP_2021", "Tot_2021", "POP_2026", "Tot_2026", "POP_2031", "Tot_2031", "POP_2036", "Tot_2036", "POP_2041", "Tot_2041", "POP_2051", "Tot_2051", "POP_Full", "Tot_Full"] # LGIP moderated GM results have no 2046
# field_list = ["POP_2011", "Tot_2011", "POP_2016", "Tot_2016", "POP_2021", "Tot_2021", "POP_2026", "Tot_2026", "POP_2031", "Tot_2031", "POP_2036", "Tot_2036", "POP_2041", "Tot_2041", "POP_2046", "Tot_2046", "POP_2051", "Tot_2051", "POP_Full", "Tot_Full"]
redistribution_layer = "redistribution_layer"
jj.delete_if_exists(redistribution_layer)
total_area_field = "GMZ_TOTAL_AREA"
data_layer = "data_layer"
jj.delete_if_exists("data_layer")
arcpy.MakeFeatureLayer_management(inputs["growth_model_polygon"], "data_layer")
arcpy.AddField_management(data_layer, total_area_field, "FLOAT")
arcpy.CalculateField_management(data_layer, total_area_field, "!Shape_Area!", "PYTHON_9.3")
#
growthmodel_csv = r'O:\Data\Planning_IP\Admin\Staff\Jared\Sewer Strategy Report Catchments\UpperRoss\GrowthModel_LGIP.csv'

if testing:
    inputs["distribution_method"] = 3  # because distribution_method 3 is a combination of 1 and 2
    inputs["output_filename"] = r'C:\TempArcGIS\scratchworkspace.gdb\redistributePolygons_testOutput'
    jj.delete_if_exists(inputs["output_filename"])
    #
    test_area_polygon = r'C:\TempArcGIS\testing.gdb\redistributePolygon_testArea'
    jj.delete_if_exists(test_area_polygon)
    create_test_area_polygon(test_area_polygon)
    #
    for layer, path in inputs.items():
        if layer not in ["distribution_method", "output_filename"]:
            out_feature_class = r'C:\TempArcGIS\testing.gdb\test_%s' % jj.get_file_from_path(path)
            jj.delete_if_exists(out_feature_class)
            arcpy.Clip_analysis(path, test_area_polygon, out_feature_class)
            inputs[layer] = out_feature_class
            logging.info("%s has been trimmed and is now in %s" % (layer, inputs[layer]))


def do_analysis(*argv):
    """See print statement undre main == __main__ for description"""
    try:
        arcpy.env.outputZFlag = "Disabled" ## disabling Z and M bounds as I think this causes a data bounds error
        arcpy.env.outputMFlag = "Disabled" # https://geonet.esri.com/thread/79969

        ## Import grothmodel_table
        jj.delete_if_exists(growthmodel_table)
        logging.info("Converting Growth Model from a .csv into a gdb table")
        logging.info("  If the resulting gdb table (%s) has fields listed as Test fiels, the schema.ini file in the csv directory may need to be changed: https://docs.microsoft.com/en-us/sql/odbc/microsoft/schema-ini-file-text-file-driver") # FIXME: make editing the .ini file unnecceasry
        arcpy.CopyRows_management(growthmodel_csv, growthmodel_table)
        for field in arcpy.ListFields(growthmodel_table):
            if field.type == "String":
                raise AttributeError("csv columns are being read as text. Change the schema.ini file so that values are Long")

        add_property_count_to_layer_x_with_name_x(data_layer, total_properties_field)

        arcpy.CopyFeatures_management(inputs["redistribution_layer_name"], redistribution_layer)

        create_intersecting_polygons()

        join_growthmodel_table_to_intersecting_polygons()

        add_total_and_local_GMZ_fields()

        create_intersecting_polygons() #recreate this layer with total_properties_filed that includes double counted properties.

        join_growthmodel_table_to_intersecting_polygons()

        add_property_count_to_layer_x_with_name_x(intersecting_polygons, local_number_of_properties_field)

        max_total_properties_field()

        ## Recalculate groth model fields
        for GM_field in field_list:
            if field_exists_in_feature_class(GM_field, intersecting_polygons):
                if inputs["distribution_method"] == 1:
                    calculate_field_proportion_based_on_area(GM_field, total_area_field)
                elif inputs["distribution_method"] == 2:
                    logging.info("calculating %s field from total GMZ number of properties" % GM_field)
                    calculate_field_proportion_based_on_number_of_lots(GM_field, total_properties_including_double_counted_field, local_number_of_properties_field)
                elif inputs["distribution_method"] == 3:
                    if GM_field in  ["POP_2016", "Tot_2016"]:
                        calculate_field_proportion_based_on_number_of_lots(GM_field, total_properties_including_double_counted_field, local_number_of_properties_field)
                    elif GM_field in  ["POP_2036", "Tot_2036", "POP_2041", "Tot_2041", "POP_2046", "Tot_2046", "POP_2051", "Tot_2051", "POP_Full", "Tot_Full"]:
                        calculate_field_proportion_based_on_area(GM_field, total_area_field)
                    elif GM_field in  ["POP_2021", "Tot_2021", "POP_2026", "Tot_2026", "POP_2031", "Tot_2031"]:
                        calculate_field_proportion_based_on_combination(GM_field, total_properties_including_double_counted_field, local_number_of_properties_field, total_area_field)
                    elif GM_field in  ["POP_2011", "Tot_2011"]:
                        arcpy.CalculateField_management (intersecting_polygons, GM_field, "returnNone()", "PYTHON_9.3", """def returnNone():
            return None""")



        ## POP_2011 is 0 here

        ### setup field maps for Spatial Join
        ## create FieldMap and FieldMappins objects
        fieldmappings = arcpy.FieldMappings()

        redistribution_layer_field_list = arcpy.ListFields(inputs["redistribution_layer_name"])
        for field in redistribution_layer_field_list:
            if field.name not in ['OBJECTID', 'Shape_Length', 'Shape_Area', 'Join_Count', 'Shape']:
                logging.info("Adding fieldmap for %s" % field.name)
                fm = arcpy.FieldMap()
                fm.addInputField(inputs["redistribution_layer_name"], field.name)
                renameFieldMap(fm, field.name)
                fieldmappings.addFieldMap(fm)

        for GM_field in field_list:
            if field_exists_in_feature_class(GM_field, intersecting_polygons):
                fm_POP_or_Total = arcpy.FieldMap()
                fm_POP_or_Total.addInputField(intersecting_polygons, GM_field)
                renameFieldMap(fm_POP_or_Total, GM_field)
                fm_POP_or_Total.mergeRule = "Sum"
                fieldmappings.addFieldMap(fm_POP_or_Total)

        ## Spatially Join intersecting_polygons back to redistribution layer
        jj.delete_if_exists(inputs["output_filename"])
        logging.info("joining intersecting_polygons back to redistribution layer")
        arcpy.SpatialJoin_analysis (redistribution_layer, intersecting_polygons, inputs["output_filename"], "JOIN_ONE_TO_ONE", keep_method, fieldmappings, "CONTAINS", "#", "#")
        logging.info("Successfully redistributed %s to %s" % (data_layer, redistribution_layer))
        logging.info("Output file can be found at %s" % inputs["output_filename"])
    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
        logging.exception(arcpy.GetMessages(2))
    except Exception as e:
        print e.args[0]
        logging.exception(e.args[0])
        # logger.error('Some weird error:', exc_info=True)  # logging info: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
# End do_analysis function


# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE,
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == '__main__':
    print("""
This script will take the Growth Model results and reportion them to a different shape.
""")
    os.system('pause')
    # Arguments overwrite defaults
    default_output = (r'')
    argv = [default_output]
    arguments_exist = True if (arcpy.GetArgumentCount() != 0) else False
    if arguments_exist:
        argv = tuple(arcpy.GetParameterAsText(i)
                     for i in range(arcpy.GetArgumentCount()))
    do_analysis(*argv)
    # see here for help on #argv https://docs.python.org/2.7/tutorial/controlflow.html#unpacking-argument-lists # noqa
    # see here for help on reading *argv in new called function: https://docs.python.org/2.7/tutorial/controlflow.html#keyword-arguments
    os.system('pause')
