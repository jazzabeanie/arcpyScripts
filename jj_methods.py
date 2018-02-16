from __future__ import division
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
try:
    import progressbar
    bar = progressbar.ProgressBar()
except ImportError as e: # ie, when progressbar is not installed (this is untested)
    def bar(itterable):
        return itterable

# see here for logging best practices: https://stackoverflow.com/questions/15727420/using-python-logging-in-multiple-modules

logger = logging.getLogger(__name__)
testing = True


def create_polygon(output, *shapes_lists):
    """
    Creates a polygon at the output from the list of points provided. Multiple points list can be provided.
    """
    if os.sep not in output:
        output=arcpy.env.workspace+"\\"+output
    delete_if_exists(output)
    logger.debug("directory = " + get_directory_from_path(output))
    logger.debug("name = " + get_file_from_path(output))
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
    return output


def create_basic_polygon(output="basic_polygon", left_x=479579.725, lower_y=7871431.255, right_x=479593.812, upper_y=7871508.742):
    array = [(left_x,lower_y),
         (left_x,upper_y),
         (right_x,upper_y),
         (right_x,lower_y),
         (left_x,lower_y)]
    if os.sep not in output:
        output=arcpy.env.workspace+"\\"+output
    delete_if_exists(output)
    create_polygon(output, array)
    return output


def create_point(x_coord=479585 , y_coord=7871450, output="basic_point"):
    """
    Creates a features class with a single point with the co-ordinates as passed in.

    Arguments:
        x_coord - the x_coordinate of the point (479585 by default)
        y_coord - the y_coordinate of the point (7871450 by default)
        output - the location to save the output
    """
    if os.sep not in output:
        output=arcpy.env.workspace+"\\"+output
    delete_if_exists(output)
    logger.debug("directory = " + get_directory_from_path(output))
    logger.debug("name = " + get_file_from_path(output))
    output = arcpy.CreateFeatureclass_management(
        out_path=get_directory_from_path(output),
        out_name=get_file_from_path(output),
        geometry_type="POINT")
    cursor = arcpy.da.InsertCursor(output, ['SHAPE@XY'])
    cursor.insertRow([(x_coord, y_coord)])
    del cursor
    return output
    # help: http://pro.arcgis.com/en/pro-app/arcpy/get-started/writing-geometries.htm


def create_points(coords_list=None, output="points"):
    """
    Creates a features class with a bunch of points as passed in.
    """
    # if type(coords_list) != type(()) or type(coords_list) != type([]):
    if type(coords_list) != type(()):
        logging.debug("coords_list type = %s" % type(coords_list))
        raise AttributeError("Error: coords_list is not a tuple or a list")
    else:
        logging.debug("coords_list = %s" % (coords_list, ))
        try:
            for i in coords_list:
                for c in i:
                    logging.debug("item in coords_list is all good")
        except TypeError as e:
            logging.debug("items in coords_list aren't itterable.")
            logging.debug(e.args[0])
            raise AttributeError('Error: item in coords_list are not itterable. create_points, take a list/tuple of coordinates as the first argument, where each item is a list/tuple containing the x and y coordinates of the point to be added. One of these was found to not be itterable.\nPlease call create_points like so: `create_points(((1, 2), (5, 2)), output="filename")`')
    if os.sep not in output:
        output=arcpy.env.workspace+"\\"+output
    delete_if_exists(output)
    logger.debug("directory = " + get_directory_from_path(output))
    logger.debug("name = " + get_file_from_path(output))
    output = arcpy.CreateFeatureclass_management(
        out_path=get_directory_from_path(output),
        out_name=get_file_from_path(output),
        geometry_type="POINT")
    for p in coords_list:
        cursor = arcpy.da.InsertCursor(output, ['SHAPE@XY'])
        cursor.insertRow([p])
        # help: http://pro.arcgis.com/en/pro-app/arcpy/get-started/writing-geometries.htm
    del cursor
    return output


def delete_if_exists(layer):
    """Deleted the passed in layer if it exists. This avoids errors."""
    if arcpy.Exists(layer):
        logger.debug("Deleting %s" % layer)
        arcpy.Delete_management(layer)
        # logger.debug("%s exists = %s" % (layer, arcpy.Exists(layer)))


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
    # Is this function necessary? I can get arguments with sys.argv. arcpy.GetParamterAsText is only useful when a script is converted to model builder tool?
    # I don't think this function is actually used anywhere except jj_tests.py
    args = tuple(arcpy.GetParameterAsText(i)
                 for i in range(arcpy.GetArgumentCount()))
    logger.debug("args = " + str(args))
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
    logger.debug("Calculating %s.%s from %s.%s" % (target_layer, target_field, join_layer, join_field))
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
    logger.debug("  Adding and calculating %s = %s" % (tmp_field_name, join_field))
    arcpy.AddField_management(join_layer_layer, tmp_field_name, join_field_object.type)
    arcpy.CalculateField_management(join_layer_layer, tmp_field_name, "!" + join_field + "!", "PYTHON", "")
    logger.debug("  Spatially joining %s to %s" % (join_layer, target_layer))
    arcpy.SpatialJoin_analysis(target_layer, join_layer, output)
    output_fields = arcpy.ListFields(output)
    new_fields = [f for f in output_fields if f.name not in original_field_names]
    logger.debug("  Calculating %s = %s" % (target_field, tmp_field_name))
    arcpy.CalculateField_management(output, target_field, "!" + tmp_field_name + "!", "PYTHON", "") # FIXME: may need to make null values 0.
    logger.debug("  Deleting joined fields:")
    for f in new_fields:
        if not f.required:
            logger.debug("    %s" % f.name)
            arcpy.DeleteField_management(output, f.name)
        else:
            logger.warning("    Warning: Cannot delete required field: %s" % f.name)


def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})


def get_file_from_path(path):
    """Returns the filename from a provided path."""
    head, tail = os.path.split(path)
    return tail or os.path.basename(head)


def get_directory_from_path(path):
    """Returns the directory from a provided path."""
    # Does this need the abspath part? With it there, if I put in a plain
    # string, the current working directory will be returned.
    return os.path.dirname(os.path.abspath(path))


def test_print():
    """tests that methods in this module can be called."""
    logger.info("success")
    logger.debug("fail")


def redistributePolygon(redistribution_inputs):
    """This function redistributes a feature class to another feature class based on different methods of distribution:
    1: By proportion of area
    2: By proportion of number of lots
    3: By a combination of 1 and 2

    It take a dictionary called 'redistribution_inputs' as an argument, which contains the following keys:
    - layer_to_redistribute_to
    - layer_to_be_redistributed
    - output_filename
    - distribution_method
    - fields_to_be_distributed"""
    try:
        log("redistribution_inputs:")
        for key in redistribution_inputs:
            log("  %s = %s" % (key, redistribution_inputs[key]))
        if arcpy.Describe(redistribution_inputs["layer_to_redistribute_to"]).spatialReference.name != arcpy.Describe(redistribution_inputs["layer_to_be_redistributed"]).spatialReference.name :
            logger.warning("WARNING: %s and %s do not have the same coordinate system. The area fields may not calculate with the same coordinates. According to http://pro.arcgis.com/en/pro-app/tool-reference/data-management/calculate-field.htm, 'Using areal units on geographic data will yield questionable results as decimal degrees are not consistent across the globe.'\rThe best approach is to use the Project (Data Management) tool to reproject the data into MGA Zone 55 and try again." % (redistribution_inputs["layer_to_redistribute_to"], redistribution_inputs["layer_to_be_redistributed"]))
            logger.warning("  layer_to_redistribute_to: %s" % arcpy.Describe(redistribution_inputs["layer_to_redistribute_to"]).spatialReference.name)
            logger.warning("  layer_to_be_redistributed: %s" % arcpy.Describe(redistribution_inputs["layer_to_be_redistributed"]).spatialReference.name)
        for field in redistribution_inputs["fields_to_be_distributed"]:
            if not field_in_feature_class(field, redistribution_inputs["layer_to_be_redistributed"]):
                raise AttributeError('Error: %s does not exist in redistribution_inputs["layer_to_be_redistributed"]' % redistribution_inputs["fields_to_be_distributed"])
        if arcpy.env.workspace == "in_memory":
            logger.warning("WARNGING: this tool may not be compatible with an in_memory workspace")
        if redistribution_inputs["distribution_method"] in [1, 2, 3]:
            logger.debug("distribution method %s is valid" % redistribution_inputs["distribution_method"])
            if redistribution_inputs["distribution_method"] == 3:
                logger.warning("WARNGING: this distribution method only works if the layer to be redistributed it growth model results")
        else:
            raise AttributeError('distribution method must be either 1, 2 or 3. Specified value = %s' % redistribution_inputs["distribution_method"])
        if hasattr(__main__, 'testing'):
            testing = __main__.testing
            logger.debug("testing status from __main__ = %s" % testing)
        if hasattr(__main__, 'now'):
            now = __main__.now
            logger.debug("'now' from __main__ = %s" % now)
        else:
            now = r'%s' % datetime.now().strftime("%Y%m%d%H%M")
        logger.debug("For redistributePolygon tool, now (which is sometimes used in filenames) = %s" % now)
        logger.debug("For redistributePolygon tool, testing = %s" % testing)

        def calculate_field_proportion_based_on_area(field_to_calculate, total_area_field):
            """
            Calculates the field_to_calculate for each polygon based on its percentage of the total area of the polygon to calculate from.
            Arguments should be the names of the fields as strings
            """
            logger.debug("Executing calculate_field_proportion_based_on_area(%s, %s)" % (field_to_calculate, total_area_field))
            logger.debug("    Calculating %s field based on the proportion of the polygon area to the %s field" % (field_to_calculate, total_area_field))
            arcpy.CalculateField_management (intersecting_polygons, field_to_calculate, "return_area_proportion_of_total(!"+total_area_field+"!, !Shape_Area!, !" + field_to_calculate + "!)", "PYTHON_9.3", """def return_area_proportion_of_total(total_area_field, Shape_Area, field_to_calculate):
                    return Shape_Area/total_area_field * int(field_to_calculate)""") # a floating point integer seems to be getting returned. It seems that arcpy will round this value to an integer if it is storing it in an integer field.
        #
        def calculate_field_proportion_based_on_number_of_lots(field_to_calculate, larger_properties_field, local_number_of_properties_field, total_area_field):
            """
            Calculates the field_to_calculate for each polygon based on the number of lots in that polygon, compared to total number of lots on the larger polygon form which the data should be interpolated.
            Arguments should be the names of the fields as strings
            """
            logger.debug("Executing calculate_field_proportion_based_on_number_of_lots(%s, %s, %s, %s)" % (field_to_calculate, larger_properties_field, local_number_of_properties_field, total_area_field))
            logger.debug("    Calculating %s field based on the proportion of the total properties value in the %s field using %s" % (field_to_calculate, larger_properties_field, local_number_of_properties_field))
            arcpy.CalculateField_management (intersecting_polygons, field_to_calculate, "return_number_proportion_of_total(!"+larger_properties_field+"!, !"+local_number_of_properties_field+"!, !" + field_to_calculate + "!, !"+total_area_field+"!, !Shape_Area!)", "PYTHON_9.3", """def return_number_proportion_of_total(total_properties, local_properties, field_to_calculate, total_area_field, Shape_Area):
                if total_properties == None: # then total_properties = 0
                    new_value = int((float(Shape_Area)/float(total_area_field)) * int(field_to_calculate))
                    # print("new value = %s" % new_value)
                    # print("area = %s" % Shape_Area)
                else:
                    new_value = int((float(local_properties)/total_properties) * int(field_to_calculate))
                return new_value""")
        #
        def calculate_field_proportion_based_on_combination(field_to_calculate, larger_properties_field, local_number_of_properties_field, total_area_field):
            """
            Calculates the the field based on area, and by number of lots, and assigned the average between the two as the value.
            """
            logger.debug("Executing calculate_field_proportion_based_on_combination(%s, %s, %s, %s)" % (field_to_calculate, larger_properties_field, local_number_of_properties_field, total_area_field))
            logger.debug("    Calculating %s field as the average value between area and number of lots method" % field_to_calculate)
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
            logger.debug("Executing add_property_count_to_layer_x_with_name_x(%s, %s)" % (feature_class, field_name))
            properties = r"O:\\Data\\Planning_IP\\Spatial\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Cadastral\\sde_vector.TCC.Properties"
            feature_layer = "add_property_count_to_layer_x_with_name_x_feature_layer"
            delete_if_exists(feature_layer)
            logger.debug("    making feature layer from feature class %s" % feature_class)
            arcpy.MakeFeatureLayer_management(
                    feature_class, # in_features
                    feature_layer, # out_layer
                    "#", # where_clause
                    "#", # workspace
                    "#") # field_info
            if (field_in_feature_class("TARGET_FID", feature_layer)):
                logger.debug("    deleteing TARGET_FID field from feature_layer")
                arcpy.DeleteField_management(feature_layer, "TARGET_FID")
            properties_SpatialJoin = "properties_SpatialJoin"
            delete_if_exists(properties_SpatialJoin)
            stats = "stats"
            delete_if_exists(stats)
            logger.debug("    joining properties to "+ feature_layer +" and outputing to %s" % properties_SpatialJoin)
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
            logger.debug("    Calculating statistics table at stats")
            arcpy.Statistics_analysis(properties_SpatialJoin, stats, "Join_Count SUM","JOIN_FID")
            logger.debug("    joining back to %s" % feature_class)
            arcpy.JoinField_management (feature_class, "OBJECTID", stats, "JOIN_FID", "FREQUENCY")
            logger.debug("    renaming 'FREQUENCY' to '%s'" % field_name)
            arcpy.AlterField_management (feature_class, "FREQUENCY", field_name)
        #
        def create_intersecting_polygons():
            """
            Creates intersecting_polygons layer by intersecting desired_shape and source_data.
            """
            logger.debug("Executing create_intersecting_polygons")
            delete_if_exists(intersecting_polygons)
            logger.debug("    Computing the polygons that intersect both features")
            arcpy.Intersect_analysis ([desired_shape, source_data], intersecting_polygons, "ALL", "", "INPUT")
            logger.debug("    intersecting_polygons output: %s" % intersecting_polygons)
        #

        global local_number_of_properties_field
        local_number_of_properties_field = "local_counted_properties"
        global total_properties_field
        total_properties_field = "total_counted_properties"
        global intersecting_polygons
        intersecting_polygons = "intersecting_polygons"
        global intersecting_polygons_buffered
        intersecting_polygons_buffered = "intersecting_polygons_buffered"
        global desired_shape
        desired_shape = "desired_shape"
        delete_if_exists(desired_shape)
        global total_area_field
        total_area_field = "soure_total_area"
        global source_data
        source_data = "source_data"
        delete_if_exists(source_data)
        arcpy.CopyFeatures_management(redistribution_inputs["layer_to_be_redistributed"], source_data)
        arcpy.AddField_management(source_data, total_area_field, "FLOAT")
        arcpy.CalculateField_management(source_data, total_area_field, "!shape.area@squaremeters!", "PYTHON_9.3")

        add_property_count_to_layer_x_with_name_x(source_data, total_properties_field)

        arcpy.CopyFeatures_management(redistribution_inputs["layer_to_redistribute_to"], desired_shape)

        create_intersecting_polygons()

        add_property_count_to_layer_x_with_name_x(intersecting_polygons, local_number_of_properties_field)

        ## Recalculate groth model fields
        for GM_field in redistribution_inputs["fields_to_be_distributed"]:
            if field_in_feature_class(GM_field, intersecting_polygons):
                if redistribution_inputs["distribution_method"] == 1:
                    calculate_field_proportion_based_on_area(GM_field, total_area_field)
                elif redistribution_inputs["distribution_method"] == 2:
                    logger.debug("calculating %s field from total GMZ number of properties" % GM_field)
                    calculate_field_proportion_based_on_number_of_lots(GM_field, total_properties_field, local_number_of_properties_field, total_area_field)
                    # alternative is to return Peron and then calculate only where total = None here.
                elif redistribution_inputs["distribution_method"] == 3:
                    if GM_field in  ["POP_2016", "Tot_2016"]:
                        calculate_field_proportion_based_on_number_of_lots(GM_field, total_properties_field, local_number_of_properties_field, total_area_field)
                    elif GM_field in  ["POP_2036", "Tot_2036", "POP_2041", "Tot_2041", "POP_2046", "Tot_2046", "POP_2051", "Tot_2051", "POP_Full", "Tot_Full"]:
                        calculate_field_proportion_based_on_area(GM_field, total_area_field)
                    elif GM_field in  ["POP_2021", "Tot_2021", "POP_2026", "Tot_2026", "POP_2031", "Tot_2031"]:
                        calculate_field_proportion_based_on_combination(GM_field, total_properties_field, local_number_of_properties_field, total_area_field)
                    elif GM_field in  ["POP_2011", "Tot_2011"]:
                        arcpy.CalculateField_management (intersecting_polygons, GM_field, "returnNone()", "PYTHON_9.3", """def returnNone():
            return None""")


        ## Spatially Join intersecting_polygons back to redistribution layer
        fieldmappings = arcpy.FieldMappings()
        for field in arcpy.ListFields(redistribution_inputs["layer_to_redistribute_to"]):
            if field.name not in ['OBJECTID', 'Shape_Length', 'Shape_Area', 'Join_Count', 'Shape']:
                logger.debug("Adding fieldmap for %s" % field.name)
                fm = arcpy.FieldMap()
                fm.addInputField(redistribution_inputs["layer_to_redistribute_to"], field.name)
                renameFieldMap(fm, field.name)
                fieldmappings.addFieldMap(fm)
        for GM_field in redistribution_inputs["fields_to_be_distributed"]:
            if field_in_feature_class(GM_field, intersecting_polygons):
                fm_POP_or_Total = arcpy.FieldMap()
                fm_POP_or_Total.addInputField(intersecting_polygons, GM_field)
                renameFieldMap(fm_POP_or_Total, GM_field)
                fm_POP_or_Total.mergeRule = "Sum"
                fieldmappings.addFieldMap(fm_POP_or_Total)
        delete_if_exists(redistribution_inputs["output_filename"])
        logger.debug("joining intersecting_polygons back to redistribution layer")
        delete_if_exists(intersecting_polygons_buffered)
        arcpy.Buffer_analysis(
            in_features=intersecting_polygons,
            out_feature_class=intersecting_polygons_buffered,
            buffer_distance_or_field=-1)
        arcpy.SpatialJoin_analysis(
            target_features=desired_shape,
            join_features=intersecting_polygons_buffered,
            out_feature_class=redistribution_inputs["output_filename"],
            join_operation="JOIN_ONE_TO_ONE",
            join_type="KEEP_ALL",
            field_mapping=fieldmappings,
            match_option="Intersect")
        logger.info("Successfully redistributed %s to %s" % (source_data, desired_shape))
        logger.info("intersecting_polygons file can be found at %s\\%s" % (arcpy.env.workspace, intersecting_polygons))
        logger.info("Output file can be found at %s" % redistribution_inputs["output_filename"])
    except arcpy.ExecuteError:
        # print arcpy.GetMessages(2)
        logger.exception(arcpy.GetMessages(2))
    except Exception as e:
        # print e.args[0]
        logger.exception(e.args[0])
        raise e


def for_each_feature(feature_class, cb, where_clause=""):
    """
    Itterates over each feature in a feature class, and calls the cb function passing in a single feature layer containing the feature of the itteration.
    """
    # TODO: use `os.path.exists(feature_class)` here instead
    if "\\" not in feature_class:
        log("WARNING: looping likes to receive the feature_class as the full path to the file, not just the name. A backslash (\\) was not found in %s" % feature_class)
    feature_layer='feature_layer'
    logger.debug("Itterating over %s..." % feature_class)
    if field_in_feature_class("OBJECTID", feature_class):
        id_field = "OBJECTID"
    elif field_in_feature_class("FID", feature_class):
        id_field = "FID"
    else:
        raise AttributeError("%s does not contain an OBJECTID or FID" % feature_class)
    with arcpy.da.SearchCursor(feature_class, id_field, where_clause) as cursor:
        for row in bar(cursor):
            arcpy.MakeFeatureLayer_management(
                in_features=feature_class,
                out_layer=feature_layer,
                where_clause="%s = %s" % (id_field, row[0]))
            cb(feature_layer)
            arcpy.Delete_management(feature_layer)


def get_sum(field_name, feature_class):
    """Returns the sum of all the features in the field_name field of the feature_class"""
    count = 0
    with arcpy.da.SearchCursor(feature_class, field_name) as cursor:
        for row in cursor:
            if row[0] is not None:
                count += row[0]
    return count


def log(text):
    # print(text)
    logger.info(text)
    # TODO: if arcpy has attribute:
    #     arcpy.AddMessage(text)


def join_csv(in_data, in_field, csv, csv_field, included_fields="#"):
    """
    Converts a csv to a table, then joins it to another table.
    """
    for f in arcpy.ListFields(csv):
        if re.match('[0-9]', f.name[0:1]):
            logger.warning("Warning: some fields in %s start with digits. these will not be joined." % csv)
    logger.debug("in_data = %s" % in_data)
    logger.debug("in_field = %s" % in_field)
    logger.debug("csv = %s" % csv)
    logger.debug("csv_field = %s" % csv_field)
    if re.match('[0-9]', csv_field[0:1]):
        raise ValueError("the name of the csv field must not start with a digit.")
    logger.debug("included_fields = %s" % included_fields)
    logger.debug('%s in %s = %s' % (csv_field, csv, field_in_feature_class(csv_field, csv)))
    delete_if_exists(arcpy.env.workspace+"\\temp_table")
    log('creating temp_table...')
    arcpy.TableToTable_conversion(
        in_rows=csv,
        out_path=arcpy.env.workspace,
        out_name="temp_table")
    log('joining temp_table to %s...' % in_data)
    logger.debug('%s in %s = %s' % (csv_field, arcpy.env.workspace+"\\temp_table", field_in_feature_class(csv_field, arcpy.env.workspace+"\\temp_table")))
    logger.debug('fields in %s:' % arcpy.env.workspace+"\\temp_table")
    for f in arcpy.ListFields(arcpy.env.workspace+"\\temp_table"):
        logger.debug("  %s" % f.name)
    # arcpy.JoinField_management(
    #         in_data="mesh_blocks_feature_layer",
    #         in_field="MB_CODE16",
    #         join_table="temp_table",
    #         join_field="MB_CODE_2016",
    #         fields="MB_CATEGORY_NAME_2016;Dwelling;Person")
    arcpy.JoinField_management(
        in_data,
        in_field,
        join_table=arcpy.env.workspace+"\\temp_table",
        join_field=csv_field,
        fields=included_fields)
    arcpy.Delete_management(arcpy.env.workspace+"\\temp_table")
    log('%s joined to %s' % (csv, in_data))
