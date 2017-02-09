# --------------------------------
# Name: create_GMZ_catchments
# Purpose: to create an area for each point that includes all GMZs whose
# centroid falls within the a buffer distance.
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

logging.basicConfig(filename='arcpyTemplate.log',  # TODO: update log filename
                    level=logging.DEBUG,
                    format='%(asctime)s %(message)s')

# Commonly used layers: # TODO: expand this section
GMZ = r'R:\InfrastructureModels\Growth\Database\GrowthModelGMZ.mdb\GMZ'
sde_properties = ("O:\\Data\\Planning_IP\\Spatial\\"
                  "WindowAuth@Mapsdb01@SDE_Vector.sde\\"
                  "sde_vector.TCC.Cadastral""\\sde_vector.TCC.Properties")


def do_analysis(*argv):
    """This function make a catchment for each point in a feature class.
    Takes 2 args:
        1. file with points so make catchments for
        2. file with polygons to use to make catchments"""
    try:
        points = argv[0]
        catchments = argv[1]
        output = argv[2]
        arcpy.SpatialJoin_analysis (catchments, points, output, {join_operation}, {join_type}, {field_mapping}, {match_option}, {search_radius}, {distance_field_name}) #TODO: finish this spatial join
        # TODO: Complete analysis
        # Spatial join points to GMZs base on buffer
            # join only LGIP_ID of the park
        # merge GMZs based on common LGIP_ID
        # save output layer
        pass
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
    if arcpy.GetArgumentCount() != 0:
        argv = tuple(arcpy.GetParameterAsText(i)
                     for i in range(arcpy.GetArgumentCount()))
    do_analysis(*argv) # see here for help on #argv https://docs.python.org/2.7/tutorial/controlflow.html#unpacking-argument-lists # noqa
