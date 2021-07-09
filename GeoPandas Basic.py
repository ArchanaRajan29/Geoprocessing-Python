# -*- coding: utf-8 -*-
"""
Created on Tue Jul  6 14:27:12 2021

@author: Ujjwal
"""

import os
import geopandas as gpd
import numpy 
import matplotlib.pyplot as plt

os.chdir(r"C:\IEEE_NITK\HandsOn\Input")

#%% Reading of Data
nybb = gpd.read_file(gpd.datasets.get_path('nybb'))

#%% Save data into shape file
nybb.to_file(r".\nybb.shp")

#%% Multipolygon ShapeFile

nybb.plot()

nybb.centroid.plot()

nybb.plot(column='BoroName')

# Get Current Projection
print(nybb.crs)

# Get Area of Geometry
print("Area (sq. Km):: \n", nybb['geometry'].area / 10**6) 


# reproject data
reproj_nybb = nybb.to_crs(epsg=4326)

# Get centroids of Geometry
print("Centroids :: \n", reproj_nybb.centroid) 

reproj_nybb['centroids'] = reproj_nybb.centroid

# Coordinate based slicing
reproj_nybb.cx[:-74, :].BoroName


# search based on name 
slatenIsland = reproj_nybb[reproj_nybb.BoroName=='Staten Island']

# Get Bounding Box
minx = float(slatenIsland.bounds['minx'])
miny = float(slatenIsland.bounds['miny'])
maxx = float(slatenIsland.bounds['maxx'])
maxy = float(slatenIsland.bounds['maxy'])

print("X Bounds = ", minx, maxx)
print("Y Bounds = ", miny, maxy)



#%% Intersection of shapefiles
world_map = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

intersected_cities = gpd.overlay(world_map, reproj_nybb, how='intersection')

#%% Choropleth Map
intersected_cities.plot(column='Shape_Area')



#%% Manipulation of Attribute
intersected_cities['Shape_Area'] = intersected_cities['Shape_Area'] / 1000000
fig, ax = plt.subplots(1,1)
intersected_cities.plot(column='Shape_Area', ax=ax, legend=True)

#%% How to read spatial data from csv
import pandas as pd
df = pd.read_csv(r"C:\IEEE_NITK\HandsOn\Input\test.csv")
df.columns
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lat, df.lon))
gdf.plot()






















