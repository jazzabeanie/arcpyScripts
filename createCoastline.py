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
from datetime import datetime
# m = imp.load_source('jj_methods', 'O:\Data\Planning_IP\Admin\Staff\Jared\GIS\Tools\arcpyScripts\jj_methods.py') # https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path

arcpy.env.workspace = "in_memory"
# arcpy.env.workspace = arcpy.env.scratchGDB
# arcpy.env.workspace = r'"C:\TempArcGIS\scratchworkspace.gdb"'
testing = False
now = r'%s' % datetime.now().strftime("%Y%m%d%H%M")

logging.basicConfig(filename='createCoastline.log',
                    level=logging.DEBUG,
                    format='%(asctime)s @ %(lineno)d: %(message)s',
                    datefmt='%Y-%m-%d,%H:%M:%S')
logging.warning("------")

# Commonly used layers:
sde = "O:\\Data\\Planning_IP\\Spatial\\WindowAuth@Mapsdb01@SDE_Vector.sde"

GMZ = r'R:\InfrastructureModels\Growth\Database\GrowthModelGMZ.mdb\GMZ'
if testing:
    DEM = r'C:\TempArcGIS\testing.gdb\DEM_strand'
    coastal_DEM = r'C:\TempArcGIS\testing.gdb\DEM_strand_coastal'
else:
    DEM = r'\\corp\erp\Spatial\MISC\02_Data_Offline\02_DEM\DEM_Rasters.gdb\DEM_2016'
    coastal_DEM = r'\\corp\erp\Spatial\MISC\02_Data_Offline\02_DEM\DEM_Rasters.gdb\DEM_2016_Coastal'
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


def delete_if_exists(layer):
    """Deleted the passed in layer if it exists. This avoids errors."""
    if arcpy.Exists(layer):
        logging.warning("Deleting %s" % layer)
        arcpy.Delete_management(layer)


def createSeawardPolygon(height_relative, AHD_relative, name):
    """Creates a shape on the seaward side of a given height relative to some other datum using the DEM. In the design case, relative to Lowest Astronomical Tide (LAT) given in https://www.msq.qld.gov.au/Tides/Tidal-planes"""
    clipped_DEM = r'C:\TempArcGIS\scratchworkspace.gdb\seawardClipped_DEM_%s_%s' % (name, now)
    clipped_coastal_DEM = r'C:\TempArcGIS\scratchworkspace.gdb\seawardClipped_coastal_DEM_%s_%s' % (name, now)
    out_polygon_features = r'C:\TempArcGIS\scratchworkspace.gdb\seaward_%s_%s' % (name, now)
    converted_raster = "converted_raster"
    converted_coastal_raster = "converted_coastal_raster"
    appended_raster = "appended_raster"
    if testing:
        # converted_raster = r'C:\TempArcGIS\scratchworkspace.gdb\%s' % "converted_raster"
        # converted_coastal_raster = r'C:\TempArcGIS\scratchworkspace.gdb\%s' % "converted_coastal_raster"
        # appended_raster = r'C:\TempArcGIS\scratchworkspace.gdb\%s' % "appended_raster"
        pass
    else:
        # clipped_DEM = "clipped_DEM_%s" % name
        # clipped_coastal_DEM = "clipped_coastal_DEM_%s" % name
        pass
    logging.info("generating shape out of DEM where level is below %s relative to LAT" % height_relative)
    height_relative_to_AHD = height_relative - AHD_relative
    logging.info("    or %s relative to AHD" % height_relative_to_AHD)
    output_raster = "DEM_under_height"
    delete_if_exists(output_raster)
    logging.info("creating input raster objects...")
    input_DEM = arcpy.sa.Raster(DEM)
    input_coastal_DEM = arcpy.sa.Raster(coastal_DEM)
    logging.info("trimming rasters...")
    # output_raster = arcpy.sa.Int(arcpy.sa.Con(input_DEM < height_relative_to_AHD, input_DEM))
    output_raster = arcpy.sa.Con(input_DEM < height_relative_to_AHD, 1)
    # output_raster = arcpy.sa.Int(arcpy.sa.SetNull(input_DEM, input_DEM, "Value > %s" % height_relative_to_AHD))
    # output_coastal_raster = arcpy.sa.Int(arcpy.sa.Con(input_coastal_DEM < height_relative_to_AHD, input_coastal_DEM))
    output_coastal_raster = arcpy.sa.Con(input_coastal_DEM < height_relative_to_AHD, 1)
    # output_coastal_raster = arcpy.sa.Int(arcpy.sa.SetNull(input_coastal_DEM, input_coastal_DEM, "Value > %s" % height_relative_to_AHD))
    delete_if_exists(clipped_DEM)
    delete_if_exists(clipped_coastal_DEM)
    output_raster.save(clipped_DEM) # temp step incase checking required
    output_coastal_raster.save(clipped_coastal_DEM) # temp step incase checking required
    pass
    logging.debug("output_raster saved to %s" % output_raster)
    logging.debug("clipped_coastla_DEM saved to %s" % output_coastal_raster)
    # logging.info("clipped_DEM saved to %s" % clipped_DEM)
    # logging.info("clipped_coastla_DEM saved to %s" % clipped_coastal_DEM)
    delete_if_exists(converted_raster)
    delete_if_exists(converted_coastal_raster)
    arcpy.RasterToPolygon_conversion(output_raster, converted_raster)
    arcpy.RasterToPolygon_conversion(output_coastal_raster, converted_coastal_raster)
    # arcpy.RasterToPolygon_conversion(clipped_DEM, converted_raster)
    # arcpy.RasterToPolygon_conversion(clipped_coastal_DEM, converted_coastal_raster)
    logging.info("DEM polygon saved to %s" % converted_raster)
    logging.info("coastal_DEM polygon saved to %s" % converted_coastal_raster)
    delete_if_exists(appended_raster)
    # arcpy.Copy_management(converted_raster, appended_raster)
    arcpy.MakeFeatureLayer_management(converted_raster, appended_raster)
    arcpy.Append_management(converted_coastal_raster, appended_raster)
    delete_if_exists(out_polygon_features)
    arcpy.Dissolve_management(appended_raster, out_polygon_features, "#", "#", "SINGLE_PART")
    logging.info("seaward %s combined polygon saved to %s" % (name, out_polygon_features))

def createLandwardPolygon(height_relative, AHD_relative, name):
    """Creates a landward shape relative to a give height based on the DEM and the coastal_DEM combined."""
    clipped_DEM = r'C:\TempArcGIS\scratchworkspace.gdb\landwardClipped_DEM_%s_%s' % (name, now)
    clipped_coastal_DEM = r'C:\TempArcGIS\scratchworkspace.gdb\landwardClipped_coastal_DEM_%s_%s' % (name, now)
    out_polygon_features = r'C:\TempArcGIS\scratchworkspace.gdb\landward_%s_%s' % (name, now)
    converted_raster = "converted_raster"
    converted_coastal_raster = "converted_coastal_raster"
    appended_raster = "appended_raster"
    if testing:
        pass
        # converted_raster = r'C:\TempArcGIS\scratchworkspace.gdb\%s' % "converted_raster"
        # converted_coastal_raster = r'C:\TempArcGIS\scratchworkspace.gdb\%s' % "converted_coastal_raster"
        # appended_raster = r'C:\TempArcGIS\scratchworkspace.gdb\%s' % "appended_raster"
    else:
        # clipped_DEM = "clipped_DEM_%s" % name
        # clipped_DEM = r'C:\TempArcGIS\scratchworkspace.gdb\landwardClipped_DEM_%s_%s' % (name, now)
        # clipped_coastal_DEM = "clipped_coastal_DEM_%s" % name
        # clipped_coastal_DEM = r'C:\TempArcGIS\scratchworkspace.gdb\landwardClipped_coastal_DEM_%s_%s' % (name, now)
        pass
    logging.info("generating shape out of DEM where level is above %s relative to LAT" % height_relative)
    height_relative_to_AHD = height_relative - AHD_relative
    logging.info("    or %s relative to AHD" % height_relative_to_AHD)
    output_raster = "DEM_above_height"
    delete_if_exists(output_raster)
    logging.info("creating input raster objects...")
    input_DEM = arcpy.sa.Raster(DEM)
    input_coastal_DEM = arcpy.sa.Raster(coastal_DEM)
    logging.info("trimming rasters...")
    # output_raster = arcpy.sa.Int(arcpy.sa.Con(input_DEM > height_relative_to_AHD, input_DEM))
    output_raster = arcpy.sa.Con(input_DEM > height_relative_to_AHD, 1)
    # output_raster = arcpy.sa.Int(arcpy.sa.SetNull(input_DEM, input_DEM, "Value < %s" % height_relative_to_AHD))
    # output_coastal_raster = arcpy.sa.Int(arcpy.sa.Con(input_coastal_DEM > height_relative_to_AHD, input_coastal_DEM))
    output_coastal_raster = arcpy.sa.Con(input_coastal_DEM > height_relative_to_AHD, 1)
    # output_coastal_raster = arcpy.sa.Int(arcpy.sa.SetNull(input_coastal_DEM, input_coastal_DEM, "Value < %s" % height_relative_to_AHD))
    delete_if_exists(clipped_DEM)
    delete_if_exists(clipped_coastal_DEM)
    output_raster.save(clipped_DEM) # temp step incase checking required
    output_coastal_raster.save(clipped_coastal_DEM) # temp step incase checking required
    pass
    logging.debug("clipped_DEM saved to %s" % output_raster)
    logging.debug("clipped_coastal_DEM saved to %s" % output_coastal_raster)
    delete_if_exists(converted_raster)
    delete_if_exists(converted_coastal_raster)
    arcpy.RasterToPolygon_conversion(output_raster, converted_raster)
    arcpy.RasterToPolygon_conversion(output_coastal_raster, converted_coastal_raster)
    logging.info("DEM polygon saved to %s" % converted_raster)
    logging.info("coastal_DEM polygon saved to %s" % converted_coastal_raster)
    delete_if_exists(appended_raster)
    arcpy.MakeFeatureLayer_management(converted_raster, appended_raster)
    arcpy.Append_management(converted_coastal_raster, appended_raster)
    delete_if_exists(out_polygon_features)
    arcpy.Dissolve_management(appended_raster, out_polygon_features, "#", "#", "SINGLE_PART")
    logging.info("landward %s combined polygon saved to %s" % (name, out_polygon_features))

def createTideLine(height_relative, AHD_relative, name): # TODO: cut sea from land and convert to polyline.
    """Creates a shape using a given height relative to some other datum. In the design case, relative to Lowest Astronomical Tide (LAT) given in https://www.msq.qld.gov.au/Tides/Tidal-planes"""
    pass # TODO
    # cuts the seaward polygon from the Land polygon
    # converts the polygone to a line

def do_analysis(*argv):
    """TODO: Add documentation about this function here"""
    try:
        if arcpy.CheckExtension("Spatial") == "Available":
            arcpy.AddMessage("Checking out Spatial")
            arcpy.CheckOutExtension("Spatial")
        else:
            raise EnvironmentError('Spatial Analyst not avaiable')
        # heights taken from: https://www.msq.qld.gov.au/Tides/Tidal-planes
        tsv_MSL_to_LAT = 1.94
        tsv_AHD_to_LAT = 1.856
        createLandwardPolygon(tsv_MSL_to_LAT, tsv_AHD_to_LAT, "mean_sea_level")
        createSeawardPolygon(tsv_MSL_to_LAT, tsv_AHD_to_LAT, "mean_sea_level")
        tsv_HAT_to_LAT = 4.11
        # createSeawardPolygon(tsv_HAT_to_LAT, tsv_AHD_to_LAT, "HAT")
        # TODO: eventually I'll call createTideLine here and that will in turn call createSeawardPolygon.
        logging.info("Need to remove inland features that wouldn't be inundated by the tide but are still below the level")
        logging.info("Then what?? remove any small islands? need to talk with Ashley about this.")
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
