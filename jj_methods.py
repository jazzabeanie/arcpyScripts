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
import __main__
from datetime import datetime
# see here for logging best practices: https://stackoverflow.com/questions/15727420/using-python-logging-in-multiple-modules

arcpy.env.workspace = r'O:\Data\Planning_IP\Admin\Staff\Jared\GIS\Tools\arcpyScripts\TestingDataset.gdb'
logging = logging.getLogger(__name__)
testing = True


# TODO: create a bunch of functions that create test data sets. For example: add the function below, but let the list of verticies be passed in as an argument.
def create_polygon(output, *shapes_lists):
    """
    Creates a polygon at the output from the list of points provided. Multiple points list can be provided.
    """
    print "directory = " + get_directory_from_path(output)
    print "name = " + get_file_from_path(output)
    arcpy.CreateFeatureclass_management(
        get_directory_from_path(output), # out_path
        get_file_from_path(output), # out_name
        "POLYGON") # geometry_type
    for shape_list in shapes_lists:
        point_array = []
        for vertex in shape_list:
            point_array.append(arcpy.Point(vertex[0], vertex[1]))
        array = arcpy.Array(point_array)
        polygon = arcpy.Polygon(array)
        # Open an InsertCursor and insert the new geometry
        cursor = arcpy.da.InsertCursor(output, ['SHAPE@'])
        cursor.insertRow([polygon])
    del cursor


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
    """Calculates a target field from a field on another featre based on spatial intersect."""
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


def redistributePolygon(inputs):
    """This function redistributes a feature class to another feature class based on different methods of distribution:
    1: By proportion of area
    2: By proportion of number of lots
    3: By the average of 1 and 2

    It take a dictionary called 'inputs' as an argument, which contains the following keys:
        redistribution_layer_name
        growth_model_polygon
        output_filename
        distribution_method
        field_list"""
    try:
        if inputs["distribution_method"] in [1, 2, 3]:
            logging.info("distribution method %s is valid" % inputs["distribution_method"])
        else:
            logging.info("distribution method = %s" % inputs["distribution_method"])
            raise AttributeError('distribution method must be either 1, 2 or 3')
        if hasattr(__main__, 'testing'):
            testing = __main__.testing
        if hasattr(__main__, 'now'):
            now = __main__.now
        else:
            now = r'%s' % datetime.now().strftime("%Y%m%d%H%M")
        logging.info("For redistributePolygon tool, now (which is sometimes used in filenames) = %s" % now)
        logging.info("For redistributePolygon tool, testing = %s" % testing)
        if testing:
            # inputs["distribution_method"] = 3  # TODO: incorporate this into the unit tests when this is moved into jj_methods
            keep_method = "KEEP_COMMON"
        else:
            keep_method = "KEEP_ALL"

        def calculate_field_proportion_based_on_area(field_to_calculate, total_area_field):
            """
            Calculates the field_to_calculate for each polygon based on its percentage of the total area of the polygon to calculate from
            Arguments should be the names of the fields as strings
            """
            logging.info("Executing calculate_field_proportion_based_on_area(%s, %s)" % (field_to_calculate, total_area_field))
            logging.info("    Calculating %s field based on the proportion of the polygon area to the %s field" % (field_to_calculate, total_area_field))
            arcpy.CalculateField_management (intersecting_polygons, field_to_calculate, "return_area_proportion_of_total(!"+total_area_field+"!, !Shape_Area!, !" + field_to_calculate + "!)", "PYTHON_9.3", """def return_area_proportion_of_total(total_area_field, Shape_Area, field_to_calculate):
            return Shape_Area/total_area_field * int(field_to_calculate)""")
        #
        def calculate_field_proportion_based_on_number_of_lots(field_to_calculate, larger_properties_field, local_number_of_properties_field):
            """
            Calculates the field_to_calculate for each polygon based on the number of lots in that polygon, compared to total number of lots on the larger polygon form which the data should be interpolated.
            Arguments should be the names of the fields as strings
            """
            logging.info("Executing calculate_field_proportion_based_on_number_of_lots(%s, %s, %s)" % (field_to_calculate, larger_properties_field, local_number_of_properties_field))
            logging.info("    Calculating %s field based on the proportion of the total properties value in the %s field using %s" % (field_to_calculate, larger_properties_field, local_number_of_properties_field))
            arcpy.CalculateField_management (intersecting_polygons, field_to_calculate, "return_number_proportion_of_total(!"+larger_properties_field+"!, !"+local_number_of_properties_field+"!, !" + field_to_calculate + "!)", "PYTHON_9.3", """def return_number_proportion_of_total(total_properties, local_properties, field_to_calculate):
            new_value =  (float(local_properties)/total_properties) * int(field_to_calculate)
            return int(new_value)""")
        #
        def calculate_field_proportion_based_on_combination(field_to_calculate, larger_properties_field, local_number_of_properties_field, total_area_field):
            """
            Calculates the the field based on area, and by number of lots, and assigned the average between the two as the value.
            """
            logging.info("Executing calculate_field_proportion_based_on_combination(%s, %s, %s, %s)" % (field_to_calculate, larger_properties_field, local_number_of_properties_field, total_area_field))
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
            Adds a field to the feature class containing the number of properties (from the SDE) in each polygon.
            """ # Previously properties would get double counted. This issue has now been fixed.
            logging.info("Executing add_property_count_to_layer_x_with_name_x(%s, %s)" % (feature_class, field_name))
            properties = r"O:\\Data\\Planning_IP\\Spatial\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Cadastral\\sde_vector.TCC.Properties"
            feature_layer = "add_property_count_to_layer_x_with_name_x_feature_layer"
            delete_if_exists(feature_layer)
            logging.info("    making feature layer from feature class %s" % feature_class)
            arcpy.MakeFeatureLayer_management(
                    feature_class, # in_features
                    feature_layer, # out_layer
                    "#", # where_clause
                    "#", # workspace
                    "#") # field_info
            if (field_in_feature_class("TARGET_FID", feature_layer)):
                logging.info("    deleteing TARGET_FID field from feature_layer")
                arcpy.DeleteField_management(feature_layer, "TARGET_FID")
            properties_SpatialJoin = "properties_SpatialJoin"
            delete_if_exists(properties_SpatialJoin)
            stats = "stats"
            delete_if_exists(stats)
            logging.info("    joining properties to "+ feature_layer +" and outputing to %s" % properties_SpatialJoin)
            arcpy.SpatialJoin_analysis(
                    properties, # target_features
                    feature_layer, # join_features
                    properties_SpatialJoin, # out_feature_class
                    "JOIN_ONE_TO_MANY", # join_operation
                    "KEEP_COMMON", # join_type
                    "#", # field_mapping
                     "HAVE_THEIR_CENTER_IN", # match_option
                    "#", # search_radius
                    "#")# distance_field_name
            logging.info("    Calculating statistics table at stats")
            arcpy.Statistics_analysis(properties_SpatialJoin, stats, "Join_Count SUM","JOIN_FID")
            logging.info("    joining back to %s" % feature_class)
            arcpy.JoinField_management (feature_class, "OBJECTID", stats, "JOIN_FID", "FREQUENCY")
            logging.info("    renaming 'FREQUENCY' to '%s'" % field_name)
            arcpy.AlterField_management (feature_class, "FREQUENCY", field_name)
        #
        def create_intersecting_polygons():
            """
            Creates intersecting_polygons layer by intersecting redistribution_layer (PS_Catchments) and data_layer (GMZ).
            """
            logging.info("Executing create_intersecting_polygons")
            delete_if_exists(intersecting_polygons)
            logging.info("    Computing the polygons that intersect both features")
            arcpy.Intersect_analysis ([redistribution_layer, data_layer], intersecting_polygons, "ALL", "", "INPUT")
            logging.info("    Output: %s" % intersecting_polygons)
        #

        global local_number_of_properties_field
        local_number_of_properties_field = "local_counted_properties"
        global total_properties_field
        total_properties_field = "total_counted_properties"
        global intersecting_polygons
        intersecting_polygons = "intersecting_polygons"
        global growthmodel_table
        growthmodel_table = "growthmodel_table"
        global redistribution_layer
        redistribution_layer = "redistribution_layer"
        delete_if_exists(redistribution_layer)
        global total_area_field
        total_area_field = "GMZ_TOTAL_AREA"
        global data_layer
        data_layer = "data_layer"
        delete_if_exists("data_layer")
        arcpy.CopyFeatures_management(inputs["growth_model_polygon"], data_layer)
        arcpy.AddField_management(data_layer, total_area_field, "FLOAT")
        arcpy.CalculateField_management(data_layer, total_area_field, "!Shape_Area!", "PYTHON_9.3")

        add_property_count_to_layer_x_with_name_x(data_layer, total_properties_field)

        arcpy.CopyFeatures_management(inputs["redistribution_layer_name"], redistribution_layer)

        create_intersecting_polygons()

        add_property_count_to_layer_x_with_name_x(intersecting_polygons, local_number_of_properties_field)

        ## Recalculate groth model fields
        for GM_field in inputs["field_list"]:
            if field_in_feature_class(GM_field, intersecting_polygons):
                if inputs["distribution_method"] == 1:
                    calculate_field_proportion_based_on_area(GM_field, total_area_field)
                elif inputs["distribution_method"] == 2:
                    logging.info("calculating %s field from total GMZ number of properties" % GM_field)
                    calculate_field_proportion_based_on_number_of_lots(GM_field, total_properties_field, local_number_of_properties_field)
                elif inputs["distribution_method"] == 3:
                    if GM_field in  ["POP_2016", "Tot_2016"]:
                        calculate_field_proportion_based_on_number_of_lots(GM_field, total_properties_field, local_number_of_properties_field)
                    elif GM_field in  ["POP_2036", "Tot_2036", "POP_2041", "Tot_2041", "POP_2046", "Tot_2046", "POP_2051", "Tot_2051", "POP_Full", "Tot_Full"]:
                        calculate_field_proportion_based_on_area(GM_field, total_area_field)
                    elif GM_field in  ["POP_2021", "Tot_2021", "POP_2026", "Tot_2026", "POP_2031", "Tot_2031"]:
                        calculate_field_proportion_based_on_combination(GM_field, total_properties_field, local_number_of_properties_field, total_area_field)
                    elif GM_field in  ["POP_2011", "Tot_2011"]:
                        arcpy.CalculateField_management (intersecting_polygons, GM_field, "returnNone()", "PYTHON_9.3", """def returnNone():
            return None""")


        ## Spatially Join intersecting_polygons back to redistribution layer
        fieldmappings = arcpy.FieldMappings()
        for field in arcpy.ListFields(inputs["redistribution_layer_name"]):
            if field.name not in ['OBJECTID', 'Shape_Length', 'Shape_Area', 'Join_Count', 'Shape']:
                logging.info("Adding fieldmap for %s" % field.name)
                fm = arcpy.FieldMap()
                fm.addInputField(inputs["redistribution_layer_name"], field.name)
                renameFieldMap(fm, field.name)
                fieldmappings.addFieldMap(fm)
        for GM_field in inputs["field_list"]:
            if field_in_feature_class(GM_field, intersecting_polygons):
                fm_POP_or_Total = arcpy.FieldMap()
                fm_POP_or_Total.addInputField(intersecting_polygons, GM_field)
                renameFieldMap(fm_POP_or_Total, GM_field)
                fm_POP_or_Total.mergeRule = "Sum"
                fieldmappings.addFieldMap(fm_POP_or_Total)
        delete_if_exists(inputs["output_filename"])
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
        raise e

def for_each_feature(feature_class, cb):
    """
    Itterates over each feature in a feature class, and calls a function with the feature selected.
    """
    # TODO: get workspace from __main__
    # https://gis.stackexchange.com/questions/79619/what-is-python-equivalent-of-modelbuilders-iterate-feature-selection
    # https://www.protechtraining.com/content/python_fundamentals_tutorial-functional_programming
    feature_layer='feature_layer'
    with arcpy.da.SearchCursor(feature_class, "OBJECTID") as cursor:
        for row in cursor:
            arcpy.MakeFeatureLayer_management(
                    in_features=feature_class,
                    out_layer=feature_layer,
                    where_clause="OBJECTID = %s" % row[0])
            cb(feature_layer)
            arcpy.Delete_management(feature_layer)

