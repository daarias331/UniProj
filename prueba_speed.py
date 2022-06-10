# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 13:41:12 2022

@author: Alex
"""

import os
import numpy as np
from matplotlib import pyplot as plt
from osgeo import gdal
import time


def get_band(path_rast = None, n_band=1, asarr=False):
    ds=gdal.Open(path_rast)
    band=ds.GetRasterBand(n_band)
    
    if asarr:
        return band.ReadAsArray()
    
    return band


'''start = time.time()

arrBand=get_band("Y:\\worldclim\\future\\raw\\cmip6\\30s\\CanESM5\\ssp126\\wc2.1_30s_bioc_CanESM5_ssp126_2021-2040.tif",1)
    
end = time.time()

print(f'time to load and get one band from outer location: {end-start}')
'''


start = time.time()

arrBand3=get_band("C:\\Users\\Alex\\UniProj\\copied_gcms_ssp126_2021-2040\\out_bio1_ssp126_2021-2040\\bio1_ssp126_2021-2040.tif", 1, asarr=True)
 
#arrBand4=get_band("C:\\Users\\Alex\\UniProj\\test_tif\\wc2.1_30s_bioc_ACCESS-ESM1-5_ssp126_2021-2040.tif",1, asarr=True)
   
end = time.time()
print(f'time to load and get one band from local disk: {end-start}')

start = time.time()
avg_band=np.nansum(arrBand3)
#avg_band=np.nanmean(arrBand3)
end = time.time()

print(f'average is {avg_band}, time to average: {end-start}')

print(np.nan)

#%%
from sys import getsizeof

print(getsizeof(arrBand3)/1000000000)