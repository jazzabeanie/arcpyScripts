# --------------------------------
# Name: # TODO
# Purpose: # TODO
# Author: Jared Johnston
# Created: # TODO
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
# m = imp.load_source('jj_methods', 'O:\Data\Planning_IP\Admin\Staff\Jared\GIS\Tools\arcpyScripts\jj_methods.py') # https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path

logging.basicConfig(filename='arcpyTemplate.log',  # TODO: update log filename
                    level=logging.DEBUG,
                    format='%(asctime)s @ %(lineno)d: %(message)s',
                    datefmt='%Y-%m-%d,%H:%M:%S')
logging.warning("------")

# Commonly used layers:
sde = "O:\\Data\\Planning_IP\\Spatial\\WindowAuth@Mapsdb01@SDE_Vector.sde"

GMZ = r'R:\InfrastructureModels\Growth\Database\GrowthModelGMZ.mdb\GMZ'
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
infrastructure = {
    'stormwater': {
        'dEndStructure': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_dEndStructure" % sde,
        'dManHole': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_dManHole" % sde,
        'dNetworkStructure': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_dNetworkStructure" % sde,
        'dPit': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_dPit" % sde,
        'dPollutionTrap': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_dPollutionTrap" % sde,
        'dDetentionBasin': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_dDetentionBasin" % sde,
        'dSchematic': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_dSchematic" % sde,
        'dStormWaterPipeBox': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_dStormWaterPipeBox" % sde,
        'dStormwaterPipeCircular': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_dStormwaterPipeCircular" % sde,
        'dStormwaterSubSoil': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_dStormwaterSubSoil" % sde,
        'dSurfaceDrainage': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_dSurfaceDrainage" % sde,
        'dHistoryLine': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_dHistoryLine" % sde,
    },
    'water': {
        'wAccessChamber': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_wAccessChamber" % sde,
        'wCPPoint': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_wCPPoint" % sde,
        'wControlValve': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_wControlValve" % sde,
        'wFitting': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_wFitting" % sde,
        'wHydrant': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_wHydrant" % sde,
        'wMeter': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_wMeter" % sde,
        'wNetworkStructure': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_wNetworkStructure" % sde,
        'wSamplingStation': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_wSamplingStation" % sde,
        'wSensor': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_wSensor" % sde,
        'wStandPipe': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_wStandPipe" % sde,
        'wValve': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_wValve" % sde,
        'wRegulator': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_wRegulator" % sde,
        'wCPLine': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_wCPLine" % sde,
        'wWaterMain': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_wWaterMain" % sde,
        'wWaterService': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_wWaterService" % sde,
        'wHistoryLine': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_wHistoryLine" % sde,
        'declared_water_service_area': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.NET.netother\\sde_vector.NET.DeclaredWaterServiceArea" % sde,
        'yabulu_water_licence': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.yabulu_water_licence" % sde,
        'wHighLevelArea': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_wHighLevelArea" % sde
    },
    'wastewater': {
        'sControlValve': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_sControlValve" % sde,
        'sFitting': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_sFitting" % sde,
        'sMaintenanceHole': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_sMaintenanceHole" % sde,
        'sMeter': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_sMeter" % sde,
        'sNetworkStructure': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_sNetworkStructure" % sde,
        'sOverflowPit': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_sOverflowPit" % sde,
        'sPit': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_sPit" % sde,
        'sPropertyConnectionPoint': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_sPropertyConnectionPoint" % sde,
        'sStandPipe': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_sStandPipe" % sde,
        'sValve': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_sValve" % sde,
        'sGravityMain': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_sGravityMain" % sde,
        'sPressureMain': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_sPressureMain" % sde,
        'sService': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_sService" % sde,
        'boundaryconn_alert': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.NET.netother\\sde_vector.NET.BoundaryConn_Alert" % sde,
        'sHistoryLine': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_sHistoryLine" % sde,
        'sHouseDrainLine': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_sHouseDrainLine" % sde,
        'sHouseDrainPoint': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_sHouseDrainPoint" % sde,
        'declared_wastewater_service_area': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.NET.netother\\SDE_Vector.NET.DeclaredWasteWaterServiceArea" % sde,
        'sewcatch_polygon': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.NET.netother\\sde_vector.NET.sewcatch_polygon" % sde
    },
    'roads': {
        'rMedian': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_rMedian" % sde,
        'rKerbChannel': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_rKerbChannel" % sde,
        'rEdgeBitumen': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_rEdgeBitumen",
        'pms_road_segs': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.pms_road_segs" % sde,
        'road_hierarchy': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.road_hierarchy" % sde,
        'ramroadopperms': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Licences\\sde_vector.TCC.RAMROADOPPERMS" % sde,
        'street_signs': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.STREET_SIGNS" % sde,
        'traffic_arc': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.NET.netother\\sde_vector.NET.traffic_arc" % sde
    },
    'fibre_optics': {
        'fibre_optics_point': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.NET.OpticalFibreDataset\\sde_vector.NET.FibreOpticsPoint" % sde,
        'fibre_optics_lines': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.NET.OpticalFibreDataset\\sde_vector.NET.FibreOpticsLines" % sde
    },
    'subdivisions': {
        'subdivisions_COT': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.subdivisions_COT" % sde,
        'subdivisions': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.NET.netother\\sde_vector.NET.subdivisions" % sde,
        'landscaping_sub': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.NET.netother\\sde_vector.NET.landscaping_sub" % sde
    },
    'survey': {
        'citiworks_survey': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Surveying\\SDE_Vector.TCC.citiworks_survey" % sde,
        'psm_control': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Surveying\\sde_vector.TCC.psm_control" % sde
    },
    'other': {
        'dialysis_patients': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\SDE_Vector.TCC.dialysis_patients" % sde,
        'electric_arc': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.NET.netother\\sde_vector.NET.electric_arc" % sde,
        'transmission_arc': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.GSS.core\\sde_vector.GSS.transmission_arc" % sde,
        'enertrade': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.NET.netother\\sde_vector.NET.enertrade" % sde,
        'trade_waste_licences': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Licences\\sde_vector.TCC.TRADEWASTELICENCES" % sde,
        'sewcatch_polygon': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.NET.netother\\sde_vector.NET.sewcatch_polygon" % sde,
        'refuse_collection_areas': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.EnvironmentalHealth\\sde_vector.TCC.Refuse_Collection_Areas" % sde,
        'light_poles': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Community\\sde_vector.TCC.Light_Poles" % sde,
        'bus_stops': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Community\\sde_vector.TCC.bus_stops" % sde,
        'enertrade': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.NET.netother\\sde_vector.NET.enertrade" % sde,
        'oil_gas_arc': "%s\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.NET.netother\\sde_vector.NET.oil_gas_arc" % sde
    }

}



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
    print("""
# TODO: write instructions here
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
