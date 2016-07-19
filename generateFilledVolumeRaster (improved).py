##====================================
## Raster Calculator / Map Algebra
## Usage: Set workspace, catchment_DEM, and list_of_levels_to_fill_to variables then run in python window with:
## `execfile(r'S:\Infrastructure Planning\S000297 - Bulk Water\CP0008427 Toonpan Water Treatment Plant\Data\GIS Data\Site Options\JCU_hills\generateFilledVolumeRaster.py')`

import arcpy
from arcpy.sa import *

#print "checking out Spatial Analyst..."
#arcpy.CheckOutExtensions("Spatial")

print ""
print "setting workspace..."
arcpy.env.workspace = r"S:\Infrastructure Planning\S000297 - Bulk Water\CP0008427 Toonpan Water Treatment Plant\Data\GIS Data\Site Options\JCU_hills\JCU_hills.gdb"

print ""
print "setting DEM location, and list_of_levels_to_fill_to variables..."
catchment_DEM = Raster('JCU_hills_DEM')
print "DEM =", catchment_DEM
list_of_levels_to_fill_to = [90, 100, 110, 120, 130]
print "list =", list_of_levels_to_fill_to

print ""
print "looping through level in list_of_levels_to_fill_to..."
for level in list_of_levels_to_fill_to:
	print ""
	print "creating raster of volume required to filled to", str(level)
	outRas = Con(catchment_DEM < level, level - catchment_DEM, 0)
	outRas.save('JCU_hills_DEM_volumeFilledTo_' + str(level))
	print "Sucessfully created raster:", arcpy.env.workspace + r"\JCU_hills_DEM_volumeFilledTo_" + str(level)
