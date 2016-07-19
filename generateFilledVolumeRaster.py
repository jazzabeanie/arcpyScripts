#**********************************************************************
# Source:
# Documentation on RasterCalculator here: 
# http://resources.arcgis.com/en/help/main/10.2/index.html#//009z000000z7000000
#
# For input into modelbuilder, see http://resources.esri.com/help/9.3/arcgisdesktop/com/gp_toolref/automating_your_work_with_models/branching_colon_implementing_if_then_else_logic.htm
# and also: http://resources.esri.com/help/9.3/arcgisdesktop/com/gp_toolref/automating_your_work_with_models/field_check_script.htm
#
# Description:
# Creates new rasters from the input raster, one for each fill level provided in the supplied list.
#
# Arguments:
#  0 - Original raster name
#  1 - List of levels to fill each raster to (list)
#
# Created by: Jared Johnston
#**********************************************************************

from arcpy.sa import *

# todo: turn this script into a funtion and make the raster path and list arguments

blacked_out_DEM = Raster(r'S:\Infrastructure Planning\S000297 - Bulk Water\CP0008427 Toonpan Water Treatment Plant\Data\GIS Data\Site Options\gunClubDam.gdb\gunClubDam_DEM_blackedOut')
list_of_levels_to_fill_to = [90, 100, 110, 120, 130]

for level in list_of_levels_to_fill_to:
	print ""
	print "creating raster of volume required to filled to", str(level)
	outRas = Con(blacked_out_DEM < level, level - blacked_out_DEM, 0)
	outRas.save(r'S:\Infrastructure Planning\S000297 - Bulk Water\CP0008427 Toonpan Water Treatment Plant\Data\GIS Data\Site Options\gunClubDam.gdb\gunClubDam_DEM_volumeFilledTo_' + str(level))

