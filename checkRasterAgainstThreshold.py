#**********************************************************************
# Source:
# This script was created based on the one found here: 
# http://resources.esri.com/help/9.3/arcgisdesktop/com/gp_toolref/automating_your_work_with_models/field_check_script.htm
#
# For input into modelbuilder, see http://resources.esri.com/help/9.3/arcgisdesktop/com/gp_toolref/automating_your_work_with_models/branching_colon_implementing_if_then_else_logic.htm
#
# Description:
# Tests if any cells in a raster are larger than the threshold:
#   Threshold - The value of which no cell in the raster can exceed.
#   All beaneath threshold - true if the every value in the passed in raster is below the threshold
#
# Arguments:
#  0 - Raster name
#  1 - Threshold (double)
#  2 - All zero values (boolean)
#
# Created by: Jared Johnston
#**********************************************************************

# Standard error handling - put everything in a try/except block
#
try:

    # Import system modules
    import sys, string, os, arcgisscripting

    import arcpy
    import numpy as np

    # Create the Geoprocessor object
    gp = arcgisscripting.create()

    # Get input arguments
    #
    in_Raster = gp.GetParameterAsText(0)
    threshold = gp.GetParameterAsText(1)

    #in_Raster = r'C:\TempArcGIS\scratchworkspace.gdb\diff_thresh'
    #threshold = 0.1

    # First check that the raster exists
    #
    if not gp.Exists(in_Raster):
        raise Exception, "Input raster does not exist"

    print "Raster = %s" % in_Raster
    print "Threshold = %s" % threshold

    raster_Array = arcpy.RasterToNumPyArray(in_Raster)
    row_num = raster_Array.shape[0]
    col_num = raster_Array.shape[1]
    cell_count = row_num * row_num
    
    row = 0
    col = 0
    
    values_exceed_threshold = False

    while col < col_num:
        if raster_Array[row, col] > threshold:
		values_exceed_threshold = True
		break
	# print "pixel value =", raster_Array[row, col]
	row+=1
        if row > row_num - 1:
		row = 0
		col+=1

    # Branch depending on whether non-zero values found or not. Issue a
    #  message, and then set our output variables accordingly
    #
    if values_exceed_threshold:
        raise ValueError("Some values in the input raster exceed the threshold. To find out where, see %s" % in_Raster)
        # gp.AddMessage("Non zero value found in raster %s" % in_Raster )
        # gp.SetParameterAsText(2, "False")
	print "this should not get printed. ValueError has not been raised"
    else:
	print "raster doesn't exceed threshold"
        gp.AddMessage("All values in %s are below the %s" % (in_Raster, threshold) )
        gp.SetParameterAsText(2, "True")


# Handle script errors
#
except Exception, errMsg:

    # If we have messages of severity error (2), we assume a GP tool raised it,
    #  so we'll output that.  Otherwise, we assume we raised the error and the
    #  information is in errMsg.
    #
    if gp.GetMessages(2):   
        gp.AddError(GP.GetMessages(2))
    else:
        gp.AddError(str(errMsg))     

