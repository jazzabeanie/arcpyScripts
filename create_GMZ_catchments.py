# --------------------------------
# Name: create_GMZ_catchments
# Purpose: to create an area for each point that includes all GMZs whose
#          centroid falls within the a buffer distance.
# Author: Jared Johnston
# Created:
# Copyright:   (c) TCC
# ArcGIS Version:   10.2
# Python Version:   2.7
# Source: https://blogs.esri.com/esri/arcgis/2011/08/04/pythontemplate/
# --------------------------------
import os # noqa
import sys # noqa
import arcpy
import logging
import jj_methods as m

logging.basicConfig(filename='create_GMZ_catchments.log',
                    level=logging.DEBUG,
                    format='%(asctime)s @ %(lineno)d: %(message)s',
                    datefmt='%Y-%m-%d,%H:%M:%S')
logging.warning("------")

# Commonly used layers:
GMZ = r'R:\InfrastructureModels\Growth\Database\GrowthModelGMZ.mdb\GMZ'
sde_properties = ("O:\\Data\\Planning_IP\\Spatial\\"
                  "WindowAuth@Mapsdb01@SDE_Vector.sde\\"
                  "sde_vector.TCC.Cadastral""\\sde_vector.TCC.Properties")


def do_analysis(*argv):
    """This function makes a catchment for each point in a feature class.
    Takes 2 args:
        1. file with points so make catchments for
        2. file with polygons to use to make catchments
    """
    try:
        existing_park_points = argv[0]
        future_park_points = argv[1]
        catchments = argv[2]
        output = argv[3]
        output1 = (r'O:\Data\IC\Spatial Data\LGIP\Database'
                   r'\scratchworkspace.gdb'
                   r'\tmp_output1')
        all_park_points = (r'C:\TempArcGIS\scratchworkspace.gdb'
                           r'\all_park_points')
        m.delete_if_exists(output)
        m.delete_if_exists(output1)
        m.delete_if_exists(all_park_points)
        arcpy.CopyFeatures_management(existing_park_points, all_park_points)
        arcpy.Append_management(future_park_points, all_park_points, "NO_TEST")
        # Field mapping:
        GMZ_fieldmap = arcpy.FieldMap()
        GMZ_fieldmap.addInputField(catchments, "GMZ")
        ID_fieldmap = arcpy.FieldMap()
        ID_fieldmap.addInputField(all_park_points, "ID")
        hierarchy_fieldmap = arcpy.FieldMap()
        hierarchy_fieldmap.addInputField(all_park_points, "Hierarchy")
        class_fieldmap = arcpy.FieldMap()
        class_fieldmap.addInputField(all_park_points, "Class")
        field_mapping = arcpy.FieldMappings()
        field_mapping.addFieldMap(GMZ_fieldmap)
        field_mapping.addFieldMap(ID_fieldmap)
        field_mapping.addFieldMap(hierarchy_fieldmap)
        field_mapping.addFieldMap(class_fieldmap)
        # ##
        arcpy.SpatialJoin_analysis(catchments, all_park_points, output1,
                                   "JOIN_ONE_TO_MANY", "KEEP_COMMON",
                                   field_mapping, "HAVE_THEIR_CENTER_IN",
                                   2000)
        arcpy.Dissolve_management(output1, output,
                                  ["ID", "Hierarchy", "Class"], "",
                                  "", "")
        logging.warning("Analysis complete. See %s" % output)
    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
        logging.exception(arcpy.GetMessages(2))
    except Exception as e:
        print e.args[0]
        logging.exception(e.args[0])
# End do_analysis function


# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE,
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == '__main__':
    # Arguments overwrite defaults
    default_existing_parks = (r'C:\TempArcGIS\scratchworkspace.gdb'
                              r'\LGIP_allExistingParks_points')
    default_future_parks = (r'O:\Data\IC\Spatial Data\LGIP\Database\LGIP.gdb'
                            r'\LGIP_Park_Future')
    default_output = (r'O:\Data\IC\Spatial Data\LGIP\Database'
                      r'\scratchworkspace.gdb'
                      r'\all_parks_GMZ_catchments')
    argv = [default_existing_parks, default_future_parks, GMZ, default_output]
    arguments_exist = True if (arcpy.GetArgumentCount() != 0) else False
    if arguments_exist:
        argv = tuple(arcpy.GetParameterAsText(i)
                     for i in range(arcpy.GetArgumentCount()))
    do_analysis(*argv) # see here for help on #argv https://docs.python.org/2.7/tutorial/controlflow.html#unpacking-argument-lists # noqa
