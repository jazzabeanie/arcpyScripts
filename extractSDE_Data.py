#**********************************************************************
# Source:
# Documentation on Clip(Analysis) here: 
# http://resources.arcgis.com/en/help/main/10.2/index.html#//000800000004000000
#
# Description:
# Takes a list of shapes as areas and clips a list of SDE data in respect to those shapes.
#
# To run, open a python window and execute the following: `execfile(r'S:\Infrastructure Planning\Staff\Jared\Southern Suburbs Sewer Planning Report\extractSDE_Data.py')`
#
# Created by: Jared Johnston
#**********************************************************************

import arcpy
from arcpy.sa import *

workspace = r'S:\Infrastructure Planning\Staff\Jared\Southern Suburbs Sewer Planning Report\SewerData.gdb\\'
SDE = r"S:\\Infrastructure Planning\\Spatial Data\\WindowAuth@Mapsdb01@SDE_Vector.sde\\sde_vector.TCC.Infrastructure\\sde_vector.TCC.NET_"

# declare variables
areas = ["RiversideRidge", "FairfieldWaters", "TheVillage", "RoseneathTruckStop"] 
SDE_data_to_clip = ['sService', 'sHouseDrainPoint', 'sNetworkStructure', 'sGravityMain', 'sPressureMain', 'sMaintenanceHole', 'sPropertyConnectionPoint']

for area in areas:
	print("Clipping for %s" % area)
	area_shape = workspace + area + "_PS_catchments"
	print("    Area in question: %s" % area_shape)
	for dataset in SDE_data_to_clip:
		print("    Clipping %s" % dataset)
		SDE_dataset = SDE + dataset
		print("        Input dataset: %s" % SDE_dataset)
		out_feature_class = workspace + area + "_" + dataset
		print("        Output dataset: %s" % out_feature_class)
		arcpy.Clip_analysis (SDE_dataset, area_shape, out_feature_class)
		print("        Done")
