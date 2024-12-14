import pandas as pd

nys_lagosid_path = "ccri_lakes_withLagosID.csv"
nys_lagosid = pd.read_csv(nys_lagosid_path)

nys_lagosid = nys_lagosid[["lagoslakei"]]  # select relevant columns from lagosid


nys_lagosid = nys_lagosid.drop_duplicates()
nys_lagosid.to_csv("insitulakeids.csv", index=False)
print(nys_lagosid)

import geopandas as gp

gp.GeoDataFrame()
shp = gp.GeoDataFrame.from_file("LAGOS_NY_4ha_Polygons/LAGOS_NY_4ha_Polygons.shp")

print(shp.head)

shp = shp[["GNIS_Name", "lagoslakei"]]
shp = shp.drop_duplicates(subset="lagoslakei")

shp.to_csv("all_nys_lakes_lagoslakeids.csv", index=False)

print(shp)
