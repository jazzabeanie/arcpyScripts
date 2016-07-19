#**********************************************************************
# Source:
# This script was created based on the one found here: 
# http://resources.esri.com/help/9.3/arcgisdesktop/com/gp_toolref/automating_your_work_with_models/field_check_script.htm
#
# For input into modelbuilder, see http://resources.esri.com/help/9.3/arcgisdesktop/com/gp_toolref/automating_your_work_with_models/branching_colon_implementing_if_then_else_logic.htm
#
# Description:
# Tests if a field exists and outputs a booleans:
#   All zero values - true if the every value in the passed in raster is zero. If this is a difference raster then the two rasters are equal.
#
# Arguments:
#  0 - Raster name
#  1 - All zero values (boolean)
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

    # Get input arguments - raster name
    #
    in_Raster = gp.GetParameterAsText(0)

    # First check that the raster exists
    #
    if not gp.Exists(in_Raster):
        raise Exception, "Input raster does not exist"

    raster_Array = arcpy.RasterToNumPyArray(in_Raster)
    row_num = raster_Array.shape[0]
    col_num = raster_Array.shape[1]
    cell_count = row_num * row_num
    
    row = 0
    col = 0
    
    non_zero_values_found = False

    while col < col_num:
        if raster_Array[row, col] != 0: # if non zero value
		non_zero_values_found = True
		break
	row+=1
        if row > row_num - 1:
		row = 0
		col+=1

    # Branch depending on whether non-zero values found or not. Issue a
    #  message, and then set our output variables accordingly
    #
    if non_zero_values_found:
        raise ValueError("Non zero value found. The extents of the input rasters are not equal. To see where extents differ, see %s" % in_Raster)
        # gp.AddMessage("Non zero value found in raster %s" % in_Raster )
        # gp.SetParameterAsText(1, "False")
    else:
        gp.AddMessage("All values are zero in raster %s" % in_Raster )
        gp.SetParameterAsText(1, "True")


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
