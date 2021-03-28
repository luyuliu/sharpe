
import arcpy, csv, numpy
arcpy.env.overwriteOutput = True

base_location = "D:\\Luyu\\sharpe"
csv_location = base_location + "\\SMAP_L4_SM_RF4_20160715T150000_1km.csv"

csv_points = arcpy.MakeTableView_management(in_table=csv_location, out_view='csv_points')

csv_points = arcpy.MakeXYEventLayer_management(csv_location, "Lon", "Lat", "csv_points_raw",
                                arcpy.SpatialReference(6350))

print("Visualization done.")

arcpy.FeatureClassToShapefile_conversion(["csv_points_raw"], base_location)

print("Conversion done.")

csv_points = arcpy.management.MakeFeatureLayer(base_location + "\\csv_points_raw.shp", "csv_points")

arcpy.PointToRaster_conversion(csv_points, "SM", base_location + "\\raster", cell_assignment="MEAN", cellsize=0.009)

print("Rasterization done.")

arcpy.RasterToASCII_conversion(base_location + "\\raster", base_location + "\\ascii.asc")

print("Export done.")