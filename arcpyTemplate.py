# --------------------------------
# Name:
# Purpose:
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
import jj_methods as m # noqa

logging.basicConfig(filename='arcpyTemplate.log',  # TODO: update log filename
                    level=logging.DEBUG,
                    format='%(asctime)s @ %(lineno)d: %(message)s',
                    datefmt='%Y-%m-%d,%H:%M:%S')
logging.warning("------")

# Commonly used layers: # TODO: expand this section
GMZ = r'R:\InfrastructureModels\Growth\Database\GrowthModelGMZ.mdb\GMZ'
sde = "O:\\Data\\Planning_IP\\Spatial\\WindowAuth@Mapsdb01@SDE_Vector.sde\\"
sde_properties = "%s\\sde_vector.TCC.Cadastral\\sde_vector.TCC.Properties" % sde
sde_roadShapes = "%s\\sde_vector.GSS.core\\SDE_Vector.GSS.road_section_polygon" % sde
sde_roadLines = "%s\\sde_vector.TCC.Cadastral\\SDE_Vector.TCC.roadcent" % sde



def delete_if_exists(layer):
    """Deleted the passed in layer if it exists. This avoids errors."""
    if arcpy.Exists(layer):
        logging.warning("Deleting %s" % layer)
        arcpy.Delete_management(layer)


def do_analysis(*argv):
    """TODO: Add documentation about this function here"""
    try:
        # TODO: Add analysis here
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
    default_output = (r'')
    argv = [default_output]
    arguments_exist = True if (arcpy.GetArgumentCount() != 0) else False
    if arguments_exist:
        argv = tuple(arcpy.GetParameterAsText(i)
                     for i in range(arcpy.GetArgumentCount()))
    do_analysis(*argv) # see here for help on #argv https://docs.python.org/2.7/tutorial/controlflow.html#unpacking-argument-lists # noqa
