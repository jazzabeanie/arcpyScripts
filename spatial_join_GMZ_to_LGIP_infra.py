import arcpy

arcpy.CheckOutExtension("Highways")

GMZ = r'R:\InfrastructureModels\Growth\Spatial\Database\GrowthModelGMZ.mdb\GMZ'

# LGIP infrastructure layers:
LGIP = {
        'Intersection': r'O:\Data\IC\Spatial Data\LGIP\Database\LGIP.gdb\LGIP_Intersection',
        'Park_Existing': r'O:\Data\IC\Spatial Data\LGIP\Database\LGIP.gdb\LGIP_Park_Existing',
        'Park_Future': r'O:\Data\IC\Spatial Data\LGIP\Database\LGIP.gdb\LGIP_Park_Future',
        'Pathway': r'O:\Data\IC\Spatial Data\LGIP\Database\LGIP.gdb\LGIP_Pathway',
        'Road': r'O:\Data\IC\Spatial Data\LGIP\Database\LGIP.gdb\LGIP_Road',
        'Road_Bridge': r'O:\Data\IC\Spatial Data\LGIP\Database\LGIP.gdb\LGIP_Road_Bridge',
        'Sewerage_Feature': r'O:\Data\IC\Spatial Data\LGIP\Database\LGIP.gdb\LGIP_Sewerage_Feature',
        'Sewerage_Gravity_Main': r'O:\Data\IC\Spatial Data\LGIP\Database\LGIP.gdb\LGIP_Sewerage_Gravity_Main',
        'Sewerage_Rising_Main': r'O:\Data\IC\Spatial Data\LGIP\Database\LGIP.gdb\LGIP_Sewerage_Rising_Main',
        'WaterFeature': r'O:\Data\IC\Spatial Data\LGIP\Database\LGIP.gdb\LGIP_WaterFeature',
        'Watermain': r'O:\Data\IC\Spatial Data\LGIP\Database\LGIP.gdb\LGIP_Watermain'
        }

LGIP = {
        'Sewerage_Gravity_Main': r'O:\Data\IC\Spatial Data\LGIP\Database\LGIP.gdb\LGIP_Sewerage_Gravity_Main',
        'Sewerage_Rising_Main': r'O:\Data\IC\Spatial Data\LGIP\Database\LGIP.gdb\LGIP_Sewerage_Rising_Main'
        }

arcpy.env.workspace = r'O:\Data\IC\Spatial Data\LGIP\Database\scratchworkspace.gdb'

def delete_if_exists(layer):
    """Deleted the passed in layer if it exists. This avoids errors."""
    if arcpy.Exists(layer):
        print("Deleting %s" % layer)
        arcpy.Delete_management(layer)


for layer in LGIP.iterkeys():
    try:
        print('generating .xls file for %s' % layer)
        temp_output = 'LGIP_' + layer
        output = r'O:\Data\Planning_IP\Admin\Staff\Jared\LGIP\Build\Tables\infrastructure_joined_GMZ' + "\\LGIP_" + layer + ".xls"
        out_path = arcpy.env.workspace
        out_name = 'LGIP_' + layer + '_table'
        delete_if_exists(temp_output)
        delete_if_exists(out_path + "\\" + out_name)
        delete_if_exists(output)
        arcpy.SpatialJoin_analysis(LGIP[layer], GMZ, temp_output)
        # Fieldmap: http://resources.arcgis.com/en/help/main/10.2/index.html#//018z00000078000000
        fm1 = arcpy.FieldMap()
        fm2 = arcpy.FieldMap()
        fms = arcpy.FieldMappings()
        try:
            fm1.addInputField(temp_output, "ID")
        except RuntimeError as e:
            print('  joining this one by LGIP_ID')
            fm1.addInputField(temp_output, "LGIP_ID")
        fm2.addInputField(temp_output, "GMZ")
        fms.addFieldMap(fm1)
        fms.addFieldMap(fm2)
        arcpy.TableToTable_conversion(temp_output, out_path, out_name, "#", fms)
        arcpy.TableToExcel_conversion(out_path + "\\" + out_name, output)
    except Exception as e:
        print('failed for %s' % layer)
        raise e
