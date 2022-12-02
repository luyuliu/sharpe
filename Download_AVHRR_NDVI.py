import os
import urllib,urllib2
import requests
import re
from bs4 import BeautifulSoup

url = 'https://www.ncei.noaa.gov/data/avhrr-land-normalized-difference-vegetation-index/access/2016/'
out_path = r'C:\Users\zhaoc\Documents\chen_research\sharpe_seed_grant\NDVI\AVHRR/'
connection = urllib2.urlopen(url)
data = BeautifulSoup(connection)
os.chdir(out_path)
for a in data.find_all('a', href=True):
    if '.nc' in a['href']:
        print("Found the URL:", a['href'])
        urllib.urlretrieve(url+a['href'],filename = a['href'])

# clip to 9 km
import arcpy
import os
path = r'C:\Users\zhaoc\Documents\chen_research\sharpe_seed_grant\NDVI\AVHRR/'
files = os.listdir(path)
os.chdir(path)
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("GeoStats")
for f in range(len(files)):
    # Local variables:
    AVHRR_nc = files[f]
    NDVI_Layer1 = "NDVI_Layer1"
    CONUS_wgs1984 = r"C:\Users\zhaoc\Documents\chen_research\sharpe_seed_grant\data\CONUS_wgs1984.shp"
    out_path = r'C:\\Users\\zhaoc\\Documents\\chen_research\\sharpe_seed_grant\\NDVI\\AVHRR_extract\\'
    out_file = out_path+'NDVI_'+AVHRR_nc[-27:-19]+'.tif'
    point_9km = r'C:\Users\zhaoc\Documents\chen_research\sharpe_seed_grant\data\grid_9km.shp'
    out_table = r'C:\Users\zhaoc\Documents\chen_research\sharpe_seed_grant\NDVI\AVHRR_point/'+'NDVI_'+AVHRR_nc[-27:-19]+'.dbf'
    out_point = r'C:\Users\zhaoc\Documents\chen_research\sharpe_seed_grant\NDVI\AVHRR_point/'+'NDVI_'+AVHRR_nc[-27:-19]+'.shp'
    point_path = r'C:\Users\zhaoc\Documents\chen_research\sharpe_seed_grant\NDVI\AVHRR_point/'
    out_csv = 'NDVI_'+AVHRR_nc[-27:-19]+'.csv'
    if int(AVHRR_nc[-27:-19]) >= 20160827:
        # Process: Make NetCDF Raster Layer
        arcpy.MakeNetCDFRasterLayer_md(AVHRR_nc, "NDVI", "longitude", "latitude", NDVI_Layer1, "", "", "BY_VALUE")

        # Process: Extract by Mask
        arcpy.gp.ExtractByMask_sa(NDVI_Layer1, CONUS_wgs1984, out_file)
        # extract value to points
        arcpy.sa.ExtractValuesToPoints(point_9km, out_file, out_point,"", "")
        # export to csv
        arcpy.TableToTable_conversion(out_point, point_path, out_csv)
