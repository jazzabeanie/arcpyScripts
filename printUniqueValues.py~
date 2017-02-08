def return_unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})

# example of use `return_unique_values(r'S:\Infrastructure Planning\Staff\Jared\Sewer Strategy Report Catchments\AssigningManholeNumbersToProperties\SewerGEMS\Database\SewGEMS.mdb\BohlePlains_PropertiesWithUSManholeNumbers', 'PROPERTY_CODE')`
