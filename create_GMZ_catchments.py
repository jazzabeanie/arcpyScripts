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
                    format='%(asctime)s %(message)s')

# Commonly used layers:
GMZ = r'R:\InfrastructureModels\Growth\Database\GrowthModelGMZ.mdb\GMZ'
sde_properties = ("O:\\Data\\Planning_IP\\Spatial\\"
                  "WindowAuth@Mapsdb01@SDE_Vector.sde\\"
                  "sde_vector.TCC.Cadastral""\\sde_vector.TCC.Properties")


def do_analysis(*argv):
    """This function make a catchment for each point in a feature class.
    Takes 2 args:
        1. file with points so make catchments for
        2. file with polygons to use to make catchments
    """
    try:
        points = argv[0]
        catchments = argv[1]
        output = argv[2]
        output1 = (r'O:\Data\IC\Spatial Data\LGIP\Database'
                   r'\scratchworkspace.gdb'
                   r'\tmp_output1')
        m.delete_if_exists(output)
        m.delete_if_exists(output1)
        GMZ_fieldmap = arcpy.FieldMap()
        GMZ_fieldmap.addInputField(catchments, "GMZ")
        ID_fieldmap = arcpy.FieldMap()
        ID_fieldmap.addInputField(points, "ID")
        field_mapping = arcpy.FieldMappings()
        field_mapping.addFieldMap(GMZ_fieldmap)
        field_mapping.addFieldMap(ID_fieldmap)
        arcpy.SpatialJoin_analysis(catchments, points, output1,
                                   "JOIN_ONE_TO_MANY", "KEEP_COMMON",
                                   field_mapping, "HAVE_THEIR_CENTER_IN",
                                   2000)
        arcpy.Dissolve_management(output1, output,
                                  "ID", "",
                                  "", "")
    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
        logging.warning(arcpy.GetMessages(2))
    except Exception as e:
        print e.args[0]
        logging.warning(e.args[0])
# End do_analysis function


# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE,
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == '__main__':
    # Arguments overwrite defaults
    default_points = (r'O:\Data\IC\Spatial Data\LGIP\Database'
                      r'\scratchworkspace.gdb'
                      r'\existing_districtRec_parks_points')
    default_output = (r'O:\Data\IC\Spatial Data\LGIP\Database'
                      r'\scratchworkspace.gdb'
                      r'\existing_disctrictRec_GMZ_catchments')
    argv = [default_points, GMZ, default_output]
    if m.arguments_exist:
        argv = m.return_tuple_of_args()
    do_analysis(*argv) # see here for help on #argv https://docs.python.org/2.7/tutorial/controlflow.html#unpacking-argument-lists # noqa
