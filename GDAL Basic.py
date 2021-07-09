# -*- coding: utf-8 -*-
"""
Spyder Editor

Author - Ujjwal Gupta
"""

from osgeo import gdal
import geopandas as gpd
import numpy as np
import os
ie5
import glob

os.chdir(r"C:\IEEE_NITK\HandsOn\Input\awh43j04feb19")

#%%
## Reading of a Geotiff file in GDAL
filename = r"AW-NH43J-096-048C-04Feb19-BAND3.tif"
ds = gdal.Open(filename, gdal.GA_ReadOnly)

#%%
#Get Filelist
print(ds.GetFileList())

## Get Count of bands in gdal dataset
nBands = ds.RasterCount
print("Number Of Bands::", nBands)

## Get width of image
print("Width::", ds.RasterXSize)

## Get height of image
print("Height::", ds.RasterYSize)

## Get Coordinate System / Projection of Image
print("Projection:: \n", ds.GetProjection())

## Get Geotransform Information of Image
# Order --> (ulx, x_size, xskew, uly, yskew, y_pixel)
print("Geotransform:: \n", ds.GetGeoTransform())
gt = ds.GetGeoTransform()

# Conversion from (row,column) of image to coordinates(x,y)
print("Upper Left Corner Coordinates ::", gdal.ApplyGeoTransform(gt, 0, 0))

#%%

## Dataset may have some metadata 
# Metadata can be acessed in thr form of dictionary
print("Metadata::", ds.GetMetadata())

## Number of bands in image
print("Number of Bands::", ds.RasterCount)

#%% Band Object functionalities
band_ds = ds.GetRasterBand(1)

# Metadata of band
print(band_ds.GetMetadata())

# Get Band Statistices
(minimum, maximum, mean, stddev) = band_ds.ComputeStatistics(False)
print("Minimum={},\nMaximum={},\nMean={},\nStdDev={}".format(minimum, maximum, mean, stddev))

#Get NoDatavalue
print("NoDataValue::", band_ds.GetNoDataValue())

#%%
## Convert Band into Numpy Array
band_array = band_ds.ReadAsArray()

plt.imshow(band_array, cmap='gray')

#%%
filenames = glob.glob('AW*.tif')
band3_array = gdal.Open(filenames[1]).ReadAsArray()
band4_array = gdal.Open(filenames[2]).ReadAsArray()

ndvi_array = (band4_array - band3_array)/(band4_array + band3_array)
ndvi_array[(ndvi_array<0)&(ndvi_array>1)] = -999

#%%
# Get Projection and Transform
band3_ds = gdal.Open(filenames[1])
proj = band3_ds.GetProjection()
gt = band3_ds.GetGeoTransform()

del band3_ds

ndvi_filename = filenames[0][:-9]+"NDVI.tif"
dst_drv = gdal.GetDriverByName('GTiff')
dst_ds = dst_drv.Create(ndvi_filename, #dst_filename
                        ndvi_array.shape[1], #width
                        ndvi_array.shape[0], #height
                        1, #Number of Bands
                        gdal.GDT_Float32, # GDAL DataType
                        ['COMPRESS=LZW']) # Create Options 

nodatavalue = -999
dst_ds.SetProjection(proj)
dst_ds.SetGeoTransform(gt)
dst_ds.GetRasterBand(1).WriteArray(ndvi_array)
dst_ds.GetRasterBand(1).SetNoDataValue(nodatavalue)

dst_ds.FlushCache()
del dst_ds

#plt.imshow(ndvi_array, cmap='gray')

#%%
## Stacking of bands (Ex. Generating FCC images)

filenames = glob.glob('AW*BAND*.tif')

### 1. Stacking of Bands ###
array_list = []
for filename in filenames:
    ds = gdal.Open(filename, gdal.GA_ReadOnly)
    array_list.append(ds.ReadAsArray())
    
gt = ds.GetGeoTransform()
proj = ds.GetProjection()    


# Visualization using pyplot
# fig = plt.figure(figsize=(10,20))
# for i in range(1, len(filenames)+1):
#     plt.subplot(1,4, i)
#     plt.imshow(array_list[i-1], cmap='gray')
    
# stacking
stacked_filename = filename[:-9]+"RGB.tif"
stacked_ds = gdal.GetDriverByName('GTiff').Create(stacked_filename, 
                                                  array_list[0].shape[1],
                                                  array_list[0].shape[0],
                                                  len(array_list), 
                                                  gdal.GDT_UInt16,
                                                  ['COMPRESS=LZW'])

stacked_ds.SetGeoTransform(gt)
stacked_ds.SetProjection(proj)
for i in range(len(array_list)):
    stacked_ds.GetRasterBand(i+1).WriteArray(array_list[i])
    
stacked_ds.FlushCache()

stacked_ds = None

#%%
# Stacking Another Tile
os.chdir(r"C:\IEEE_NITK\HandsOn\Input\awh43p04feb19")

#Run Above cell code again

#%%
os.chdir(r'C:\IEEE_NITK\HandsOn\Input')

############# Mosaicing of Images #############
# get list of all files
search_pattern = os.path.join(r'C:\IEEE_NITK\HandsOn\Input', ".\**\*RGB.tif")
rasterlist = glob.glob(search_pattern , recursive=True)
 
#Build VRT
raster_vrt = gdal.BuildVRT(".\Mosaiced_raster.vrt", rasterlist) 

#Convert VRT to Geotiff 
trans_ds = gdal.Translate(r".\Merged_raster.tif", raster_vrt)

#Release
raster_vrt = trans_ds = None

#%%

### Reprojection of Raster ###
ds = gdal.Open(r".\Merged_raster.tif")
warp_options = gdal.WarpOptions(dstSRS="EPSG:32643")
reproj_ds  = gdal.Warp(r".\Reproj.tif", ds, options=warp_options)

reproj_ds = ds = None

#%%
########## Resampling of Raster ############
reproj_ds = gdal.Open(r".\Reproj.tif")

translate_options = gdal.TranslateOptions(xRes=20, yRes=20, resampleAlg='bilinear')

resampled_ds = gdal.Translate(r'.\resampled.tif', reproj_ds, options=translate_options)

del resampled_ds, reproj_ds


#%%

#### Clipping Raster Based on Area Of Interest (AOI) #####
ds = gdal.Open(r".\Merged_raster.tif")
warp_options = gdal.WarpOptions(cutlineDSName=r'.\mansa.shp',
                                cropToCutline=True,
                                dstNodata=0)
clipped_ds = gdal.Warp(".\clipped.tif", ds, options=warp_options)

del clipped_ds, ds

#%% Rasterization of vector data

from osgeo import ogr

## Read Vector Data ##
shp_ds = ogr.GetDriverByName("ESRI Shapefile").Open('.\mansa.shp', 0)
layer = shp_ds.GetLayer('mansa')
shp_crs= layer.GetSpatialRef()  

# Create destds with same details as ref image
ref_ds = gdal.Open(r".\Merged_raster.tif")

#get bounds
gt = ref_ds.GetGeoTransform()
xmin = gt[0]
ymax = gt[3]

xmax = xmin + ref_ds.RasterXSize * gt[1]
ymin = ymax + ref_ds.RasterYSize * gt[5]

del ref_ds

rasterize_options = gdal.RasterizeOptions(outputBounds=[xmin, ymin, xmax, ymax],
                                          outputType=gdal.GDT_Byte,
                                          xRes=gt[1], yRes=-1*gt[5],
                                          creationOptions=['COMPRESS=LZW'],
                                          allTouched=True, noData=0, burnValues=255)


ds = gdal.Rasterize(r".\Rasterized.tif", '.\mansa.shp', format='GTiff', options=rasterize_options)

ds = None
shp_ds = None
layer = None














