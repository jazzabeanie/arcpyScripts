# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
#
# redistributePolygon.py
# Finalised: 13/09/2016
#
##### Description: #####
# This tool redistributes the growth model to another polygon. It was
# developed for the purpose of finding the growth model projections for pump
# station catchments of Southern Suburbs.
#
##### Usage: #####
# Before using this tool, the Issues section below should be fully understood.
#
# To use this tool, assign the variables below as required, save the file, then
# enter the following single line of code (without the leading '# ') into a python window in ArcCatalog (not ArcMap,
# due to processing time):
# execfile(r'PATH_TO_THIS_PYTHON_FILE')
# where PATH_TO_THIS_PYTHON_FILE is substituted for the full path of this
# python file. For example:
# execfile(r'S:\Infrastructure Planning\Staff\Jared\GIS\Tools\arcpyScripts\redistributePolygon.py')
#
##### Variables: #####
# The temp_workspace variable:
# This variable is where all the intermediate files are stored. Either create a
# geodatabase at the location shown below, or change it to a workspace
# geodatabase that has already been created. Note the use of double backslash
# (\\) instead of single backslash (\). This path must end with a double
# backslash (\\).
temp_workspace = "C:\\TempArcGIS\\scratchworkspace.gdb\\"
#
# The redistribution_layer_path variable:
# This variable contains the full path to the layer that the growth model will
# be redistributed to. Note the letter r before the path surrounded in single
# quotation marks.
redistrubtion_layer_path = r'O:\Data\Planning_IP\Admin\Staff\Jared\Sewer Strategy Report Catchments\UpperRoss\Data.gdb\Overall_Catchments_20170720_Upper_Ross' # TODO
#
# The growth_model_polygon variable:
# This variable contains the full path to the growth model feature class that
# contains the growth model zones as polygons. Note the letter r before the
# path surrounded in single quotation marks.
growth_model_polygon = r'R:\InfrastructureModels\Growth\Spatial\Database\GrowthModelGMZ.mdb\GMZ'
#
# The method_of_distribution variable:
# This variable contains an integer that represents the method used to
# redistribute the GMZ. The options are as follows:
#  - 1 - redistribution by area
#  - 2 - redistribution by number of properties
#  - 3 - redistribution by a combination of the above two methods (default). If
#  	 this method is selected, the number of properties method is used for
#  	 2016, area method is used for years >2036, and the average of the two
#  	 is used for 2016-2036. This was choosen based on advice from Brian.
method_of_distribution = 3
#
# The output variable:
# This variable contains the full path where the output file will be written.
output = r'O:\Data\Planning_IP\Admin\Staff\Jared\Sewer Strategy Report Catchments\UpperRoss\Data.gdb\UpperRoss_GrowthModelRedistributedToPSCatchments' # TODO
#
# The growthmodel_csv_path variable:
# This variable should contain the full path of the .csv file containing a
# subset of the growth model data. The .csv file reference by this variable
# should be created from the 'Pops and Emps' tab of the growth model outputs
# provided by Brian. The .csv file must contain the following columns only:
# 	"GMZ",
#	"POP_2011", "Tot_2011",
#	"POP_2016", "Tot_2016",
#	"POP_2021", "Tot_2021",
#	"POP_2026", "Tot_2026",
#	"POP_2031", "Tot_2031",
#	"POP_2036", "Tot_2036",
#	"POP_2041", "Tot_2041",
#	"POP_2046", "Tot_2046",
#	"POP_2051", "Tot_2051",
#	"POP_Full", and "Tot_Full".
# It should also contain only the growth data for the individual GMZs. Excel
# spreadsheet provided by Brian typically contain addition data below this
# table on the 'Pops and Emps' tab.  This additional data should not be
# included in the .csv file.
growthmodel_csv_path = r'O:\Data\Planning_IP\Admin\Staff\Jared\Southern Suburbs Sewer Planning Report\SouthernSuburbsGrowthModel20160908_mediumGrowth.csv' # TODO
#
# ---------------------------------------------------------------------------
# ----- Issues
# ---------------------------------------------------------------------------
#
# This tool used to generate this data has not been fully tested. The sections
# below describe the known issues. In addition to these, unknown issues may
# also exist.
#
# ##### Partially covered GMZs. #####
# The method in which GMZs are distributed to pump station catchments changes
# depending on which year is being considered. The method for each year is
# summarised below. Number of lots refers to the number of lots in a section
# of pump station catchment compared to the total number of lots in the GMZ.
# Area refers to the portion of area in a section of pump station catchment
# compared to the total area of the GMZ. Combination refers to the mean
# average of the two methods.
#  - 2016 - number of lots
#  - 2021 - combination
#  - 2026 - combination
#  - 2031 - combination
#  - 2036 - area
#  - 2041 - area
#  - 2046 - area
#  - 2051 - area
#  - Full Developed Scenario - area
#
# The distribution methods described above work well for areas where the GMZs
# are fully covered by pump station catchments and where there is an even
# distribution of population and employment EPs. For other areas, the
# redistribution can be inaccurate. For this reason, pump station catchments
# that cross into GMZs that are not fully serviced by pump station catchments
# have had their value manually adjusted.
#
# ##### Double counting issue. #####
# There is an issue with properties that cross pump station catchments being
# counted twice. This issue seems to affects only the proportion allocated, not
# the total population across the catchments. The error is negligible in the
# typical catchment where the number of properties is high and the number of
# properties crossing the boundaries is low in comparison. It does become an
# issue when the inverse is true, especially when the few properties in the
# catchments contain a high number of EP (eg, JCU, the Hospital, Lavarack
# Barracks).
#
# ##### High EP concentration over few properties. #####
# The tool assumes that population and employment EPs are evenly distributed
# across a catchment. In areas where EPs are concentrated over a few
# properties, it can calculate a concentrated population as being spread
# over several pump station catchments.
#
# ##### Intermitent data issue. #####
# The intersecting_polygons layer can have growth model data joined to it
# multiple times. for example, you will find POP_2016_2017, and POP_2021_2022
# fields. This doesn't seem to impact on the final results, but this issue
# should be fully understood before and / or fixed before this tool is used on
# other areas.
#
# For the reasons listed above, the data must be checked before being used.
#
# Jared Johnston



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
		arcpy.AddMessage("The following output filename already exists and will now be deleted: %s" % feature)
		arcpy.Delete_management(feature)
#
def calculate_field_proportion_based_on_area(field_to_calculate, total_area_field):
	"""
	Calculates the field_to_calculate for each polygon based on its percentage of the total area of the polygon to calculate from
	Arguments should be the names of the fields as strings
	"""
	arcpy.AddMessage("    Calculating %s field based on the proportion of the polygon area to the %s field" % (field_to_calculate, total_area_field))
	arcpy.CalculateField_management (intersecting_polygons, field_to_calculate, "return_area_proportion_of_total(!"+total_area_field+"!, !Shape_Area!, !" + field_to_calculate + "!)", "PYTHON_9.3", """def return_area_proportion_of_total(GMZ_total_area, Shape_Area, field_to_calculate):
	return Shape_Area/GMZ_total_area * field_to_calculate""")
#
def calculate_field_proportion_based_on_number_of_lots(field_to_calculate, larger_properties_field, local_number_of_properties_field):
	"""
	Calculates the field_to_calculate for each polygon based on the number of lots in that polygon, compared to total number of lots on the larger polygon form which the data should be interpolated.
	Arguments should be the names of the fields as strings
	"""
	arcpy.AddMessage("    Calculating %s field based on the proportion of the total properties value in the %s field" % (field_to_calculate, larger_properties_field))
	arcpy.CalculateField_management (intersecting_polygons, field_to_calculate, "return_number_proportion_of_total(!"+larger_properties_field+"!, !"+local_number_of_properties_field+"!, !" + field_to_calculate + "!)", "PYTHON_9.3", """def return_number_proportion_of_total(total_properties, local_properties, field_to_calculate):
	new_value =  (float(local_properties)/total_properties) * field_to_calculate
	return int(new_value)""")
#
def calculate_field_proportion_based_on_combination(field_to_calculate, larger_properties_field, local_number_of_properties_field, total_area_field):
	"""
	Calculates the the field based on area, and by number of lots, and assigned the average between the two as the value.
	"""
	arcpy.AddMessage("    Calculating %s field as the average value between area and number of lots method")
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
	properties = r"O:\\Data\\Planning_IP\\Spatial\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Cadastral\\sde_vector.TCC.Properties"
	# see: http://gis.stackexchange.com/questions/35468/what-is-the-proper-syntax-and-usage-for-arcgis-in-memory-workspace
	properties_SpatialJoin = workspace + "properties_SpatialJoin"
	stats = workspace + "stats"
	delete_if_exists(properties_SpatialJoin)
	delete_if_exists(stats)
	arcpy.AddMessage("    joining properties to "+ feature_class +" and outputing to %s" % properties_SpatialJoin)
	arcpy.SpatialJoin_analysis(feature_class, properties, properties_SpatialJoin, "JOIN_ONE_TO_MANY", "KEEP_ALL", "", "INTERSECT")
	arcpy.AddMessage("    Calculating statistics table at stats")
	arcpy.Statistics_analysis(properties_SpatialJoin, stats, "Join_Count SUM","TARGET_FID")
	arcpy.AddMessage("    joining back to intersecting_polygons")
	arcpy.JoinField_management (feature_class, "OBJECTID", stats, "TARGET_FID", "FREQUENCY")
	arcpy.AddMessage("    renaming 'FREQUENCY' to '%s'" % field_name)
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
	arcpy.AddMessage("Computing the polygons that intersect both features")
	arcpy.Intersect_analysis ([redistribution_layer, data_layer], intersecting_polygons, "ALL", "", "INPUT")
	arcpy.AddMessage("Output: %s" % intersecting_polygons)
#
def join_growthmodel_table_to_intersecting_polygons():
	fields_to_be_joined = "" # this list may need to be edited depending on what is required of the tool. To join all fields, set this variable to an empty string (""). To specify a list of fields, use a list, eg, ["POP_2011", "Tot_2011", "POP_2016", "Tot_2016"]. Although, this list may be better set in the fields_list variable.
	arcpy.AddMessage("Joining growthmodel to interseting polygons")
	arcpy.JoinField_management (intersecting_polygons, "GMZ", growthmodel_table, "GMZ", fields_to_be_joined)
	arcpy.AddMessage("Output: %s" % intersecting_polygons)
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
	arcpy.AddMessage("    Creating %s layer" % data_layer_rejoined)
	delete_if_exists(data_layer_rejoined)
	arcpy.AddMessage ("    data_layer = %s" % data_layer)
	arcpy.AddMessage ("    intersecting_polygons = %s" % intersecting_polygons)
	arcpy.AddMessage ("    data_layer_rejoined = %s" % data_layer_rejoined)
	arcpy.SpatialJoin_analysis (data_layer, intersecting_polygons, data_layer_rejoined, "JOIN_ONE_TO_ONE", "KEEP_COMMON", fieldmappings_data, "INTERSECT", -0.5)
	arcpy.AddMessage("    %s includes %s field" % (data_layer_rejoined, total_properties_including_double_counted_field))
	arcpy.JoinField_management (data_layer, "OBJECTID", data_layer_rejoined,  "TARGET_FID", total_properties_including_double_counted_field)
	arcpy.AddMessage("    %s field joined to %s" % (total_properties_including_double_counted_field, data_layer_rejoined))
#
def max_total_properties_field():
	"""
	Calculates the total_properties_including_double_counted_field to be the max of itself or the total_properties_field.
	"""
	arcpy.CalculateField_management (intersecting_polygons, total_properties_including_double_counted_field, "max([!"+total_properties_including_double_counted_field+"!, !"+total_properties_field+"!])", "PYTHON_9.3")


## Script Arguments - These are the values that will typically change. They have been built to be used in a model builder with default values proivded if none are received from the model. If run as a python scrip, these arguments will take their values from the variables provided at the top of the script.
#
workspace = arcpy.GetParameterAsText(5)
if workspace == '#' or not workspace:
    workspace = temp_workspace
    arcpy.AddMessage("you have not provided a workspace. Using default: %s" % workspace)
#
redistribution_layer_name = arcpy.GetParameterAsText(0)
if redistribution_layer_name == '#' or not redistribution_layer_name:
    redistribution_layer_name = redistrubtion_layer_path
    arcpy.AddMessage("you have not provided a redistribution_layer_name. using default: %s" % redistribution_layer_name)
#
data_layer = arcpy.GetParameterAsText(1)
if data_layer == '#' or not data_layer:
    #raise ValueError('You must provide a data_layer')
    data_layer = growth_model_polygon
arcpy.AddMessage("data layer: %s" % data_layer)
delete_if_exists(workspace + "data_layer")
arcpy.Select_analysis (data_layer, workspace + "data_layer")
data_layer = workspace + "data_layer"
arcpy.AddMessage("new data layer: %s" % data_layer)
#
distribution_method = arcpy.GetParameter(2)
if distribution_method == '#' or not distribution_method:
    distribution_method = method_of_distribution # 1 - by area, 2 - by number of properties, 3 - by a combination of the two methods.
    									    # for distribution_method = 3, number of properties method is used for 2016, area method is used for >2036, and
									    # the average of the two is used for 2016-2036.
    arcpy.AddMessage("you have not provided a distribution_method. 1 = distribute by area, 2 = distribute my number of properties. Using %s by default" % distribution_method)
if distribution_method in [1, 2, 3]:
	arcpy.AddMessage("distribution method %s is valid" % distribution_method)
else:
	arcpy.AddMessage("distribution method = %s" % distribution_method)
	arcpy.AddMessage("distribution method type = %s" % distribution_method.type)
	raise ValueError('Distribution method must be either 1, 2 or 3')
#
output_filename = arcpy.GetParameterAsText(3)
if output_filename == '#' or not output_filename:
    #output_filename = workspace + "redistributedPolygon" # provide a default value if unspecified # this should be the default if running from a python model tool.
    output_filename = output
    arcpy.AddMessage("you have not provided an output_layer. This tool will now delete the default file and rewrite it: %s" % output_filename)
    delete_if_exists(output_filename)
#
# this table should be created from the 'Pops and Emps' tab of the growth model outputs provided by Brian. The fields in the table I'm currently using are ["GMZ", "POP_2011", "Tot_2011", "POP_2016", "Tot_2016", "POP_2021", "Tot_2021", "POP_2026", "Tot_2026", "POP_2031", "Tot_2031", "POP_2036", "Tot_2036", "POP_2041", "Tot_2041", "POP_2046", "Tot_2046", "POP_2051", "Tot_2051", "POP_Full", "Tot_Full"]
growthmodel_csv = arcpy.GetParameterAsText(4)
if growthmodel_csv == '#' or not growthmodel_csv:
    growthmodel_csv = growthmodel_csv_path
    arcpy.AddMessage("you have not provided a growthmodel_csv. Using default: %s" % growthmodel_csv)

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
arcpy.AddMessage("Converting Growth Model from a .csv into a gdb table")
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
			arcpy.AddMessage("calculating %s field from total GMZ number of properties" % GM_field)
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

redistribution_layer_field_list = arcpy.ListFields(redistribution_layer_name)
for field in redistribution_layer_field_list:
	if field.name not in ['OBJECTID', 'Shape_Length', 'Shape_Area', 'Join_Count', 'Shape']:
		arcpy.AddMessage("Adding fieldmap for %s" % field.name)
		fm = arcpy.FieldMap()
		fm.addInputField(redistribution_layer_name, field.name)
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
delete_if_exists(output_filename)
arcpy.AddMessage("joining intersecting_polygons back to redistribution layer")
arcpy.SpatialJoin_analysis (redistribution_layer, intersecting_polygons, output_filename, "JOIN_ONE_TO_ONE", "KEEP_ALL", fieldmappings, "CONTAINS", "#", "#")
arcpy.AddMessage("Successfully redistributed %s to %s" % (data_layer, redistribution_layer))
arcpy.AddMessage("Output file can be found at %s" % output_filename)
