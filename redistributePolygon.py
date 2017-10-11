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
import jj_methods as jj # noqa
import __main__
from datetime import datetime
logging = logging.getLogger(__name__)


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
            logging.info("distribution method type = %s" % inputs["distribution_method"].type)
            raise valueerror('distribution method must be either 1, 2 or 3')
        if __main__.testing:
            testing = __main__.testing
        if __main__.now:
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
            jj.delete_if_exists(feature_layer)
            logging.info("    making feature layer from feature class %s" % feature_class)
            arcpy.MakeFeatureLayer_management(
                    feature_class, # in_features
                    feature_layer, # out_layer
                    "#", # where_clause
                    "#", # workspace
                    "#") # field_info
            if (jj.field_in_feature_class("TARGET_FID", feature_layer)):
                logging.info("    deleteing TARGET_FID field from feature_layer")
                arcpy.DeleteField_management(feature_layer, "TARGET_FID")
            properties_SpatialJoin = "properties_SpatialJoin"
            jj.delete_if_exists(properties_SpatialJoin)
            stats = "stats"
            jj.delete_if_exists(stats)
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
            jj.delete_if_exists(intersecting_polygons)
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
        jj.delete_if_exists(redistribution_layer)
        global total_area_field
        total_area_field = "GMZ_TOTAL_AREA"
        global data_layer
        data_layer = "data_layer"
        jj.delete_if_exists("data_layer")
        arcpy.CopyFeatures_management(inputs["growth_model_polygon"], data_layer)
        arcpy.AddField_management(data_layer, total_area_field, "FLOAT")
        arcpy.CalculateField_management(data_layer, total_area_field, "!Shape_Area!", "PYTHON_9.3")

        add_property_count_to_layer_x_with_name_x(data_layer, total_properties_field)

        arcpy.CopyFeatures_management(inputs["redistribution_layer_name"], redistribution_layer)

        create_intersecting_polygons()

        add_property_count_to_layer_x_with_name_x(intersecting_polygons, local_number_of_properties_field)

        ## Recalculate groth model fields
        for GM_field in inputs["field_list"]:
            if jj.field_in_feature_class(GM_field, intersecting_polygons):
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
                jj.renameFieldMap(fm, field.name)
                fieldmappings.addFieldMap(fm)
        for GM_field in inputs["field_list"]:
            if jj.field_in_feature_class(GM_field, intersecting_polygons):
                fm_POP_or_Total = arcpy.FieldMap()
                fm_POP_or_Total.addInputField(intersecting_polygons, GM_field)
                jj.renameFieldMap(fm_POP_or_Total, GM_field)
                fm_POP_or_Total.mergeRule = "Sum"
                fieldmappings.addFieldMap(fm_POP_or_Total)
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


if __name__ == '__main__':  # then script is being called from command line
    print("""
This script will take the Growth Model results and reportion them to a different shape.
""")
    os.system('pause')
    testing = False
    arcpy.env.workspace = r'C:\TempArcGIS\scratchworkspace.gdb' # TODO: is there a better way to handle this? Does arcpy.env.workspace have a location by default that I can use? can I raise an error if the folder doesn't exist?
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
        logging.basicConfig(filename='redistributePolygon.log',
                            level=logging.INFO,
                            format='%(asctime)s @ %(lineno)d: %(message)s',
                            datefmt='%Y-%m-%d,%H:%M:%S')
        logging.info("testing = False")
    #
    # default input params
    inputs = {}
    inputs["redistribution_layer_name"] = r'o:\data\planning_ip\admin\staff\jared\sewer strategy report catchments\upperross\data.gdb\overall_catchments_20171004_upper_ross'
    inputs["growth_model_polygon"] = r'r:\infrastructuremodels\growth\spatial\database\growthmodelgmz.mdb\gmz'
    inputs["output_filename"] = r'o:\data\planning_ip\admin\staff\jared\sewer strategy report catchments\upperross\data.gdb\upperross_growthmodelredistributedtopscatchments_2'
    jj.delete_if_exists(inputs["output_filename"])
    #
    inputs["intersect_join_field"] = "GMZ"
    inputs["growth_join_field"] = "GMZ"
    inputs["distribution_method"] = 3
    if inputs["distribution_method"] in [1, 2, 3]:
        logging.info("distribution method %s is valid" % inputs["distribution_method"])
    else:
        logging.info("distribution method = %s" % inputs["distribution_method"])
        logging.info("distribution method type = %s" % inputs["distribution_method"].type)
        raise valueerror('distribution method must be either 1, 2 or 3')
    inputs["field_list"] = ["pop_2011", "tot_2011", "pop_2016", "tot_2016", "pop_2021", "tot_2021", "pop_2026", "tot_2026", "pop_2031", "tot_2031", "pop_2036", "tot_2036", "pop_2041", "tot_2041", "pop_2051", "tot_2051", "pop_full", "tot_full"] # lgip moderated gm results have no 2046
    redistributePolygon(inputs)
    os.system('pause')
