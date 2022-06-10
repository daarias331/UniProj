# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 16:14:24 2022

@author: Alex
"""

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
import shutil


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
    """
    Parameters
    ----------
    infiles : TYPE
        DESCRIPTION.
    outfile : TYPE
        DESCRIPTION.

    Returns
    -------
    string with the shell command to be called on Gda.

    """    
    return  'gdal_calc.py -A '+' '.join(infiles)+f' --outfile={outfile} --A_band={band} --calc="numpy.average(A,axis=0)"'
                


count=0
count_non_exist=0
for bio in biovar:
    for ssp in ssps:
        for period in periods:
            inpaths=[]
            innames=[]
            
            # Verify and create (if necessary) outout folder in the current directory
            out_folder=os.path.join(os.getcwd(),f"copied_gcms_{ssp}_{period}")
            if not os.path.exists(out_folder):
                os.mkdir(out_folder)
            
            if ssp=="ssp126" and period=="2021-2040": #This if allows for only copying specific ssps and periods
                for gcm in gcms:
                    count+=1
                    
                    ## remember to add check exists()
                    in_file_name=name_p1+"_".join([gcm,ssp,period])+".tif" #Builds file input name
                    in_file_path=os.path.join(*[inpath_p1,gcm,ssp,in_file_name]) #Builds path to input file
                    
                    if not os.path.exists(in_file_path):
                        print(in_file_path, 'Does not exist in Payals directoy, skipping')
                        count_non_exist +=1
                    else:
                        inpaths.append(in_file_path)
                        innames.append(in_file_name)
                        print('\n OK it exists in Payals directory, try to copy')
                
                        out_file_name=in_file_name
                        out_path=os.path.join(out_folder,out_file_name) #Builds path to output file
                        
                        if os.path.exists(out_path):
                            print(f'\nALERT: {out_path} already exists in local dir. Ignore copy operation')
                        else:
                            print(f'\nCopying {in_file_path} to {out_path}')
                            start=time.time()
                            shutil.copy(in_file_path, out_path)
                            end=time.time()
                            print(f'OK {out_path} has been copied. It took {end-start} seconds')

            
            #print('\n',inpaths,'\n\n')
            #print(out_path)
            
            '''
            # These paths are just for testing purposes
            inpaths=["C:\\Users\\Alex\\UniProj\\test_tif\\wc2.1_10m_bioc_ACCESS-ESM1-5_ssp126_2021-2040.tif",
                     "C:\\Users\\Alex\\UniProj\\test_tif\\wc2.1_10m_bioc_BCC-CSM2-MR_ssp126_2021-2040.tif",
                     "C:\\Users\\Alex\\UniProj\\test_tif\\wc2.1_10m_bioc_CanESM5_ssp126_2021-2040.tif"]
            '''
           
            
print(count)
print('# non existent paths: ',count_non_exist)
