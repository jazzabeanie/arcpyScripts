# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# redistributePolygon.py
# Created on: 2016-08-01 13:00:00
#
# Usage: redistributePolygon <redistribution_layer> <target_layer> <distribution_method> <output_filename> <growthmodel_csv>
# Description: 
# This model splits the target polygon based on intersection with the redistribution polygon. It then joins the split polygon back together based on a common attibute that was carried over from the redistribution polygon. it takes the argument:
#  - redistribution_layer: the areas that the target feature should be rejoined to, eg, Sewer Pump Station Catchments
#  - target_layer: the layer with the data that need to be redistributed, eg, Growth Model Zones.
#  - distribution_method: The method by which the values in the target_layer should be distibuted when split. Initally this tool will be built with only distribution by area, but in the future this may include number of properties or percentage of undeveloped land.
#  - output_filename:
#  - growthmodel_csv: table containing growth model data to be joined
# 
# The Manhole number is given by the Upstream Manhole Number field in the GravityMain. This field is passed to the PropertyConnectionPoints layer by selecting any PropertyConnectionPoints that aren't intersecting with a service line. The Manhole Number is then passed to the property by a spatial join.
#
# execfile(r'S:\Infrastructure Planning\Staff\Jared\GIS\Tools\arcpyScripts\redistributePolygon.py')
# 
# ---------------------------------------------------------------------------

## defining functions
def calculate_field_proportion_based_on_area(field_to_calculate, total_area_field):
	"""
	Calculates the field_to_calculate for each polygon based on its percentage of the total area of the polygon to calculate from
	Arguments should be the names of the fields as strings
	"""
	print("Calculating %s field based on the proportion of the polygon area to the %s field" % (field_to_calculate, total_area_field))
	arcpy.CalculateField_management (intersecting_polygons, field_to_calculate, "return_area_proportion_of_total(!"+total_area_field+"!, !Shape_Area!, !" + field_to_calculate + "!)", "PYTHON_9.3", """def return_area_proportion_of_total(GMZ_total_area, Shape_Area, field_to_calculate):
	return Shape_Area/GMZ_total_area * field_to_calculate""")

def calculate_field_proportion_based_on_number_of_lots(field_to_calculate):
	"""
	"""
	print("#todo: write this method")

## Preprocessing
import arcpy
#
workspace = "C:\\TempArcGIS\\scratchworkspace.gdb\\"
arcpy.env.OverwriteOutput = True

## Script arguments
#
## this section is commented out because I am now getting redistrbution_layer form a list of layers. I've left it here incase this tool is converted into a more general tool that can be applied to any two layers
#redistribution_layer = arcpy.GetParameterAsText(0)
#if redistribution_layer == '#' or not redistribution_layer:
#    #raise ValueError('You must provide a redistribution_layer')
#    redistribution_layer = r'S:\Infrastructure Planning\Staff\Jared\Southern Suburbs Sewer Planning Report\SewerData.gdb\RiversideRidge_PS_catchments' # provide a default value if unspecified
#print("redistribution layer: %s" % redistribution_layer)
#arcpy.AddMessage("AddMessage: redistribution layer: %s" % redistribution_layer)
#redistribution_layers = [	'RiversideRidge_PS_catchments',
#				'RoseneathTruckStop_PS_catchments',
#				'TheVillage_PS_catchments',
#				'FairfieldWaters_PS_catchments']
redistribution_layers = [	'RiversideRidge_PS_catchments', ]
#
target_layer = arcpy.GetParameterAsText(1)
if target_layer == '#' or not target_layer:
    #raise ValueError('You must provide a target_layer')
    target_layer = r'S:\Infrastructure Planning\Spatial Data\Water_sewer\Sewer_Catchments_2015\Sewer_Catchments_2015.mdb\GMZ_2015' # provide a default value if unspecified
print("target layer: %s" % target_layer)
#
#distribution_method = arcpy.GetParameterAsText(2)
distribution_method = 1
#if distribution_method == '#' or not distribution_method:
#    distribution_method = 1 # provide a default value if unspecified
#    arcpy.AddMessage("you have not provided a distribution_method. Using area method by default")
#
output_filename = arcpy.GetParameterAsText(3)
if output_filename == '#' or not output_filename:
    output_filename = r'C:\TempArcGIS\scratchworkspace.gdb\redistributedPolygon' # provide a default value if unspecified
    print("you have not provided an output_layer. This tool will now delete the default file and rewrite it: %s" % output_filename)
    if arcpy.Exists(output_filename):
    	print("The following output filename already exists and will now be deleted: %s" % output_filename)
    	arcpy.Delete_management(output_filename)
#
# this table should be created from growth model outputs provided by Brian. The fields in the table I'm currently using are ["GMZ", "POP 2011", "Total 2011", "POP 2016", "Total 2016", "POP 2021", "Total 2021", "POP 2026", "Total 2026", "POP 2031", "Total 20131", "POP 2036", "Total 2036", "POP 2041", "Total 2041", "POP 2046", "Total 2046", "POP 2051", "Total 2051", "POP Full", "Total Full"]
growthmodel_csv = arcpy.GetParameterAsText(4)
if growthmodel_csv == '#' or not growthmodel_csv:
    growthmodel_csv = r'S:\Infrastructure Planning\Staff\Jared\Southern Suburbs Sewer Planning Report\GrowthModelutputs30June2016.csv' # provide a default value if unspecified
    arcpy.AddMessage("you have not provided a growthmodel_csv. Using default: %s" % growthmodel_csv)
    print("you have not provided a growthmodel_csv. Using default: %s" % growthmodel_csv)

## Local variables:
intersecting_polygons = workspace + "intersecting_polygons"
growthmodel_table = workspace + "growthmodel_table"

## Import grothmodel_table
if arcpy.Exists(growthmodel_table):
	print("The following output filename already exists and will now be deleted: %s" % growthmodel_table)
    	arcpy.Delete_management(growthmodel_table)
# Convert Growth Model from a .csv into a gdb table
arcpy.CopyRows_management (growthmodel_csv, growthmodel_table)

for item in redistribution_layers:
	redistribution_layer = r'S:\Infrastructure Planning\Staff\Jared\Southern Suburbs Sewer Planning Report\SewerData.gdb\\' + item
	## create intersecting_polygons layer
	if arcpy.Exists(intersecting_polygons):
		print("The following output filename already exists and will now be deleted: %s" % intersecting_polygons)
		arcpy.Delete_management(intersecting_polygons)
	else:
		print("intersecting_polygons does not exist: %s" % intersecting_polygons)
	arcpy.AddMessage("Computing the polygons that intersect both features")
	print("Computing the polygons that intersect both features")
	arcpy.Intersect_analysis ([[target_layer, 1], [redistribution_layer, 2]], intersecting_polygons, "ALL", "", "")
	arcpy.AddMessage("Output: %s" % intersecting_polygons)
	print("Output: %s" % intersecting_polygons)

	## Join growthmodel_table to intersecting_polygons
	fields_to_be_joined = "POP_2011" # this list may need to be edited depending on what is required of the tool. To join all fields, set this variable to an empty string ("")
	print("Executing Join Field")
	arcpy.JoinField_management (intersecting_polygons, "GMZ", growthmodel_table, "GMZ", fields_to_be_joined) #todo: replace fields_to_be_joined with "" so that all fields are joined by default
	arcpy.AddMessage("Output: %s" % intersecting_polygons)
	print("Output: %s" % intersecting_polygons)

	## Recalculate groth model fields
	#todo: only execute this following code if area is selected a redistribution method. If other methods are selected, add additional code
	for GM_field in ["POP_2011", "Total_2011", "POP_2016", "Total_2016", "POP_2021", "Total_2021", "POP_2026", "Total_2026", "POP_2031", "Total_20131", "POP_2036", "Total_2036", "POP_2041", "Total_2041", "POP_2046", "Total_2046", "POP_2051", "Total_2051", "POP_Full", "Total_Full"]:
		fields = arcpy.ListFields(intersecting_polygons, GM_field)
		if len(fields) == 1: # essentially, if field exist. See: https://epjmorris.wordpress.com/2015/04/22/how-can-i-check-to-see-if-an-attribute-field-exists-using-arcpy/
			if distribution_method == 1:
				calculate_field_proportion_based_on_area(GM_field, "GMZ_TOTAL_AREA")
			elif distribution_method == 2:
				calculate_field_proportion_based_on_number_of_lots(GM_field)

	## setup field maps for Spatial Join
	# create FieldMap and FieldMappins objects
	fieldmappings = arcpy.FieldMappings()
	fm_layer = arcpy.FieldMap()
	fm_REF_NO = arcpy.FieldMap()
	fm_GMZ = arcpy.FieldMap()
	fm_POP_2011 = arcpy.FieldMap()
	# add the source fields for each FieldMap object, eg, some_FieldMap_object.addInputField(source_feature_class, field_name)
	fm_layer.addInputField(redistribution_layer, "Layer")
	fm_REF_NO.addInputField(redistribution_layer, "REF_NO")
	fm_GMZ.addInputField(intersecting_polygons, "GMZ")
	fm_POP_2011.addInputField(intersecting_polygons, "POP_2011")
	# Assign a field name for the output file. NOTE: in examples this has been done in separete steps, if it doesn't work, change this.
	print("assigning output field name")
	fm_layer.outputField.name = "PS_name"
	fm_REF_NO.outputField.name = "PS_REF_NO"
	fm_GMZ.outputField.name = "GMZs_contrib"
	fm_POP_2011.outputField.name = "PS_POP_2011"
	print("done assigning output field name")
	# Assign output field type
	fm_GMZ.outputField.type = "String"
	fm_GMZ.outputField.length = 100
	# Set merge rules
	fm_POP_2011.mergeRule = "Sum"
	fm_GMZ.mergeRule = "Join"
	fm_GMZ.joinDelimiter = ", "
	# add FieldMap objects to FieldMappings object
	fieldmappings.addFieldMap(fm_layer)
	fieldmappings.addFieldMap(fm_REF_NO)
	#fieldmappings.addFieldMap(fm_GMZ) # when I leave this in I get "ExecuteError: ERROR 001156: Failed on input OID 1, could not write value '412, 379, 413, 201, 411, 410' to output field GMZ Failed to execute (SpatialJoin)." My hypothesis is that is fails because GMZs are integers and can't be written to a text field. I've looked breifly how to cast the input field to a string, but I can't seem to find out how (this page might give more insight: http://gis.stackexchange.com/questions/158922/change-field-type-using-field-mapping-for-list-of-tables-using-python). All I can think to do is add a new field and copy the values accross converting to string in the process. This field isn't neccesary so I'll ignore it.
	fieldmappings.addFieldMap(fm_POP_2011)

	## Spatially Join intersecting_polygons back to redistribution layer
	print("joining intersecting_polygons back to redistribution layer")
	arcpy.SpatialJoin_analysis (redistribution_layer, intersecting_polygons, output_filename+"_"+item, "JOIN_ONE_TO_ONE", "KEEP_ALL", fieldmappings, "CONTAINS", "#", "#") #output_filename+"_"+item is used here because I am itterating through a list of files. This should be just output_filename if the script is operating on only 1 layer
	print("Successfully redistributed %s to %s" % (target_layer, redistribution_layer))
	print("Output file can be found at %s" % output_filename)



