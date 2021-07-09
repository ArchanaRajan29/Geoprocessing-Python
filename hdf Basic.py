# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 14:27:14 2021

@author: Ujjwal K. Gupta
"""
from osgeo import gdal
import geopandas as gpd
import numpy
import rasterstats
import os
import matplotlib.pyplot as plt

os.chdir(r"C:\IEEE_NITK\HandsOn\Input")
## Reading of a Geotiff file in GDAL
filename = r"MOD13Q1.A2019001.h24v05.006.2019024152651.hdf"
ds = gdal.Open(filename)

#Get Metatdata Dictionary
print("Dataset Metadata::\n", ds.GetMetadata_Dict())

#Get SubDataset List
subdataset_list = ds.GetSubDatasets()

for sd, description in subdataset_list:
    print(description)
    
band_ds = gdal.Open(subdataset_list[0][0])

# Get Projection
print(band_ds.GetProjection())

# Get Transform
print(band_ds.GetGeoTransform())

data = band_ds.GetRasterBand(1).ReadAsArray()

plt.imshow(data, cmap='gray')


