## Developed by Jared Johnston

# Import the arcpy site package
import arcpy, numpy

for level in [90, 100, 110, 120, 130]:
	# Your input floating point raster
	raster = r'S:\Infrastructure Planning\S000297 - Bulk Water\CP0008427 Toonpan Water Treatment Plant\Data\GIS Data\Site Options\gunClubDam.gdb\gunClubDam_DEM_volumeFilledTo_' + str(level)

	# Convert the raster to a numpy array
	array = arcpy.RasterToNumPyArray(raster, nodata_to_value = 0)

	# Sum the array
	print "dam wall level =", str(level) + ", total volume [m^3] =", str(array.sum())
