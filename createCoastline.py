# --------------------------------
# Name: createCoastline.py
# Purpose: To create an updated coastline layer
# Author: Jared Johnston
# Created: 20170823
# Copyright:   (c) TCC
# ArcGIS Version:   10.2
# Python Version:   2.7
# Source: https://blogs.esri.com/esri/arcgis/2011/08/04/pythontemplate/
# --------------------------------
import os # noqa
import sys # noqa
import arcpy
import logging
import json
import jj_methods as m # noqa
# m = imp.load_source('jj_methods', 'O:\Data\Planning_IP\Admin\Staff\Jared\GIS\Tools\arcpyScripts\jj_methods.py') # https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path

arcpy.env.workspace = "in_memory"
# arcpy.env.workspace = arcpy.env.scratchGDB
testing = True

logging.basicConfig(filename='createCoastline.log',
                    level=logging.DEBUG,
                    format='%(asctime)s @ %(lineno)d: %(message)s',
                    datefmt='%Y-%m-%d,%H:%M:%S')
logging.warning("------")

# Commonly used layers:
sde = "O:\\Data\\Planning_IP\\Spatial\\WindowAuth@Mapsdb01@SDE_Vector.sde"

GMZ = r'R:\InfrastructureModels\Growth\Database\GrowthModelGMZ.mdb\GMZ'
DEM = r'\\corp\erp\Spatial\MISC\02_Data_Offline\02_DEM\DEM_2016.gdb\DEM_2016'
DEM_old = r'O:\Data\Planning_IP\Spatial\Base Layers\LIDAR_All_Years_Current_DEM.gdb\LIDAR_All_Years_1m_DEM'
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

## Infrastructure
with open("O:\\Data\\Planning_IP\\Admin\\Staff\\Jared\\GIS\\Tools\\arcpyScripts\\infrastructure_layers.json") as data_file:
        infrastructure = json.load(data_file)


#class Dem(arcpy.sa.Raster):
#    def remove_cells_above(self, height_relative_to_AHD):
#        logging.info("removeing cells of %s above %s" % (self, height_relative_to_AHD))
#        return arcpy.sa.Con(self < height_relative_to_AHD, self)
#    def integise(self):
#        logging.info("Converting %s to integer" % self)
#        return arcpy.sa.Int(self)
#
#
def delete_if_exists(layer):
    """Deleted the passed in layer if it exists. This avoids errors."""
    if arcpy.Exists(layer):
        logging.warning("Deleting %s" % layer)
        arcpy.Delete_management(layer)


def createTideLine(height_relative, AHD_relative, name):
    """Creates a shape using a given height relative to some other datum. In the design case, relative to Lowest Astronomical Tide (LAT) given in https://www.msq.qld.gov.au/Tides/Tidal-planes"""
    if testing:
        clipped_DEM = r'C:\TempArcGIS\scratchworkspace.gdb\testRaster20170829_%s' % name
        out_polygon_features = r'C:\TempArcGIS\scratchworkspace.gdb\%s' % name
        converted_raster = r'C:\TempArcGIS\scratchworkspace.gdb\%s' % "converted_raster"
    else:
        clipped_DEM = "clipped_DEM_%s" % name
        out_polygon_features = name
        converted_raster = r'converted_raster'
    logging.info("generating shape out of DEM where level is below %s relative to LAT" % height_relative)
    height_relative_to_AHD = height_relative - AHD_relative
    logging.info("    or %s relative to AHD" % height_relative_to_AHD)
    output_raster = "DEM_under_height"
    delete_if_exists(output_raster)
    input_DEM = arcpy.sa.Raster(DEM)
    # input_DEM = Dem(DEM)
    # output_raster = input_DEM \
    #                 .remove_cells_above(height_relative_to_AHD) \
    #                 .integise()
    # trimmed_raster = arcpy.sa.Con(input_DEM < height_relative_to_AHD, input_DEM)
    # filled_raster = arcpy.sa.Fill(trimmed_raster, 0.5) # TODO: remove this step, and address it with the polygon be removing small features.
    # output_raster = arcpy.sa.Int(filled_raster)
    output_raster = arcpy.sa.Int(arcpy.sa.Con(input_DEM < height_relative_to_AHD, input_DEM))
    delete_if_exists(clipped_DEM)
    output_raster.save(clipped_DEM) # temp step to check
    logging.info("clipped_DEM saved to %s" % clipped_DEM)
    delete_if_exists(converted_raster)
    arcpy.RasterToPolygon_conversion(clipped_DEM, converted_raster)
    delete_if_exists(out_polygon_features)
    arcpy.Dissolve_management(converted_raster, out_polygon_features)
    logging.info("polygon saved to %s" % out_polygon_features)


def do_analysis(*argv):
    """TODO: Add documentation about this function here"""
    try:
        if arcpy.CheckExtension("Spatial") == "Available":
            arcpy.AddMessage("Checking out Spatial")
            arcpy.CheckOutExtension("Spatial")
        else:
            raise EnvironmentError('Spatial Analyst not avaiable')
        tsv_MSL_to_LAT = 1.94
        tsv_AHD_to_LAT = 1.856
        # createTideLine(tsv_MSL_to_LAT, tsv_AHD_to_LAT, "mean_sea_level")
        tsv_HAT_to_LAT = 4.11
        createTideLine(tsv_HAT_to_LAT, tsv_AHD_to_LAT, "HAT2")
        arcpy.CheckInExtension("Spatial")
    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
        logging.exception(arcpy.GetMessages(2))
        arcpy.CheckInExtension("Spatial")
    except Exception as e:
        logging.exception(e.args[0])
        print e.args[0]
        arcpy.CheckInExtension("Spatial")
        # logger.error('Some weird error:', exc_info=True)  # logging info: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
# End do_analysis function


# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE,
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == '__main__':
    print("""
Executing analysis
""")
    os.system('pause')
    # Arguments overwrite defaults
    default_output = (r'')
    argv = [default_output]
    arguments_exist = True if (arcpy.GetArgumentCount() != 0) else False
    if arguments_exist:
        argv = tuple(arcpy.GetParameterAsText(i)
                     for i in range(arcpy.GetArgumentCount()))
    do_analysis(*argv) # see here for help on #argv https://docs.python.org/2.7/tutorial/controlflow.html#unpacking-argument-lists # noqa
    os.system('pause')
