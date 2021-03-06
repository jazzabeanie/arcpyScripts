from __future__ import division
# --------------------------------
# Name: TODO
# Purpose: TODO
# Author: Jared Johnston
# Created: TODO
# Copyright:   (c) TCC
# ArcGIS Version:   10.5
# Python Version:   2.7
# Source: https://blogs.esri.com/esri/arcgis/2011/08/04/pythontemplate/
# --------------------------------
import os # noqa
import sys # noqa
import arcpy
import logging
import json
import imp
import argparse
from datetime import datetime
try:
    import progressbar
    bar = progressbar.ProgressBar()
except ImportError as e: # ie, when progressbar is not installed (this is untested)
    def bar(itterable):
        return itterable
jj = imp.load_source('jj_methods', r'\\corp\tcc\Plan & Comm Engage\Plan\Data\Planning_IP\Admin\Staff\Jared\GIS\Tools\arcpyScripts\jj_methods.py') # https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path

# https://docs.python.org/2/library/argparse.html#module-argparse
# https://docs.python.org/2/howto/argparse.html
# parse the arguments:
parser = argparse.ArgumentParser(description='TODO: write a little description about what the function does. Maybe this should be the same as the do_analysis docstring?')
# TODO: set mandatory arguments here:
# parser.add_argument("growth_by_gmz", help="A string containing the path to a csv file containing the growth information by GMZs.")
# parser.add_argument("join_output", help="A string containing the path of the location to save the GMZ feature class once the growth data has been added.")
# TODO: set optional arguments here:
parser.add_argument("-t",
                    "--testing",
                    action="store_true",
                    help="Indicates that the script is in testing mode. " + \
                         "Gives development options, increased logging level.")
args = parser.parse_args()
if args.testing:
    testing = True
    print("Testing mode = %s" % testing)
else:
    testing = False

# arcpy.env.workspace = "in_memory" # I think some tools aren't compatible with in_memory workspaces (like the redistributePolygon tool).
arcpy.env.workspace = "C:\TempArcGIS\scratchworkspace.gdb"
now = r'%s' % datetime.now().strftime("%Y%m%d%H%M")

if __name__ == '__main__':
    logging.basicConfig(filename='log.log',  # TODO
        level=logging.DEBUG,
        format='%(asctime)s @ %(lineno)d: %(message)s',
        datefmt='%Y-%m-%d,%H:%M:%S')
else:
    logging.getLogger(__name__)

# Commonly used layers:
sde = "O:\\Data\\Planning_IP\\Spatial\\WindowAuth@Mapsdb01@SDE_Vector.sde"

GMZ = r'R:\InfrastructureModels\Growth\Spatial\Database\GrowthModelGMZ.mdb\GMZ'
sde_properties = "%s\\sde_vector.TCC.Cadastral\\sde_vector.TCC.Properties" % sde
sde_landParcels = "%s\\sde_vector.TCC.Cadastral\\sde_vector.TCC.Land_Parcels" % sde
sde_roadShapes = "%s\\sde_vector.GSS.core\\SDE_Vector.GSS.road_section_polygon" % sde
sde_roadLines = "%s\\sde_vector.TCC.Cadastral\\SDE_Vector.TCC.roadcent" % sde

## City Plan
zoning = "%s\\SDE_Vector.TCC.Cityplan_2014_Core\\SDE_Vector.TCC.CP14_G_Zoning" % sde

## Flooding
flood_study_areas = "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Flooding\\sde_vector.TCC.FloodStudyAreas_Current"

## Waste Water
overall_catchments = "O:\\Data\\Planning_IP\\Admin\\Spatial Data\\Water_sewer\\Sewer_Catchments_2015\\Sewer_Catchments_2015.mdb\\Overall_Catchments"

## Census
SA1 = r'O:\Data\Planning_IP\Admin\Staff\Jared\LGIP\2016 Census Mesh Block Data\derived_layers.gdb\SA1_2016_TSV_Project'
SA2 = r'O:\Data\Planning_IP\Admin\Staff\Jared\LGIP\2016 Census Mesh Block Data\derived_layers.gdb\SA2_2016_TSV_Project'

## Infrastructure
with open("O:\\Data\\Planning_IP\\Admin\\Staff\\Jared\\GIS\\Tools\\arcpyScripts\\infrastructure_layers.json") as data_file:
        infrastructure = json.load(data_file)


def do_analysis(*argv):
    try:
        pass
        # TODO: Add analysis here
    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
        logging.exception(arcpy.GetMessages(2))
    except Exception as e:
        print e.args[0]
        logging.exception(e.args[0])
        # logger.error('Some weird error:', exc_info=True)  # logging info: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
# End do_analysis function


# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE,
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == '__main__':
    logging.warning("------")

    do_analysis()
    # see here for help on #argv https://docs.python.org/2.7/tutorial/controlflow.html#unpacking-argument-lists # noqa
    # see here for help on reading *argv in new called function: https://docs.python.org/2.7/tutorial/controlflow.html#keyword-arguments
    os.system('pause')
