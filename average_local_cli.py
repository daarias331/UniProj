# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 12:24:59 2022

@author: Alex
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 09:51:00 2022

@author: Alex
"""

import os
import numpy as np  
#from matplotlib import pyplot as plt
from osgeo import gdal
import time


import argparse
parser= argparse.ArgumentParser(description='Program to average gcms by ssp and period')
parser.add_argument('-i','--input_directory', type=str, metavar='', help='specify the folder where the tif files to be averaged are')
parser.add_argument('-o','--output_directory', type=str, metavar='', help='specify the folder where the resulting file will be stored')
parser.add_argument('-b','--band', type=int, metavar='',help='Specify which band will be averaged')
parser.add_argument('-s','--ssp', type=str, metavar='',help='Specify which for which ssp the average will be generated. Format "ssp213"')
parser.add_argument('-p','--period', type=str, metavar='',help='Specify which for which period the average will be generated. Format "YYYY-YYYY"')

args = parser.parse_args()

#os.environ['PROJ_LIB']="C:\\Users\\Alex\\.conda\\envs\\bioenv\\Library\\share\\proj"

#biovar=[1]

#ssps=["ssp126"] #,"sp245","ssp370","ssp585"]

#periods=["2021-2040","2041-2060","2061-2080","2081-2100"]

    
#gcms=["ACCESS-ESM1-5","BCC-CSM2-MR","CanESM5","CanESM5-CanOE","CMCC-ESM2","CNRM-CM6-1","CNRM-CM6-1-HR","CNRM-ESM2-1",\
      #"EC-Earth3-Veg","EC-Earth3-Veg-LR","FIO-ESM-2-0","GFDL-ESM4","GISS-E2-1-G","GISS-E2-1-H","HadGEM3-GC31-LL",\
       #   "INM-CM4-8","INM-CM5-0","IPSL-CM6A-LR","MIROC-ES2L","MIROC6","MPI-ESM1-2-HR","MPI-ESM1-2-LR","MRI-ESM2-0","UKESM1-0-LL"]


def build_gdal_call(band,infiles, outfile):
    """Builds call to gdal_calc.py 

    Args:
        band (int): Raster band to be used in the call
        infiles (List[str]): List of strings with the paths to input files
        outfile (str): Path to output file

    Returns:
        str: CLI command in str format, to be used in a CLI call
    """
    return  'gdal_calc.py -A '+' '.join(infiles)+f' --outfile={outfile} --A_band={band} --calc="numpy.nanmean(A,axis=0)" --NoDataValue=-9999'
            

def average_ssp_period_sband(band, ssp, period, input_path, out_path=None):
    """_summary_

    Args:
        band (int): Raster band to be used in the call
        ssp (str): ssp for which the average is being calculated
        period (str): period for which the average is being calculated.
        input_path (str, Path): Path to the folder containing the gcm's that will be averaged across
        out_path (str, Path): Path to output folder. Defaults to None. If None, it creates the output folder in the current working directory
    """

    input_folder=''
    if input_path is None:    
        input_folder=os.path.join(os.getcwd(),f"copied_gcms_{ssp}_{period}")
    else:
        input_folder=input_path
    
    if not os.path.exists(input_folder):
        #os.mkdir(out_folder)
        print(f'ERROR: Could not find the path {input_folder} \n')
    else:
        infile_names= os.listdir(input_folder)
        infilepaths=[]
        for f in infile_names:
            path_file=os.path.join(input_folder,f)
            infilepaths.append(path_file)
        
        ## Creates the output folder
        #out_folder=''
        if out_path is None:
            out_folder=os.path.join(os.getcwd(), *['out',f'out_{ssp}_{period}'])
        else:
            out_folder=os.path.join(out_path, *['out',f'out_{ssp}_{period}'])

        if not os.path.exists(out_folder):
            os.makedirs(out_folder)

        out_file_name=f'bio{band}_{ssp}_{period}.tif'
        out_file_path=os.path.join(out_folder, out_file_name)
        
        
        ## Now call gdal_calc
        call = build_gdal_call(band, infilepaths, out_file_path) #Build the CLI call
        
        print(call)
        
        with open(f'{out_folder}/info{ssp}_{period}.txt','w') as f:
            f.write('GCMs used for the average:\n')
            for iname in infile_names:
                f.write(str(iname))
                f.write('\n')


        start=time.time()
        os.system(call) # Calling the gdal_calc.py function
        end=time.time()
        
        print(f"Average completed. Time elapsed: {end-start} seconds")
        
if __name__=='__main__':


    if args.band is None:
        total_bands=19
        for i in range(1,total_bands+1):
            average_ssp_period_sband(i, args.ssp, args.period, args.input_directory, args.output_directory)

    else:
        average_ssp_period_sband(args.band, args.ssp, args.period, args.input_directory, args.output_directory)
     