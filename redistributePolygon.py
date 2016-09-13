# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
#
# redistributePolygon.py
# Finalised: 13/09/2016
#
##### Description: 
# This tool redistributed the growth model to another polygon. It was developed for the purposed of finding the growth model projections for pump station catchments.
#
##### Usage: Assign the variables below as required, save the file, then enter the following code into the python window in ArcCatalog (not ArcMap, due to processing time):
# execfile(r'PATH_TO_THIS_PYTHON_FILE')
# where PATH_TO_THIS_PYTHON_FILE is substituted for the full path of this python file. For example: execfile(r's:\infrastructure planning\staff\jared\gis\tools\arcpyscripts\redistributepolygon.py')
# 
##### Variables:
# The workspace variable:
# This viable is where all the intermediate files are stored. Either create a geodatabase at the location shown below, or change it to a workspace geodatabase that has already been created.
workspace = "C:\\TempArcGIS\\scratchworkspace.gdb\\" # note the use of double backslash (\\) instead of single backslash (\). This path must end with a double backslash (\\).
#
# The redistribution_layer_path variable:
# This variable contains the full path to the layer that the growth model will be redistributed to.
redistrubtion_layer_path = r'S:\Infrastructure Planning\Staff\Jared\Southern Suburbs Sewer Planning Report\SewerData.gdb\southernsuburbs_overall_catchments'
#
# ---------------------------------------------------------------------------

## Preprocessing
import arcpy
#
arcpy.env.OverwriteOutput = True

## disabling Z and M bounds as I think this causes a data bounds error
# https://geonet.esri.com/thread/79969
print('Z: ' + arcpy.env.outputZFlag)
arcpy.env.outputZFlag = "Disabled"
print('Z: ' + arcpy.env.outputZFlag)
#
print('M: ' + arcpy.env.outputMFlag)
arcpy.env.outputMFlag = "Disabled"
print('M: ' + arcpy.env.outputMFlag)

## defining functions
#TODO: move these functions into a module and import that in the preprocessing stage
def delete_if_exists(feature):
	if arcpy.Exists(feature):
		print("The following output filename already exists and will now be deleted: %s" % feature)
		arcpy.Delete_management(feature)
#
def calculate_field_proportion_based_on_area(field_to_calculate, total_area_field):
	"""
	Calculates the field_to_calculate for each polygon based on its percentage of the total area of the polygon to calculate from
	Arguments should be the names of the fields as strings
	"""
	print("    Calculating %s field based on the proportion of the polygon area to the %s field" % (field_to_calculate, total_area_field))
	arcpy.CalculateField_management (intersecting_polygons, field_to_calculate, "return_area_proportion_of_total(!"+total_area_field+"!, !Shape_Area!, !" + field_to_calculate + "!)", "PYTHON_9.3", """def return_area_proportion_of_total(GMZ_total_area, Shape_Area, field_to_calculate):
	return Shape_Area/GMZ_total_area * field_to_calculate""")
#
def calculate_field_proportion_based_on_number_of_lots(field_to_calculate, larger_properties_field, local_number_of_properties_field):
	"""
	Calculates the field_to_calculate for each polygon based on the number of lots in that polygon, compared to total number of lots on the larger polygon form which the data should be interpolated.
	Arguments should be the names of the fields as strings
	"""
	print("    Calculating %s field based on the proportion of the total properties value in the %s field" % (field_to_calculate, larger_properties_field))
	arcpy.CalculateField_management (intersecting_polygons, field_to_calculate, "return_number_proportion_of_total(!"+larger_properties_field+"!, !"+local_number_of_properties_field+"!, !" + field_to_calculate + "!)", "PYTHON_9.3", """def return_number_proportion_of_total(total_properties, local_properties, field_to_calculate):
	new_value =  (float(local_properties)/total_properties) * field_to_calculate
	return int(new_value)""")
#
def calculate_field_proportion_based_on_combination(field_to_calculate, larger_properties_field, local_number_of_properties_field, total_area_field):
	"""
	Calculates the the field based on area, and by number of lots, and assigned the average between the two as the value.
	"""
	print("    Calculating %s field as the average value between area and number of lots method")
	arcpy.CalculateField_management (intersecting_polygons, field_to_calculate, "return_average_value(!"+larger_properties_field+"!, !"+local_number_of_properties_field+"!, !" + field_to_calculate + "!, !" + total_area_field + "!, !Shape_Area!)", "PYTHON_9.3", """def return_number_proportion_of_total(total_properties, local_properties, field_to_calculate):
	new_value =  (float(local_properties)/total_properties) * field_to_calculate
	return int(new_value)
def return_area_proportion_of_total(GMZ_total_area, Shape_Area, field_to_calculate):
	return Shape_Area/GMZ_total_area * field_to_calculate
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
	properties = r"S:\\Infrastructure Planning\\Spatial Data\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Cadastral\\sde_vector.TCC.Properties"
	# see: http://gis.stackexchange.com/questions/35468/what-is-the-proper-syntax-and-usage-for-arcgis-in-memory-workspace
	properties_SpatialJoin = workspace + "properties_SpatialJoin"
	stats = workspace + "stats"
	delete_if_exists(properties_SpatialJoin)
	delete_if_exists(stats)
	print("    joining properties to "+ feature_class +" and outputing to %s" % properties_SpatialJoin)
	arcpy.SpatialJoin_analysis(feature_class, properties, properties_SpatialJoin, "JOIN_ONE_TO_MANY", "KEEP_ALL", "", "INTERSECT")
	print("    Calculating statistics table at stats")
	arcpy.Statistics_analysis(properties_SpatialJoin, stats, "Join_Count SUM","TARGET_FID")
	print("    joining back to intersecting_polygons")
	arcpy.JoinField_management (feature_class, "OBJECTID", stats, "TARGET_FID", "FREQUENCY")
	print("    renaming 'FREQUENCY' to '%s'" % field_name)
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
	delete_if_exists(intersecting_polygons)
	print("Computing the polygons that intersect both features")
	arcpy.Intersect_analysis ([redistribution_layer, data_layer], intersecting_polygons, "ALL", "", "INPUT")
	print("Output: %s" % intersecting_polygons)
#
def join_growthmodel_table_to_intersecting_polygons():
	fields_to_be_joined = "" # this list may need to be edited depending on what is required of the tool. To join all fields, set this variable to an empty string (""). To specify a list of fields, use a list, eg, ["POP_2011", "Tot_2011", "POP_2016", "Tot_2016"]. Although, this list may be better set in the fields_list variable.
	print("Joining growthmodel to interseting polygons")
	arcpy.JoinField_management (intersecting_polygons, "GMZ", growthmodel_table, "GMZ", fields_to_be_joined)
	print("Output: %s" % intersecting_polygons)
#
def add_total_and_local_GMZ_fields():
	add_property_count_to_layer_x_with_name_x(intersecting_polygons, local_number_of_properties_field)
	data_layer_rejoined = workspace + "data_layer_rejoined" # this layer will store the intersecting polygons layer back into GMZs so that the total properties in each GMZ includes any double counting.
	fieldmappings_data = arcpy.FieldMappings()
	# map total_properties_including_double_counted_field:
	fm_total_properties_rejoined = arcpy.FieldMap()
	fm_total_properties_rejoined.addInputField(intersecting_polygons, local_number_of_properties_field)
	renameFieldMap(fm_total_properties_rejoined, total_properties_including_double_counted_field)
	fm_total_properties_rejoined.mergeRule = "Sum"
	fieldmappings_data.addFieldMap(fm_total_properties_rejoined)
	print("    Creating %s layer" % data_layer_rejoined)
	delete_if_exists(data_layer_rejoined)
	print ("    data_layer = %s" % data_layer)
	print ("    intersecting_polygons = %s" % intersecting_polygons)
	print ("    data_layer_rejoined = %s" % data_layer_rejoined)
	arcpy.SpatialJoin_analysis (data_layer, intersecting_polygons, data_layer_rejoined, "JOIN_ONE_TO_ONE", "KEEP_COMMON", fieldmappings_data, "INTERSECT", -0.5)
	print("    %s includes %s field" % (data_layer_rejoined, total_properties_including_double_counted_field))
	arcpy.JoinField_management (data_layer, "OBJECTID", data_layer_rejoined,  "TARGET_FID", total_properties_including_double_counted_field)
	print("    %s field joined to %s" % (total_properties_including_double_counted_field, data_layer_rejoined))
#
def max_total_properties_field():
	"""
	Calculates the total_properties_including_double_counted_field to be the max of itself or the total_properties_field.
	"""
	arcpy.CalculateField_management (intersecting_polygons, total_properties_including_double_counted_field, "max([!"+total_properties_including_double_counted_field+"!, !"+total_properties_field+"!])", "PYTHON_9.3")


## Script Arguments - These are the values that will typically change. They have been built to be used in a model builder with default values proivded if none are received from the model. If run as a python scrip, these arguments will take their values from the variables provided at the top of the script.
#
redistribution_layer_name = arcpy.GetParameterAsText(0)
if redistribution_layer_name == '#' or not redistribution_layer_name:
    redistribution_layer_name = redistrubtion_layer_path
    arcpy.AddMessage("you have not provided a redistribution_layer_name. using default: %s" % redistribution_layer_name)
#
data_layer = arcpy.GetParameterAsText(1)
if data_layer == '#' or not data_layer:
    #raise ValueError('You must provide a data_layer')
    data_layer = r'S:\Infrastructure Planning\Staff\Jared\Southern Suburbs Sewer Planning Report\SewerData.gdb\GMZ' # provide a default value if unspecified
print("data layer: %s" % data_layer)
delete_if_exists(workspace + "data_layer")
arcpy.Select_analysis (data_layer, workspace + "data_layer")
data_layer = workspace + "data_layer"
print("new data layer: %s" % data_layer)
#
distribution_method = arcpy.GetParameterAsText(2)
if distribution_method == '#' or not distribution_method:
    distribution_method = 3 # 1 - by area, 2 - by number of properties, 3 - by a combination of the two methods.
    									    # for distribution_method = 3, number of properties method is used for 2016, area method is used for >2036, and 
									    # the average of the two is used for 2016-2036.
    arcpy.AddMessage("you have not provided a distribution_method. 1 = distribute by area, 2 = distribute my number of properties. Using %s by default" % distribution_method)
#
output_filename = arcpy.GetParameterAsText(3)
if output_filename == '#' or not output_filename:
    output_filename = workspace + "redistributedPolygon" # provide a default value if unspecified
    print("you have not provided an output_layer. This tool will now delete the default file and rewrite it: %s" % output_filename)
    delete_if_exists(output_filename)
#
# this table should be created from the 'Pops and Emps' tab of the growth model outputs provided by Brian. The fields in the table I'm currently using are ["GMZ", "POP_2011", "Tot_2011", "POP_2016", "Tot_2016", "POP_2021", "Tot_2021", "POP_2026", "Tot_2026", "POP_2031", "Tot_2031", "POP_2036", "Tot_2036", "POP_2041", "Tot_2041", "POP_2046", "Tot_2046", "POP_2051", "Tot_2051", "POP_Full", "Tot_Full"]
growthmodel_csv = arcpy.GetParameterAsText(4)
if growthmodel_csv == '#' or not growthmodel_csv:
    growthmodel_csv = r'S:\Infrastructure Planning\Staff\Jared\Southern Suburbs Sewer Planning Report\SouthernSuburbsGrowthModel20160908_mediumGrowth.csv' # provide a default value if unspecified
    print("you have not provided a growthmodel_csv. Using default: %s" % growthmodel_csv)

## Local variables:
local_number_of_properties_field = "local_counted_properties"
total_properties_including_double_counted_field = "total_double_counted_properties" # the number of properties counted in the intersecting polygons, then joined back together in the GMZs (or data_layer)
total_properties_field = "total_counted_properties"
intersecting_polygons = workspace + "intersecting_polygons"
growthmodel_table = workspace + "growthmodel_table"
# TODO: remove 2011 fields from output
field_list = ["POP_2011", "Tot_2011", "POP_2016", "Tot_2016", "POP_2021", "Tot_2021", "POP_2026", "Tot_2026", "POP_2031", "Tot_2031", "POP_2036", "Tot_2036", "POP_2041", "Tot_2041", "POP_2046", "Tot_2046", "POP_2051", "Tot_2051", "POP_Full", "Tot_Full"]

## Import grothmodel_table
delete_if_exists(growthmodel_table)
print("Converting Growth Model from a .csv into a gdb table")
arcpy.CopyRows_management (growthmodel_csv, growthmodel_table)

add_property_count_to_layer_x_with_name_x(data_layer, total_properties_field)

input_layer = redistribution_layer_name
redistribution_layer = workspace + "redistribution_layer"
delete_if_exists(redistribution_layer)
arcpy.CopyFeatures_management(input_layer, redistribution_layer)

create_intersecting_polygons()

join_growthmodel_table_to_intersecting_polygons()

add_total_and_local_GMZ_fields()

create_intersecting_polygons() #recreate this layer with total_properties_filed that includes double counted properties.

join_growthmodel_table_to_intersecting_polygons()

add_property_count_to_layer_x_with_name_x(intersecting_polygons, local_number_of_properties_field)

max_total_properties_field()

## Recalculate groth model fields
total_area_field = "GMZ_TOTAL_AREA"
# TODO: add total_area_field
for GM_field in field_list:
	if field_exists_in_feature_class(GM_field, intersecting_polygons):
		if distribution_method == 1:
			calculate_field_proportion_based_on_area(GM_field, total_area_field)
		elif distribution_method == 2:
			print("calculating %s field from total GMZ number of properties" % GM_field)
			calculate_field_proportion_based_on_number_of_lots(GM_field, total_properties_including_double_counted_field, local_number_of_properties_field)
		elif distribution_method == 3:
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
fm_layer = arcpy.FieldMap()
fm_REF_NO = arcpy.FieldMap()
fm_GMZ = arcpy.FieldMap()
#fm_POP_2011 = arcpy.FieldMap()
## add the source fields for each FieldMap object, eg, someFieldMap_object.addInputField(source_feature_class, field_name)
fm_layer.addInputField(redistribution_layer, "Layer")
fm_REF_NO.addInputField(redistribution_layer, "REF_NO")
fm_GMZ.addInputField(intersecting_polygons, "GMZ")
#fm_POP_2011.addInputField(intersecting_polygons, "POP_2011)
## Assign a field name for the output file. NOTE: in exampls this has been done in separete steps, if it doesn't work, change this.
print("assigning output field name")
renameFieldMap(fm_layer, "PS_name")
renameFieldMap(fm_REF_NO, "PS_REF_NO")
renameFieldMap(fm_GMZ, "GMZs_contrib")
#renameFieldMap(fm_POP_2011, "PS_POP_2011")
print("done assigning output field name")
## Assign output field type
fm_GMZ.outputField.type = "String"
fm_GMZ.outputField.length = 100
## Set merge rules
#fm_POP_2011.mergeRule = "Sum"
fm_GMZ.mergeRule = "Join"
fm_GMZ.joinDelimiter = ", "
## add FieldMap objects to FieldMappings object
fieldmappings.addFieldMap(fm_layer)
fieldmappings.addFieldMap(fm_REF_NO)
#fieldmappings.addFieldMap(fm_GMZ) # when I leave this in Iget "ExecuteError: ERROR 001156: Failed on input OID 1, could not write value '412, 379, 413, 201, 411, 410' to output field GMZ Failed to execute (SpatialJoin)." My hypothesis is that is fails because GMZs are integers and can't be written to a text field. I've looked breifly how to cast the input field to a string, but I can't seem to find out how (this page might give more insight: http://gis.stackexchange.com/questions/158922/change-field-type-using-field-mapping-for-list-of-tables-using-python). All I can think to do is add a new field and copy the values accross converting to string in the process. This field isn't neccesary so I'll ignore it.
#fieldmappings.addFieldMap(fm_POP_2011)
#
## create FieldMaps for growth model field
for GM_field in field_list:
	if field_exists_in_feature_class(GM_field, intersecting_polygons):
		fm_POP_or_Total = arcpy.FieldMap()
		fm_POP_or_Total.addInputField(intersecting_polygons, GM_field)
		#fm_POP_or_Total.outputField.name = GM_field
		renameFieldMap(fm_POP_or_Total, GM_field)
		fm_POP_or_Total.mergeRule = "Sum"
		fieldmappings.addFieldMap(fm_POP_or_Total)

## Spatially Join intersecting_polygons back to redistribution layer
delete_if_exists(output_filename)
print("joining intersecting_polygons back to redistribution layer")
arcpy.SpatialJoin_analysis (redistribution_layer, intersecting_polygons, output_filename, "JOIN_ONE_TO_ONE", "KEEP_ALL", fieldmappings, "CONTAINS", "#", "#")
print("Successfully redistributed %s to %s" % (data_layer, redistribution_layer))
print("Output file can be found at %s" % output_filename)
