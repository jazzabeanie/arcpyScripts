##====================================
## This tool is designed to generate a table from the output layer of the GenerateServicedGMZ_layer.py tool. This table can be used to look at population growth in sewer serviced areas. This tool was created seperatedly to the GenerateServicedGMZ_layer.py tool so that visual check can ber performed between the twol processors.
## Developed by Jared Johnston
## Source: http://nygeog.github.io//2014/file/geodatabase/shapefile/osgeo4w/2014/08/28/filegeodatabase_osgeo4w_ogr.html
## Usage: Update veriables if required and run in python window with:
## `execfile(r'S:\Infrastructure Planning\Staff\Jared\Sewer Strategy Report Catchments\GrowthModelProjections\GenerateServicedGMZ_table.py')`

import arcpy
import csv
from arcpy import env
arcpy.env.OverwriteOutput = True

# declare variables
ServicedGMZ_layer = 'C:\TempArcGIS\scratchworkspace.gdb\GMZ_with_wasteWaterServiceField'
table   = ServicedGMZ_layer
outfile = 'S:\Infrastructure Planning\Staff\Jared\Sewer Strategy Report Catchments\GrowthModelProjections\GMZ_wasteWaterService_table.csv'

fields = arcpy.ListFields(table)
field_names = [field.name for field in fields]

with open(outfile,'wb') as f:
    w = csv.writer(f)
    w.writerow(field_names)
    for row in arcpy.SearchCursor(table):
        field_vals = [row.getValue(field.name) for field in fields]
        w.writerow(field_vals)
    del row

