from __future__ import division
# --------------------------------
module_name = "jj_methods"
module_description = """
This module contains commonly used functions to help with analysis and mapping
in ArcGIS.  It is designed to be imported into other python scripts."""
# Author: Jared Johnston
# Created: 10/02/2017
# Copyright:   (c) TCC
# ArcGIS Version:   10.5.1
# Python Version:   2.7
module_version = "01.02.20180509"
# Template Source: https://blogs.esri.com/esri/arcgis/2011/08/04/pythontemplate/
# --------------------------------
import os


def main():
    print("")
    print("name: %s" % module_name)
    print("version: %s" % module_version)
    print("description: \n%s\n" % module_description)


if __name__ == '__main__':
    main()
    exit()

import sys # noqa
import arcpy
import re
import logging
import __main__
from datetime import datetime
try:
    import progressbar
    bar = progressbar.ProgressBar()
except ImportError as e:  # ie, when progressbar is not installed (this is untested)
    def bar(itterable):
        return itterable

# see here for logging best practices: https://stackoverflow.com/questions/15727420/using-python-logging-in-multiple-modules

logger = logging.getLogger(__name__)
testing = True

if arcpy.env.scratchWorkspace is None:
    arcpy.env.scratchWorkspace = r'C:\TempArcGIS\scratchworkspace.gdb'

if arcpy.env.workspace is None:
    arcpy.env.workspace = r'C:\TempArcGIS\scratchworkspace.gdb'

if not arcpy.Exists(arcpy.env.scratchWorkspace):
    raise ExecuteError("ERROR: %s does not exist. You must create this database, or set one that already exists." % arcpy.env.scratchWorkspace)

if not arcpy.Exists(arcpy.env.workspace):
    raise ExecuteError("ERROR: %s does not exist. You must create this database, or set one that already exists." % arcpy.env.workspace)


def get_identifying_field(layer):
    if field_in_feature_class("OBJECTID", layer):
        return "OBJECTID"
    elif field_in_feature_class("FID", layer):
        return "FID"
    else:
        raise AttributeError("%s does not contain an OBJECTID or FID" % layer)


def create_polygon(output, *shapes_lists):
    """
    Creates a polygon at the output from the list of points provided. Multiple points list can be provided.
    """
    if os.sep not in output:
        output = arcpy.env.workspace + "\\" + output
    delete_if_exists(output)
    logger.debug("directory = " + get_directory_from_path(output))
    logger.debug("name = " + get_file_from_path(output))
    output = arcpy.CreateFeatureclass_management(
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
    array = [(left_x, lower_y),
             (left_x, upper_y),
             (right_x, upper_y),
             (right_x, lower_y),
             (left_x, lower_y)]
    if os.sep not in output:
        output=arcpy.env.workspace+"\\"+output
    delete_if_exists(output)
    create_polygon(output, array)
    return output


def create_point(x_coord=479585, y_coord=7871450, output="basic_point"):
    """
    Creates a features class with a single point with the co-ordinates as passed in.

    Arguments:
        x_coord - the x_coordinate of the point (479585 by default)
        y_coord - the y_coordinate of the point (7871450 by default)
        output - the location to save the output
    """
    if os.sep not in output:
        output = arcpy.env.workspace + "\\" + output
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

    The coords_list must be an itterable, where each item is another itterable
    with an x and y coordinate.
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
    else:
        logger.debug("Layer doesn't exist: %s" % layer)
    # For some reason, if a script is running in ArcMap, this function needs to be executed twice.
    if arcpy.Exists(layer):
        logger.debug("Deleting %s" % layer)
        arcpy.Delete_management(layer)
        # logger.debug("%s exists = %s" % (layer, arcpy.Exists(layer)))
    else:
        logger.debug("Layer doesn't exist: %s" % layer)


def is_polygon(layer):
    """
    If layer is a polygon, returns True, otherwise returns false.
    """
    # Why does this work when add_external_area_field doesn't?
    logger.debug("arcpy.Exists(layer) = %s" % arcpy.Exists(layer))
    logger.debug("layer = %s" % layer)
    # layer = "%s" % layer # TODO: Why is this necessary? What's going on here? arcpy.Describe is complaining about data sometimes, and I can't consistantly reproduce the error. in ArcGIS Pro, there is a arcpy.da.Describe function. I assume this was created for good reason and that using it will solve this problem in the future.
    desc = arcpy.Describe(layer)
    if desc.shapeType == "Polygon":
        return True
    else:
        return False

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


def check_field_in_fc(field, fc):
    "raises an error if the field does not exist in the feature class"
    if not field_in_feature_class(field, fc):
        raise AttributeError('Error: %s does not exist in %s' % (field, fc))


def spatial_references_differ(layer_one, layer_two):
    "Checks the spatial references of the layer_to_redistribute_to" + \
    " and the layer_to_be_redistributed of the input dictionary."
    if arcpy.Describe(layer_one).spatialReference.name != arcpy.Describe(layer_two).spatialReference.name:
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


def calculate_external_field(target_layer, target_field, join_layer, join_field, output, **spatial_join_attributes):
    """Calculates a target field from a field on another featre based on
    spatial join. If output is None, target_layer field will be calculated
    in place.

    WARNING: Using output == None with a temporary workspace risks deleting the
    target_layer. Use with caution."""
    if arcpy.Describe(join_layer).shapeType != "Polygon":
        raise AttributeError("This tool currently only works when the join_layer is a polgyon.")
    if "distance_field_name" in spatial_join_attributes.keys():
        raise AttributeError("This tool only adds the join_field. A distance field will not be added from the spatial join.")
    tmp_field_name = "delete_me"
    join_layer_copy = "join_layer_copy"
    delete_if_exists(join_layer_copy)
    target_layer_copy = "target_layer_copy"
    delete_if_exists(target_layer_copy)
    logger.debug("Making copy of %s" % join_layer)
    arcpy.CopyFeatures_management(join_layer, join_layer_copy)
    logger.debug("Making copy of %s" % target_layer)
    arcpy.CopyFeatures_management(target_layer, target_layer_copy)
    if output:
        delete_if_exists(output)
    original_fields = arcpy.ListFields(target_layer_copy)
    original_field_names = [f.name for f in original_fields]

    def tmp_field_exists_in_join_layer():
        if tmp_field_name in [f.name for f in arcpy.ListFields(join_layer_copy)]:
            return True
        else:
            return False

    if tmp_field_exists_in_join_layer():
        raise AttributeError("Error: cannot perform this operation on a field named 'delete_me'")

    try:
        join_field_object = arcpy.ListFields(join_layer, join_field)[0]
    except IndexError as e:
        raise IndexError("could not find %s in %s" % (join_field, join_layer))
    if len(arcpy.ListFields(join_layer, join_field)) > 1:
        raise AttributeError("Multiple fields found when searching for the %s in %s" % (join_field, join_layer))

    logger.debug("Calculating %s.%s from %s.%s" % (target_layer_copy, target_field, join_layer, join_field))

    logger.debug("  Adding and calculating %s = %s" % (tmp_field_name, join_field))
    arcpy.AddField_management(join_layer_copy, tmp_field_name, join_field_object.type)
    arcpy.CalculateField_management(join_layer_copy, tmp_field_name, "!" + join_field + "!", "PYTHON", "")

    logger.debug("  Spatially joining %s to %s" % (join_layer, target_layer_copy))
    join_layer_buffered = "join_layer_buffered"
    # TODO: skip the buffer step if the join_layer is a point or a line type feature class
    delete_if_exists(join_layer_buffered)
    join_layer_buffered = arcpy.Buffer_analysis(
        in_features=join_layer_copy,
        out_feature_class=join_layer_buffered,
        buffer_distance_or_field=-0.5)
    if output == None:
        output = str(target_layer)
        delete_if_exists(output)
    try:
        output = arcpy.SpatialJoin_analysis(target_layer_copy, join_layer_buffered, output, **spatial_join_attributes)
    except TypeError as e:
        log("Error: probably some invalid keword argument was passed in. calculate_external_field passes all optional keyword argument on to SpatialJoin_analysis.")
        if not arcpy.Exists(output):
            log("Copying target_layer_copy back to target_layer...")
            arcpy.CopyFeatures_management(target_layer_copy, target_layer)
        raise e
    except Exception as e:
        log("SpatialJoin_analysis failed.")
        if not arcpy.Exists(output):
            log("Copying target_layer_copy back to target_layer...")
            arcpy.CopyFeatures_management(target_layer_copy, target_layer)
        raise e
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
    logging.info("Create %s" % output)
    return output


def add_external_area_field(
        in_features=None,
        new_field_name="external_area",
        layer_with_area_to_grab=None,
        dissolve=True):
    """
    Adds a new field and give it the value of the area that intersects with
    another feature class.

    Params
    ------

    first: in_features
        The layer that will have the new field added
    second: new_field_name (defulat = "external_area")
        The name of the new field that will contain the area
    third: layer_with_area_to_grab
        The layer that will be intersected to obtain the area
    fourth: dissolve (default = True)
        If true, the layer_with_area_to_grab will be intersected, and then
        dissolved before being intersected again. This ensures that there is
        only 1 feature per in_feature.

    Returns a copy of the original in_features with the new field added.
    """
    logger.debug("Executing add_external_area_field...")
    logger.debug("in_features = %s" % in_features)
    logger.debug("layer_with_area_to_grab = %s" % layer_with_area_to_grab)
    logger.debug("type(in_features) = %s" % type(in_features))
    logger.debug("type(layer_with_area_to_grab) = %s" % type(layer_with_area_to_grab))
    in_features_is_polygon = is_polygon(in_features)
    layer_with_area_to_grab_is_polygon = is_polygon(layer_with_area_to_grab)
    logger.debug("is_polygon(in_features) = %s" % in_features_is_polygon)
    logger.debug("is_polygon(layer_with_area_to_grab) = %s" % layer_with_area_to_grab_is_polygon)
    if in_features is None or layer_with_area_to_grab is None:
        raise AttributeError("Error: add_external_area_field function must take both in_features and layer_with_area_to_grab feature classes as arguments.")
    elif not (arcpy.Exists(in_features) and arcpy.Exists(layer_with_area_to_grab)):
        logger.debug("arcpy.Exists(in_features) = %s" %
            arcpy.Exists(in_features))
        logger.debug("arcpy.Exists(layer_with_area_to_grab) = %s" %
            arcpy.Exists(layer_with_area_to_grab))
        raise AttributeError("Error: both in_features and layer_with_area_to_grab feature classes must exist.")
    elif not (in_features_is_polygon and layer_with_area_to_grab_is_polygon):
    # elif not is_polygon(layer_with_area_to_grab):
        raise AttributeError("Error: both in_features and layer_with_area_to_grab feature classes must be polygons.")
    else:
        logger.debug("Input features classes passed to add_external_area_field are OK.")
        # print("")

    in_copy = "add_external_area_in_features_copy"
    delete_if_exists(in_copy)
    # delete_if_exists(in_copy) # why do I need to do this twice? What is goin on here?
    in_copy = arcpy.Copy_management(
        in_data = in_features,
        out_data=in_copy)
    if dissolve:
        if field_in_feature_class("FID_%s" % get_file_from_path(in_copy), in_copy):
            raise AttributeError("Error: FID_%s already exists in %s" % (get_file_from_path(in_copy, in_copy)))
        delete_if_exists("preliminary_intersect")
        preliminary_intersect = arcpy.Intersect_analysis(
            in_features = [in_copy, layer_with_area_to_grab],
            out_feature_class = "preliminary_intersect",
            join_attributes="ONLY_FID")
        logging.debug("Preliminary dissolve found at %s\\preliminary_intersect" % arcpy.env.workspace)
        delete_if_exists("layer_with_area_to_grab_dissolved")
        layer_with_area_to_grab = arcpy.Dissolve_management(
            in_features=preliminary_intersect,
            out_feature_class="layer_with_area_to_grab_dissolved",
            dissolve_field = "FID_%s" % get_file_from_path(in_copy))
    in_copy = arcpy.AddField_management(in_copy, new_field_name, "FLOAT")
    intersecting_with_external = "intersecting_with_external"
    delete_if_exists(intersecting_with_external)
    intersecting_with_external = arcpy.Intersect_analysis(
        in_features = [in_copy, layer_with_area_to_grab],
        out_feature_class = intersecting_with_external)
    # TODO: What do I do if there are no intersecting areas? There will be an empty feature class
    in_copy_with_new_field = calculate_external_field(
        target_layer = in_copy,
        target_field = new_field_name,
        join_layer = intersecting_with_external,
        join_field = "Shape_Area",
        output = "%s_with_new_field" % get_file_from_path(in_features))
        # output = in_features) # TODO: change back FIXME
    arcpy.CalculateField_management(
        in_copy_with_new_field,
        new_field_name,
        "return_zero_where_None(!" + \
            new_field_name  + "!)",
        "PYTHON_9.3",
        """def return_zero_where_None(value):
               if value is None:
                   return 0
               else:
                   return value""")
    return in_copy_with_new_field

def renameFieldMap(fieldMap, name_text):
    """
    Sets the output fieldname of a FieldMap object. Used when creating FieldMappings.
    """
    type_name = fieldMap.outputField
    type_name.name = name_text
    fieldMap.outputField = type_name


def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})


def get_file_from_path(path):
    """Returns the filename from a provided path."""
    path = str(path)
    head, tail = os.path.split(path)
    return tail or os.path.basename(head)
    # return tail


def get_directory_from_path(path):
    """Returns the directory from a provided path."""
    # Does this need the abspath part? With it there, if I put in a plain
    # string, the current working directory will be returned.
    # return os.path.dirname(os.path.abspath(path))
    path = str(path)
    # logging.debug("in get_directory_from_path, path = %s" % path)
    if os.path.dirname(path):
        return os.path.dirname(path)
    else:
        raise AttributeError("get_directory_from_path received a string with no path (%s). What should be the default behaviour here? return arcpy.env.workspace or return the current working directory from os.path.abspath()?" % path)


def test_print():
    """tests that methods in this module can be called."""
    logger.info("success")
    logger.debug("fail")


def print_table(table):
    f_list = []
    for field in [field.name for field in arcpy.ListFields(table)]:
        f_list.append(field)
    print(f_list)
    with arcpy.da.SearchCursor(table, "*") as cursor:
        for row in cursor:
            print(row)


def add_layer_count(in_features, count_features, new_field_name, output=None, by_area=False):
    """
    Creates a new field in in_features called new_field_name, then populates it
    with the number of count_features that fall inside it.

    Params
    ------

    first: in_features
        The layer that will have the count added to it
    second: count_features
        The features that will be counted
    third: new_field_name
        The name of the new field that will contain the count
    fourth: output (optional)
        The output location to save the new layer. If not provided, the
        original layer will be modified (I think this might only be the case
        where by_area=False)
    fifth: by_area (optional)
        A boolean. If True, the count_features will be counted by the area that
        falls within the in_features. If False (default), the count_features
        will be counted by the number of centroids that fall inside the
        in_features.

    Returns a new layer with the new_field_name added.
    """

    logger.debug("Executing add_layer_count(%s, %s, %s, %s, %s)" % (in_features, count_features, new_field_name, output, by_area))
    if field_in_feature_class(new_field_name, in_features):
        raise AttributeError("ERROR: Cannot add field. Field %s already exists in %s" % (new_field_name, in_features))

    def get_original_id_name(in_features):
        name = "original_id"
        appendix = 2
        while field_in_feature_class(name, in_features):
            name = "original_id_%s" % appendix
            appendix += 1
        return name

    def get_count_field_name(count_features):
        """creates a uniqe name for a field to add to the count_features."""
        name = "count_field"
        appendix = 2
        while field_in_feature_class(name, count_features):
            name = "count_field_%s" % appendix
            appendix += 1
        return name

    def add_layer_count_by_area(in_features, count_features, new_field_name, output=None):
        """Creates a new field in in_features called new_field_name, then populates it with the number of count_features that fall inside it."""

        if not output:
            # Do I need to add functionality to modify the in_features? This is the way add_layer_count_by_centroid is setup.
            output="add_layer_count_result"

        id_field = get_identifying_field(in_features)
        count_field = get_count_field_name(count_features)
        original_id_field = get_original_id_name(in_features)

        # Make temporary layers so that the source files are not changed
        in_features_copy = "%s\\in_features_copy" % arcpy.env.scratchWorkspace
        delete_if_exists(in_features_copy)
        in_features_copy = arcpy.CopyFeatures_management(
            in_features,
            in_features_copy)
        logger.debug("in_features_copy = %s" % in_features_copy)
        count_features_copy = "%s\\count_features_copy" % arcpy.env.scratchWorkspace
        delete_if_exists(count_features_copy)
        count_features_copy = arcpy.CopyFeatures_management(
            count_features,
            count_features_copy)
        logger.debug("count_features_copy = %s" % count_features_copy)

        delete_if_exists(output)

        # This added field is a reference that will be used to join back to the
        # in_features_copy later
        if field_in_feature_class(original_id_field, in_features_copy):
            logging.debug("WARNING: %s field already exists. %s contains the following fields: " % (original_id_field, in_features_copy))
            logging.debug("  %s" % [f.name for f in arcpy.ListFields(in_features_copy)])
        arcpy.AddField_management(in_features_copy, original_id_field, "LONG")
        arcpy.CalculateField_management(in_features_copy, original_id_field, "!%s!" % id_field, "PYTHON_9.3")

        if field_in_feature_class(count_field, count_features_copy):
            logging.debug("WARNING: %s field already exists. %s contains the following fields: " % (count_field, count_features_copy))
            logging.debug("  %s" % [f.name for f in arcpy.ListFields(count_features_copy)])
        # Adding the new field (of type FLOAT so fractions can be counted)
        arcpy.AddField_management(count_features_copy, count_field, "FLOAT")
        # Giving everyhting a value of 1, which will be used to count
        arcpy.CalculateField_management(count_features_copy, count_field, "1", "PYTHON_9.3")

        # Generate a table counting the count_features_copy
        count_table = "%s\\add_layer_count_table" % arcpy.env.scratchWorkspace
        delete_if_exists(count_table)
        count_table = arcpy.TabulateIntersection_analysis(
            in_zone_features = in_features_copy,
            zone_fields = original_id_field,
            in_class_features = count_features_copy,
            out_table = count_table,
            sum_fields = count_field)

        # Deletes old field values
        # arcpy.DeleteField_management(in_features_copy, new_field_name) # TODO: Is this required?

        # Rejoin back to input_features
        in_features_joined = arcpy.JoinField_management(
            in_data = in_features_copy,
            in_field = id_field,
            join_table = count_table,
            join_field = original_id_field,
            fields = count_field)

        # TODO: rename field to new_field_name
        arcpy.AlterField_management(
                in_table = in_features_joined,
                field = count_field,
                new_field_name = new_field_name)
                # {new_field_alias},
                # {field_type},
                # {field_length},
                # {field_is_nullable},
                # {clear_field_alias})

        output = arcpy.CopyFeatures_management(
            in_features_joined,
            output)

        return output


    def add_layer_count_by_centroid(in_features, count_features, new_field_name, output=None):
        """
        Creates a new field in in_features called new_field_name, then populates
        it with the number of count_features' centroids that fall inside it. If
        output is provided, it creates a new layer as the output, otherwise, it
        appends the layer count to in_features.
        """
        # in_features_copied = False

        if output:
            logger.debug("    Copying in_features to output (%s) so that the original is not modified" % output)
            delete_if_exists(output)
            # Copy_management will perserve OBJECTID field, which is key to the
            # stats table being joined back the output
            output = arcpy.Copy_management(
                in_data = in_features,
                out_data = output)
            # in_features_copied = True
        else:
            output=in_features

        def clean_in_features():
            all_input_fields = [f.name for f in arcpy.ListFields(in_features)] + [f.name for f in arcpy.ListFields(count_features)]
            invalid_fields = ["FREQUENCY", "Join_Count", "TARGET_FID", "JOIN_FID"]
            invalid_fields_in_inputs = list(set(all_input_fields).intersection(invalid_fields))
            if invalid_fields_in_inputs:
                logging.debug("The following fields exist in either %s or %s: %s" % (in_features, count_features, invalid_fields_in_inputs))
                in_features_cleaned = "in_features_cleaned"
                delete_if_exists(in_features_cleaned)
                logger.debug("    making a copy of in_features so that invalid fields can be deleted" % in_features)
                # Copy_management will perserve OBJECTID field, which is key to
                # the stats table being joined back the output
                in_features_cleaned = arcpy.Copy_management(
                    in_data = in_features,
                    out_data = in_features_cleaned)
                # in_features_copied = True

                for field in invalid_fields_in_inputs:
                    logger.debug("    deleteing %s field from in_features_cleaned" % field)
                    arcpy.DeleteField_management(in_features_cleaned, field)
                return in_features_cleaned
            else:
                return in_features

        in_features_cleaned = clean_in_features()
        logging.debug("in_features_cleaned can be found at %s" % in_features_cleaned)

        # multiple deletes needed if running from in ArcMap. Why??
        count_features_joined = "count_features_joined"
        delete_if_exists(count_features_joined)
        delete_if_exists(count_features_joined)
        delete_if_exists(count_features_joined)
        stats = "stats"
        delete_if_exists(stats)
        delete_if_exists(stats)
        delete_if_exists(stats)
        logger.debug("    joining count_features to %s and outputing to %s" % (in_features_cleaned, count_features_joined))
        count_features_joined = arcpy.SpatialJoin_analysis(
            target_features = count_features,
            join_features = in_features_cleaned,
            out_feature_class = count_features_joined,
            join_operation = "JOIN_ONE_TO_MANY",
            join_type = "KEEP_COMMON",
            field_mapping = "#",
            match_option = "HAVE_THEIR_CENTER_IN",
            search_radius = "#",
            distance_field_name = "#")
        logger.debug("    Calculating statistics table at %s" % stats)
        arcpy.Statistics_analysis(
            in_table = count_features_joined,
            out_table = stats,
            statistics_fields = "Join_Count SUM",
            # the JOIN_FID field added by spatial join if JOIN_ONE_TO_MANY is
            # selected. I think it corresponds with the OBJECTID of the
            # join_feature used in Spatial Join
            case_field = "JOIN_FID")
        logger.debug("    joining back to %s" % output)
        arcpy.JoinField_management(
            in_data = output,
            in_field = "OBJECTID", # FIXME: this only works if the in_features are modified in place (ie, if no output is provided)
            join_table = stats,
            join_field = "JOIN_FID",
            fields = "FREQUENCY")
        logger.debug("    renaming 'FREQUENCY' to '%s'" % new_field_name)
        arcpy.AlterField_management(
            output,
            "FREQUENCY",
            new_field_name)
        return output

    if by_area is True:
        # TODO: check that count_features is a polygon
        if not is_polygon(count_features) or not is_polygon(in_features):
            raise AttributeError("if by_area is True, both in_features and count_features must be polygons")
        return add_layer_count_by_area(in_features, count_features, new_field_name, output)
    else:
        return add_layer_count_by_centroid(in_features, count_features, new_field_name, output)


def redistributePolygon(redistribution_inputs):
    """
    This function redistributes the data in one feature class to another
    feature class.

    Params
    ------

    It take a dictionary called 'redistribution_inputs' as an argument, which
    contains the following keys:
    - layer_to_redistribute_to
    - layer_to_be_redistributed
    - output_filename
    - distribution_method
    - fields_to_be_distributed
    - properties_layer

    distribution_method: an integer given below;
                          1. distributes by proportion of area;
                          2. distributes by number of lots;
                          3. distributes by a combination of methods 1 and 2
                             above (this is a special use case);
                         or a string containing the path to the
                         distribution feature class. If provided the fields
                         will be distributed by the proportion of the area of
                         this features class that falls within each polygon. If
                         none exists for a particular area, properties will be
                         used as the distribution method. If no properties
                         exist for a particular area, the area method will be
                         used.

    fields_to_be_distributed: a list of the field names which should be
                              distributed.

    properties_layer: the layer which contains the property / land parcel
                      boundaries. This will be used whenever the distribution
                      by number of lots is called. If not provided, the
                      sde_vector.TCC.Land_Parcels will be used.

    Returns
    -------
    No value returned.
    """

    # TODO:
    # In the future, the distribution method should be provided as a list. For
    # example, you might want to first distribute by Net Developable Area (by
    # area), then by properties (by centroid), then by area.

    local_number_of_properties_field = "intersected_total_properties"
    total_properties_field = "source_total_properties"
    total_intersecting_area = "total_intersecting_area"
    local_intersecting_area = "local_intersecting_area"
    intersecting_polygons = "intersecting_polygons"
    intersecting_polygons_buffered = "intersecting_polygons_buffered"
    desired_shape = "desired_shape"
    delete_if_exists(desired_shape)
    delete_if_exists(desired_shape)
    total_area_field = "source_total_area"
    source_data = "source_data"
    delete_if_exists(source_data)
    delete_if_exists(source_data)
    if "properties_layer" in redistribution_inputs.keys():
        land_parcels = redistribution_inputs["properties_layer"]
        logger.debug("For this analysis, %s will be used as the properties layer" % land_parcels)
    else:
        land_parcels = r'Database Connections\WindowAuth@gisdbcore01@sde_vector.sde' +\
                       r'\sde_vector.TCC.Cadastral\sde_vector.TCC.Land_Parcels'
        # land_parcels = r'C:\TempArcGIS\testing.gdb\testing_properties'
        logger.debug("For this analysis, %s will be used as the properties layer" % land_parcels)

    def log_inputs():
        logging.debug("redistribution_inputs:")
        for key in redistribution_inputs:
            logging.debug("  %s = %s" % (key, redistribution_inputs[key]))

    def perform_checks():
        if spatial_references_differ(
                redistribution_inputs["layer_to_redistribute_to"],
                redistribution_inputs["layer_to_be_redistributed"]):
            logger.warning("spatial references differ")
            logger.warning("layer_to_redistribute_to = %s" % redistribution_inputs["layer_to_redistribute_to"])
            logger.warning("layer_to_be_redistributed = %s" % redistribution_inputs["layer_to_be_redistributed"])
            logger.warning(
                "WARNING: %s and %s do not have the same coordinate system."  % (
                    redistribution_inputs["layer_to_redistribute_to"],
                    redistribution_inputs["layer_to_be_redistributed"]) +
                " The area fields may not calculate with the same " +
                "coordinates. According to " +
                "http://pro.arcgis.com/en/pro-app/tool-reference/data-management/calculate-field.htm," +
                " 'Using areal units on geographic data will yield" +
                " questionable results as decimal degrees are not consistent" +
                " across the globe.'\rThe best approach is to use the " +
                "Project (Data Management) tool to reproject the data into " +
                "MGA Zone 55 and try again.")
            logger.warning("  layer_to_redistribute_to: %s" %
                arcpy.Describe(
                    redistribution_inputs["layer_to_redistribute_to"]
                ).spatialReference.name)
            logger.warning("  layer_to_be_redistributed: %s" %
                arcpy.Describe(
                    redistribution_inputs["layer_to_be_redistributed"]
                ).spatialReference.name)
        for field in redistribution_inputs["fields_to_be_distributed"]:
            check_field_in_fc(field, redistribution_inputs["layer_to_be_redistributed"])
        if arcpy.env.workspace == "in_memory":
            logger.warning("WARNGING: this tool may not be compatible with" + \
            "an in_memory workspace")
        if redistribution_inputs["distribution_method"] in [1, 2, 3]:
            logger.debug("distribution method %s is valid" %
                redistribution_inputs["distribution_method"])
            if redistribution_inputs["distribution_method"] == 3:
                logger.warning("WARNGING: this distribution method only" + \
                "works if the layer to be redistributed is growth model results")
        elif arcpy.Exists(redistribution_inputs["distribution_method"]) and \
                is_polygon(redistribution_inputs["distribution_method"]):
                    logger.debug("distribution method is valid feature class: %s" %
                        redistribution_inputs["distribution_method"])
        else:
            raise AttributeError('distribution method must be either 1, 2, 3, or the path to a feature class. Specified value = %s' % redistribution_inputs["distribution_method"])

    def get_testing_and_now():
        if hasattr(__main__, 'testing'):
            testing = __main__.testing
            logger.debug("testing status from __main__ = %s" % testing)
        else:
            testing = False
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
                return Shape_Area/total_area_field * field_to_calculate""") # a floating point integer seems to be getting returned. It seems that arcpy will round this value to an integer if it is storing it in an integer field.

    def calculate_field_proportion_based_on_number_of_lots(field_to_calculate, larger_properties_field, local_number_of_properties_field, total_area_field):
        """
        Calculates the field_to_calculate for each polygon based on the number of lots in that polygon, compared to total number of lots on the larger polygon form which the data should be interpolated.
        Arguments should be the names of the fields as strings
        """
        logger.debug("Executing calculate_field_proportion_based_on_number_of_lots(%s, %s, %s, %s)" % (
            field_to_calculate,
            larger_properties_field,
            local_number_of_properties_field,
            total_area_field))
        logger.debug("    Calculating %s field based on the proportion of the total properties value in the %s field using %s" % (field_to_calculate, larger_properties_field, local_number_of_properties_field))
        arcpy.CalculateField_management(
            intersecting_polygons,
            field_to_calculate,
            "return_number_proportion_of_total(!" + \
                larger_properties_field + "!, !" + \
                local_number_of_properties_field + "!, !"  + \
                field_to_calculate  + "!, !" + \
                # total_area_field + "!)",
                total_area_field + "!, !" + \
                "shape.area@squaremeters" + "!)",
            "PYTHON_9.3",
            """def return_number_proportion_of_total(
                       total_properties,
                       local_properties,
                       field_to_calculate,
                       total_area_field,
                       Shape_Area):
                   if total_properties == None: # then total_properties = 0
                       new_value = int((float(Shape_Area)/float(total_area_field)) * int(field_to_calculate))
                       # print("new value = %s" % new_value)
                       # print("area = %s" % Shape_Area)
                   else:
                       new_value = int((float(local_properties)/total_properties) * int(field_to_calculate))
                   return new_value""")

    def calculate_field_proportion_based_on_combination(field_to_calculate, larger_properties_field, local_number_of_properties_field, total_area_field):
        """
        Calculates the the field based on area, and by number of lots, and assigned the average between the two as the value.
        """
        logger.debug("Executing calculate_field_proportion_based_on_combination(%s, %s, %s, %s)" % (field_to_calculate, larger_properties_field, local_number_of_properties_field, total_area_field))
        logger.debug("    Calculating %s field as the average value between area and number of lots method" % field_to_calculate)
        arcpy.CalculateField_management(
        intersecting_polygons,
        field_to_calculate,
        "return_average_value(!" + \
            larger_properties_field + "!, !" + \
            local_number_of_properties_field + "!, !" + \
            field_to_calculate + "!, !" + \
            total_area_field + "!, !" + \
            # "Shape_Area" + "!)",
            "shape.area@squaremeters" + "!)",
        "PYTHON_9.3",
        """def return_number_proportion_of_total(total_properties, local_properties, field_to_calculate):
                new_value =  (float(local_properties)/total_properties) * int(field_to_calculate)
                return int(new_value)
            def return_area_proportion_of_total(GMZ_total_area, Shape_Area, field_to_calculate):
                return Shape_Area/GMZ_total_area * int(field_to_calculate)
            def return_average_value(total_properties, local_properties, field_to_calculate, GMZ_total_area, Shape_Area):
                properties = return_number_proportion_of_total(total_properties, local_properties, field_to_calculate)
                area = return_area_proportion_of_total(GMZ_total_area, Shape_Area, field_to_calculate)
                average = (area + properties) / 2
                return average""")

    def calculate_field_portion_of_external_area(
            field_to_calculate,
            total_external_area_field,
            local_external_area_field,
            total_properties_field,
            local_properties_field,
            total_area_field):
        """TODO"""
        logger.debug("Executing calculate_field_portion_of_external_area(\n\t\t%s, \n\t\t%s, \n\t\t%s, \n\t\t%s, \n\t\t%s, \n\t\t%s)..." % (
            field_to_calculate,
            total_external_area_field,
            local_external_area_field,
            total_properties_field,
            local_properties_field,
            total_area_field))
        logger.debug("    Calculating %s field based on the proportion of the intersecting external area that falls within" % field_to_calculate)
        arcpy.CalculateField_management(
            intersecting_polygons,
            field_to_calculate,
            "return_external_area_proportion_of_total(!" + \
                total_external_area_field + "!, !" + \
                local_external_area_field + "!, !"  + \
                total_properties_field + "!, !" + \
                local_properties_field + "!, !"  + \
                field_to_calculate  + "!, !" + \
                total_area_field + "!, " + \
                "!Shape_Area!)",
            "PYTHON_9.3",
            """def return_external_area_proportion_of_total(
                       total_external_area,
                       local_external_area,
                       total_properties,
                       local_properties,
                       field_to_calculate,
                       total_area_field,
                       Shape_Area):
                   if total_external_area == 0:
                       # print("no external area, calculating by properties...")
                       if total_properties == None:
                           new_value = Shape_Area/total_area_field * field_to_calculate
                       else:
                           new_value = (float(local_properties)/total_properties) * field_to_calculate
                   else:
                       new_value = (float(local_external_area)/total_external_area) * field_to_calculate
                   return new_value""")

    # TODO: create a function to replace the calculate functions above. It
    # accepts a list of tuples (each tuple containig a total and a local value
    # field). The function will take each tuple and calculate the field base on
    # the portion of the values in each of the tuple field. If it finds any
    # polygon where the total value is 0, it will move to the next tuple and do
    # the same. This would be much more reusable.


    def add_area_field(layer, field_name):
        arcpy.AddField_management(layer, field_name, "FLOAT")
        arcpy.CalculateField_management(
            layer,
            field_name,
            "!shape.area@squaremeters!",
            "PYTHON_9.3")

    def intersect(*input_layers):
        logger.debug("Intersecting %s" % str(input_layers))
        delete_if_exists(intersecting_polygons)
        logger.debug("    Computing the polygons that intersect both features")
        arcpy.Intersect_analysis(
            in_features=list(input_layers),
            out_feature_class=intersecting_polygons,
            join_attributes="ALL",
            cluster_tolerance="",
            output_type="INPUT")
        logger.debug("    intersecting_polygons output: %s" % intersecting_polygons)
        return intersecting_polygons


    def create_intersecting_polygons():
        """
        Creates intersecting_polygons layer by intersecting desired_shape and source_data.
        """
        logger.debug("Executing create_intersecting_polygons")
        delete_if_exists(intersecting_polygons)
        logger.debug("    Computing the polygons that intersect both features")
        arcpy.Intersect_analysis(
            in_features=[desired_shape, source_data],
            out_feature_class=intersecting_polygons,
            join_attributes="ALL",
            cluster_tolerance="",
            output_type="INPUT")
        logger.debug("    intersecting_polygons output: %s" % intersecting_polygons)


    def create_temp_copies_of_inputs():
        logger.debug("Creating temporary copies of input layer...")
        arcpy.CopyFeatures_management(
            redistribution_inputs["layer_to_be_redistributed"],
            source_data)
        arcpy.CopyFeatures_management(
            redistribution_inputs["layer_to_redistribute_to"],
            desired_shape)


    log_inputs()
    perform_checks()
    get_testing_and_now()

    create_temp_copies_of_inputs()

    add_area_field(source_data, total_area_field)

    # I may be able to improve efficiency if I dissolve the distribute_method
    # (if applicable) layer here, so that i don't have to do it twice below.

    if redistribution_inputs["distribution_method"] in (2, 3):
        logger.debug("Adding %s to %s" % (total_properties_field, source_data))
        # Adding total properties to source_data
        source_data = add_layer_count(
            new_field_name = total_properties_field,
            in_features = source_data,
            count_features = land_parcels)
            # output = "%s\\source_data" % arcpy.env.workspace)
    elif arcpy.Exists(redistribution_inputs["distribution_method"]):
        logger.debug("Adding %s to %s" % (total_properties_field, source_data))
        # Adding total properties to source_data
        source_data = add_layer_count(
            new_field_name = total_properties_field,
            in_features = source_data,
            count_features = land_parcels)
            # output = "%s\\source_data" % arcpy.env.workspace)
        logger.debug("Adding %s field to %s" % (total_intersecting_area, source_data))
        # Adding total intersecting area to source_data
        source_data = add_external_area_field(
            in_features = source_data,
            new_field_name = total_intersecting_area,
            layer_with_area_to_grab = redistribution_inputs["distribution_method"],
            dissolve = True)


    intersecting_polygons = intersect(desired_shape, source_data)

    if redistribution_inputs["distribution_method"] in (2, 3):
        logger.debug("Adding %s to %s" % (local_number_of_properties_field, intersecting_polygons))
        # Adding local number of properties to intersecting_polygons
        intersecting_polygons = add_layer_count(
            new_field_name = local_number_of_properties_field,
            in_features = intersecting_polygons,
            count_features = land_parcels)
            # output = "%s\\intersecting_polygons" % arcpy.env.workspace)
    elif arcpy.Exists(redistribution_inputs["distribution_method"]):
        logger.debug("Adding %s to %s" % (local_number_of_properties_field, intersecting_polygons))
        # Adding local number of properties to intersecting_polygons
        intersecting_polygons = add_layer_count(
            new_field_name = local_number_of_properties_field,
            in_features = intersecting_polygons,
            count_features = land_parcels)
            # output = "%s\\intersecting_polygons" % arcpy.env.workspace)
        logger.debug("Adding %s field to %s" % (local_intersecting_area, source_data))
        intersecting_polygons = add_external_area_field(
            in_features = intersecting_polygons,
            new_field_name = local_intersecting_area,
            layer_with_area_to_grab = redistribution_inputs["distribution_method"],
            dissolve = True)

    # delete_if_exists("before_calculating_fields")
    # before_calculating_fields = arcpy.Copy_management(intersecting_polygons, "before_calculating_fields") # FIXME: this raises an ExecuteError. haven't investigates why, but I would use CopyFeatures_Management instead of Copy_management
    # logger.debug("check Dwelling1 of %s" % before_calculating_fields)

    ## Recalculate groth model fields
    for field in redistribution_inputs["fields_to_be_distributed"]:
        if field_in_feature_class(field, intersecting_polygons):
            if redistribution_inputs["distribution_method"] == 1:
                logger.debug("calculating %s field based on portion of total area" % field)
                calculate_field_proportion_based_on_area(
                    field,
                    total_area_field)
            elif redistribution_inputs["distribution_method"] == 2:
                logger.debug("fields in intersecting_polygons = %s" % [f.name for f in arcpy.ListFields(intersecting_polygons)])
                logger.debug("calculating %s field from total GMZ number of properties" % field)
                calculate_field_proportion_based_on_number_of_lots(
                    field,
                    total_properties_field,
                    local_number_of_properties_field,
                    total_area_field)
                # alternative is to return Peron and then calculate only where total = None here.
            elif redistribution_inputs["distribution_method"] == 3:
                if field in [
                        "POP_2016",
                        "Tot_2016"]:
                    calculate_field_proportion_based_on_number_of_lots(
                        field,
                        total_properties_field,
                        local_number_of_properties_field,
                        total_area_field)
                elif field in [
                        "POP_2036",
                        "Tot_2036",
                        "POP_2041",
                        "Tot_2041",
                        "POP_2046",
                        "Tot_2046",
                        "POP_2051",
                        "Tot_2051",
                        "POP_Full",
                        "Tot_Full"]:
                    calculate_field_proportion_based_on_area(
                        field,
                        total_area_field)
                elif field in [
                        "POP_2021",
                        "Tot_2021",
                        "POP_2026",
                        "Tot_2026",
                        "POP_2031",
                        "Tot_2031"]:
                    calculate_field_proportion_based_on_combination(
                        field,
                        total_properties_field,
                        local_number_of_properties_field,
                        total_area_field)
                elif field in [
                        "POP_2011",
                        "Tot_2011"]:
                    arcpy.CalculateField_management(
                        intersecting_polygons,
                        field,
                        "returnNone()",
                        "PYTHON_9.3",
                        """def returnNone():
                               return None""")
            elif arcpy.Exists(redistribution_inputs["distribution_method"]):
                logger.debug("Calculating %s field base on the portion of %s" %
                    (field, redistribution_inputs["distribution_method"]))
                calculate_field_portion_of_external_area(
                    field,
                    total_intersecting_area,
                    local_intersecting_area,
                    total_properties_field,
                    local_number_of_properties_field,
                    total_area_field)


    ## Spatially Join intersecting_polygons back to redistribution layer
    fieldmappings = arcpy.FieldMappings()
    for field in arcpy.ListFields(redistribution_inputs["layer_to_redistribute_to"]):
        if field.name not in ['OBJECTID', 'Shape_Length', 'Shape_Area', 'Join_Count', 'Shape', 'SHAPE']:
            logger.debug("Adding fieldmap for %s" % field.name)
            fm = arcpy.FieldMap()
            fm.addInputField(redistribution_inputs["layer_to_redistribute_to"], field.name)
            renameFieldMap(fm, field.name)
            fieldmappings.addFieldMap(fm)
    for field in redistribution_inputs["fields_to_be_distributed"]:
        if field_in_feature_class(field, intersecting_polygons):
            fm_POP_or_Total = arcpy.FieldMap()
            fm_POP_or_Total.addInputField(intersecting_polygons, field)
            renameFieldMap(fm_POP_or_Total, field)
            fm_POP_or_Total.mergeRule = "Sum"
            fieldmappings.addFieldMap(fm_POP_or_Total)
    delete_if_exists(redistribution_inputs["output_filename"])
    logger.debug("joining intersecting_polygons back to redistribution layer")
    delete_if_exists(intersecting_polygons_buffered)
    arcpy.Buffer_analysis(
        in_features=intersecting_polygons,
        out_feature_class=intersecting_polygons_buffered,
        buffer_distance_or_field=-1)
    output = arcpy.SpatialJoin_analysis(
        target_features=desired_shape,
        join_features=intersecting_polygons_buffered,
        out_feature_class=redistribution_inputs["output_filename"],
        join_operation="JOIN_ONE_TO_ONE",
        join_type="KEEP_ALL",
        field_mapping=fieldmappings,
        match_option="Intersect")
    assert os.sep in str(output)
    redistribution_inputs["output_filename"] = str(output)
    logger.info("Successfully redistributed %s to %s" % (source_data, desired_shape))
    logger.info("intersecting_polygons file can be found at %s" % intersecting_polygons)
    logger.info("Output file can be found at %s" % redistribution_inputs["output_filename"])


def for_each_feature(feature_class, cb, *args, **kwargs):
    """
    Iterates over each feature in a feature class, and calls the cb function
    passing in a single feature layer containing the feature of the itteration.
    """
    if "where_clause" in kwargs.keys():
        where_clause = kwargs["where_clause"]
    else:
        where_clause = None
    # TODO: use `os.path.exists(feature_class)` here instead
    if "\\" not in feature_class:
        log("WARNING: looping likes to receive the feature_class as the full path to the file, not just the name. A backslash (\\) was not found in %s" % feature_class)
    feature_layer='feature_layer'
    logger.debug("Itterating over %s..." % feature_class)
    id_field = get_identifying_field(feature_class)
    with arcpy.da.SearchCursor(feature_class, id_field, where_clause) as cursor:
        for row in bar(cursor):
            arcpy.MakeFeatureLayer_management(
                in_features=feature_class,
                out_layer=feature_layer,
                where_clause="%s = %s" % (id_field, row[0]))
            cb(feature_layer, *args)
            arcpy.Delete_management(feature_layer)


def get_sum(field_name, feature_class):
    """Returns the sum of all the features in the field_name field of the feature_class"""
    count = 0
    with arcpy.da.SearchCursor(feature_class, field_name) as cursor:
        for row in cursor:
            if row[0] is not None:
                count += row[0]
    return count


def apply_symbology(source, destinations):
    """
    Applies the symbology from the source to each layer in the destination list.
    Only useful when run from the python window in arcmap.

    Params
    ------

    first: source
        The layer that has the symbology to apply
    second: destinations
        A list of layers to apply the symbology to, or a string representing a
        single layer.

    Returns nothing. The source can be easily written by draging the layer into
    the python window from the table of contents. The desintation list can be
    done similarly by dragging into multiple highlighted layers.
    """
    if type(destinations) == type("some string"):
        arcpy.ApplySymbologyFromLayer_management(destinations, source)
    elif type(destinations) == type([]):
        for layer in destinations:
            arcpy.ApplySymbologyFromLayer_management(layer, source)
    else:
        raise AttributeError("Error: destinations attribute was %s, but should have been either string or list." % type(destinations))


def log(text):
    print(text)
    logger.info(text)
    # TODO: if arcpy has attribute:
    #     arcpy.AddMessage(text)


def join_csv(in_data, in_field, csv, csv_field, output=None, included_fields="#"):
    """
    Converts a csv to a table, then joins it to another table.
    """
    try:
        if output:
            in_data = arcpy.Copy_management(
                in_data = in_data,
                out_data = output)
        # TODO: check for strings and if they are found, issue a warning
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
        logger.debug('creating temp_table...')
        arcpy.TableToTable_conversion(
            in_rows=csv,
            out_path=arcpy.env.workspace,
            out_name="temp_table")
        logger.debug('joining temp_table to %s...' % in_data)
        logger.debug('%s in %s = %s' % (csv_field, arcpy.env.workspace+"\\temp_table", field_in_feature_class(csv_field, arcpy.env.workspace+"\\temp_table")))
        logger.debug('fields in %s:' % arcpy.env.workspace+"\\temp_table")
        for f in arcpy.ListFields(arcpy.env.workspace+"\\temp_table"):
            logger.debug("  %s" % f.name)
        output = arcpy.JoinField_management(
            in_data,
            in_field,
            join_table=arcpy.env.workspace+"\\temp_table",
            join_field=csv_field,
            fields=included_fields)
        arcpy.Delete_management(arcpy.env.workspace+"\\temp_table")
        logger.debug('%s joined to %s' % (csv, in_data))
        return output
    except arcpy.ExecuteError as e:
        if re.match('.*The value is not a Data Element.*', e.args[0]):
            log("")
            log("WARNING: you may need to remove the in_data (%s) from the Table of contents before running this tool." % in_data)
            raise e
        else:
            raise e


def export_to_csv(in_data, out_csv):
    """Write the input table to a csv file."""
    from csv import writer
    logger.debug("Exporting %s to %s" % (in_data, out_csv))
    fields = arcpy.ListFields(in_data)
    field_names = [f.name for f in fields]
    logger.debug("  fields to add: %s" % field_names)
    if arcpy.Exists(out_csv):
        logger.warning("WARNING: %s was overwritten" % out_csv)
    with open(out_csv, 'wb') as f:
        w = writer(f)
        w.writerow(field_names)
        with arcpy.da.SearchCursor(in_data, field_names) as cursor:
            for row in cursor:
                w.writerow(row)


def list_contents_of(geodatabase, wildcard=None):
    """returns a list of the features classes in the geodatabase supplied"""
    logging.debug("setting input to string")
    geodatabase = str(geodatabase)
    logging.debug("Checking intput is gdb")
    if not re.match(".*[.]gdb", geodatabase):
        raise AttributeError("input provided is not a geodatabase ('.gdb' not found in path)")
    logging.debug("preserving old workspace")
    old_workspace = str(arcpy.env.workspace)
    logging.debug("setting workspace to geodatabase")
    arcpy.env.workspace = geodatabase
    if wildcard:
        logging.debug("getting results with wildcard")
        result = arcpy.ListFeatureClasses(wildcard)
    else:
        logging.debug("getting results without wildcard")
        result = arcpy.ListFeatureClasses()
        logging.debug("result = %s" % result)
    if result == []:
        logging.warning("No results found in %s" % geodatabase)
    logging.debug("setting workspace back to what it was originally")
    arcpy.env.workspace = old_workspace
    return result

def get_duplicates(table, field):
    def get_all_values(table, field):
        with arcpy.da.SearchCursor(table, [field]) as cursor:
            return [row[0] for row in cursor]

    uniques = unique_values(table, field)
    all_values = get_all_values(table, field)
    for value in uniques:
        i = all_values.index(value)
        del all_values[i]
    duplicates = sorted(all_values)
    return duplicates

def get_verts(fcl):
    """get the verticies of a polygon. source: https://gis.stackexchange.com/questions/9433/extracting-coordinates-of-polygon-vertices-in-arcmap"""
    desc = arcpy.Describe(fcl)
    shapefieldname = desc.ShapeFieldName
    gebieden = arcpy.UpdateCursor(fcl)
    for gebied in gebieden:
        polygoon = gebied.getValue(shapefieldname)
        for punten in polygoon:
            print "shape:"
            for punt in punten:
                print "  ", punt.X, punt.Y
