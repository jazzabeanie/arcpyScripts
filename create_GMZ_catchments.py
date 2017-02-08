#--------------------------------
# Name: create_GMZ_catchments
# Purpose: to create an area for each point that includes all GMZs whose
# centroid falls within the a buffer distance.
# Author: Jared Johnston
# Created:
# Copyright:   (c) TCC
# ArcGIS Version:   10.2
# Python Version:   2.7
# Source: https://blogs.esri.com/esri/arcgis/2011/08/04/pythontemplate/
#--------------------------------
import os
import sys
import arcpy
import logging

logging.basicConfig(filename='arcpyTemplate.log', # TODO: update log filename
                                            level=logging.DEBUG,
                                            format='%(asctime)s %(message)s')

# Commonly used layers: # TODO: expand this section
GMZ = r'R:\InfrastructureModels\Growth\Database\GrowthModelGMZ.mdb\GMZ'
sde_properties = "O:\\Data\\Planning_IP\\Spatial\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Cadastral\\sde_vector.TCC.Properties"

def do_analysis(*argv):
    """TODO: Add documentation about this function here"""
    try:
        #TODO: Add analysis here
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
    # Arguments are optional
    argv = tuple(arcpy.GetParameterAsText(i)
        for i in range(arcpy.GetArgumentCount()))
    do_analysis(*argv) # https://docs.python.org/2.7/tutorial/controlflow.html#unpacking-argument-lists
