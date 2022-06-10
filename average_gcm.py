# -*- coding: utf-8 -*-
"""
Created on Fri May 20 14:12:47 2022

@author: Alex
"""

import os
import numpy as np
from matplotlib import pyplot as plt
from osgeo import gdal
import time


inpath_p1=os.path.join(*["Y:","worldclim","future","raw","cmip6","30s"]) # Builds the path where the models are stored

#biovar=np.arange(1,19+1)
biovar=[1]

ssps=["ssp126"] #,"sp245","ssp370","ssp585"]

#periods=["2021-2040","2041-2060","2061-2080","2081-2100"]

    
gcms=["ACCESS-ESM1-5","BCC-CSM2-MR","CanESM5","CanESM5-CanOE","CMCC-ESM2","CNRM-CM6-1","CNRM-CM6-1-HR","CNRM-ESM2-1",\
      "EC-Earth3-Veg","EC-Earth3-Veg-LR","FIO-ESM-2-0","GFDL-ESM4","GISS-E2-1-G","GISS-E2-1-H","HadGEM3-GC31-LL",\
          "INM-CM4-8","INM-CM5-0","IPSL-CM6A-LR","MIROC-ES2L","MIROC6","MPI-ESM1-2-HR","MPI-ESM1-2-LR","MRI-ESM2-0","UKESM1-0-LL"]


# inpath_p1=os.path.join(*["C:","Users","Alex","UniProj","test_tiff"]) #This inpath is used for testing purposes only

periods=["2021-2040"] #,"2041-2060"]

#gcms=['ACCESS-ESM1-5','BCC-CSM2-MR',"CanESM5"]  #This gcms are only for testing purposes
    
name_p1="wc2.1_30s_bioc_"


def build_gdal_call(band,infiles, outfile):

    return  'gdal_calc.py -A '+' '.join(infiles)+f' --outfile={outfile} --A_band={band} --calc="numpy.average(A,axis=0)" --NoDataValue=hey'
                


count=0
count_non_exist=0
for bio in biovar:
    for ssp in ssps:
        for period in periods:
            inpaths=[]
            for gcm in gcms:
                count+=1
                
                ## remember to add check exists()
                in_file_name=name_p1+"_".join([gcm,ssp,period])+".tif" #Builds file input name
                in_file_path=os.path.join(*[inpath_p1,gcm,ssp,in_file_name]) #Builds path to input file
                
                if os.path.exists(in_file_path):
                    inpaths.append(in_file_path)
                    print('\n OK it exists')
                else:
                    print(in_file_path, 'Does not exist, skipping')
                    count_non_exist +=1
            
            # Verify and create (if necessary) outout folder in the current directory
            out_folder=os.path.join(os.getcwd(),"output_avg")
            if not os.path.exists(out_folder):
                os.mkdir(out_folder)
            
            out_file_name= "_".join([f'BIO{bio}_30s_',ssp,period])+".tif" # Builds file output name
            out_path=os.path.join(out_folder,out_file_name) #Builds path to output file
            
            #print('\n',inpaths,'\n\n')
            #print(out_path)
            
            '''
            # These paths are just for testing purposes
            inpaths=["C:\\Users\\Alex\\UniProj\\test_tif\\wc2.1_10m_bioc_ACCESS-ESM1-5_ssp126_2021-2040.tif",
                     "C:\\Users\\Alex\\UniProj\\test_tif\\wc2.1_10m_bioc_BCC-CSM2-MR_ssp126_2021-2040.tif",
                     "C:\\Users\\Alex\\UniProj\\test_tif\\wc2.1_10m_bioc_CanESM5_ssp126_2021-2040.tif"]
            '''
           
            cmd=build_gdal_call(bio, inpaths, out_path)
            print(f'Calling gdal calc on band:{bio}, ssp {ssp} and period {period}' )
            
            start=time.time()
            os.system(cmd)
            end=time.time()
            
            print(f"Time to calculate band:{bio}, ssp {ssp} and period {period} was:{end-start}")
            
print(count)
print('# non existent paths: ',count_non_exist)

#%%
#rast1="wc2.1_30s_bioc_ACCESS-ESM1-5_ssp126_2021-2040.tif"
#rast2="wc2.1_30s_bioc_BCC-CSM2-MR_ssp126_2021-2040.tif"


#ds1=gdal.Open(os.path.join(curpath, f'test_tif/{rast1}'))

#ds2=gdal.Open(os.path.join(curpath, f'test_tif/{rast2}'))


#print(ds1)

#print("Size is {} x {} x {}".format(ds1.RasterXSize, ds1.RasterYSize, ds1.RasterCount))   

#band1=ds1.GetRasterBand(1)
#band2=ds2.GetRasterBand(1)

#ar1=band1.ReadAsArray()
#ar2=band2.ReadAsArray()

#for 

#np1=np.nan_to_num(np.array(ar1),nan=0.0)
#np2=np.nan_to_num(np.array(ar2),nan=0.0)

#np1=np1.astype('float64')
#np2=np2.astype('float64')

#print('replaced nan\n',np1)

#to_mean=[ar1,ar2]
#avg=np.mean(to_mean,axis=0)
#print('\n mean\n',avg)
                                   

#gt1=ds1.GetGeoTransform()


#proj1=ds1.GetProjection()


#%%

import numpy as np
from matplotlib import pyplot as plt
from osgeo import gdal

def test_avg(infile, expected):
    
    to_mean=[]
    
    for i, infi in enumerate(infile):
        
        ds=gdal.Open(infile[i])
        band=ds.GetRasterBand(3)
        ar=band.ReadAsArray()
        to_mean.append(ar)
        
    
    avg=np.mean(to_mean,axis=0)
    
    #######################3
    exp=gdal.Open(expected)
    exp_band1=exp.GetRasterBand(1)
    exp_ar1=exp_band1.ReadAsArray()

    print(np.nansum(avg)-np.nansum(exp_ar1))
    
    return avg, exp_ar1

infil=["C:\\Users\\Alex\\UniProj\\test_tif\\wc2.1_10m_bioc_ACCESS-ESM1-5_ssp126_2021-2040.tif",
         "C:\\Users\\Alex\\UniProj\\test_tif\\wc2.1_10m_bioc_BCC-CSM2-MR_ssp126_2021-2040.tif",
         "C:\\Users\\Alex\\UniProj\\test_tif\\wc2.1_10m_bioc_CanESM5_ssp126_2021-2040.tif"]

expecti='C:\\Users\\Alex\\output_avg\\BIO3_ssp126_2021-2040.tif'

averaged, expected =test_avg(infil,expecti)


#%%
data = np.array([[1,2,3], [4,5,np.NaN], [np.NaN,6,np.NaN], [0,0,0]])
masked_data = np.ma.masked_array(data, np.isnan(data))
print(data)
print(masked_data)
#%%
arr1=np.array([1,np.nan])
arr2=np.array([3,4])

print(np.nanmean([arr1,arr2],axis=0))
#%%
import os
pat_l=["Y:","worldclim","future","raw","cmip6","30s","ACCESS-ESM1-5","ssp126","wc2.1_30s_bioc_ACCESS-ESM1-5_ssp126_2021-2040.tif"]
pat=os.path.join(*pat_l)
print(pat)
#print(os.path.abspath(os.getcwd()))
#print(os.getcwd())

print(os.path.exists(pat))

print("_".join(["1","2","3"]))

print(os.path.join(os.getcwd(),"output_avg"))
print('hello world'+'--calc="numpy.average(A,axis=0)"')
#%%
import os
import time

print(os.path.exists('C:\\Users\\Alex\\UniProj\\test_tif\\wc2.1_30s_bioc_BCC-CSM2-MR_ssp126_2021-2040.tif'))

start=time.time()

calci=[i for i in range(10)]
time.sleep(2)

end=time.time()

print("time was: ",end-start)
