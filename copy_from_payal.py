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
#import numpy as np
import time
import shutil

import argparse
parser= argparse.ArgumentParser(description='Program to average gcms by ssp and period')
#parser.add_argument('-i','--input_directory', type=str, metavar='', help='specify the folder where the tif files to be averaged are')
parser.add_argument('-o','--output_folder', type=str, metavar='',help='Specify path where the files will be copied to')
parser.add_argument('-s','--ssp', type=str, metavar='',help='Specify which for which ssp the average will be generated. Format "ssp213"')
parser.add_argument('-p','--period', type=str, metavar='',help='Specify which for which period the average will be generated. Format "YYYY-YYYY"')

args = parser.parse_args()

periods=["2021-2040"] #,"2041-2060"]

    
name_p1="wc2.1_30s_bioc_"


def copy_from_payal(ssp: str, period: str, out=None):
    """Copies gcm's bioclim variables of specified ssp and period, from Payal's drive to Skip's Mediaflux storage
    It follows Payal's folder structure ./worldclim/future/raw/cmip6/30s so it is meant to be run only pointing to that folder  
    Args:
        ssp (str): ssp whose gcm's will be copied
        period (str): period whose gcm's will be copied
        out (str, optional): Output folder. Defaults to None.
    """
    start_glob=time.time()

    # Builds the path where the models are stored, following Payal's drive folder structure
    inpath_p1=os.path.join("/",*["home","ubuntu","mnt3","worldclim","future","raw","cmip6","30s"]) 
    print("Payal's files are in: ",inpath_p1)
    out_folder=''
    if out is None:
        out_folder=f'/home/ubuntu/mnt/exp_alex/{period}/{ssp}'
    else:
        out_folder=os.path.join(out,*[str(period),str(ssp)])

 
    if not os.path.exists(out_folder):
        f"Creating output folder for period {period} and {ssp}"
        os.makedirs(out_folder)

    gcms=["ACCESS-CM2","ACCESS-ESM1-5","BCC-CSM2-MR","CanESM5","CanESM5-CanOE","CMCC-ESM2","CNRM-CM6-1","CNRM-CM6-1-HR","CNRM-ESM2-1",\
      "EC-Earth3-Veg","EC-Earth3-Veg-LR","FIO-ESM-2-0","GFDL-ESM4","GISS-E2-1-G","GISS-E2-1-H","HadGEM3-GC31-LL",\
          "INM-CM4-8","INM-CM5-0","IPSL-CM6A-LR","MIROC-ES2L","MIROC6","MPI-ESM1-2-HR","MPI-ESM1-2-LR","MRI-ESM2-0","UKESM1-0-LL"]

    print("ey")
    
    not_in_payal=[]

    for gcm in gcms:
        #count+=1
        
        ## remember to add check exists()
        # Builds file input name in format 1_30s_bioc_gcm_ssp_period.tiff. 
        # For example:  wc2.1_30s_bioc_ACCESS-CM2_ssp126_2021-2040.tif
        in_file_name=name_p1+"_".join([gcm,ssp,period])+".tif" 

        #Builds path to input file
        in_file_path=os.path.join(*[inpath_p1,gcm,ssp,in_file_name]) 
        
        
        if not os.path.exists(in_file_path):
            print(in_file_path, 'Does not exist in Payals directoy, cannot copy')
            not_in_payal.append(str(in_file_path))
            #count_non_exist +=1
        else:
            print('\n OK it exists in Payals directory, try to copy')
    
            out_file_name=in_file_name
            out_path=os.path.join(out_folder,out_file_name) #Builds path to output file
            
            if os.path.exists(out_path):
                print(f'\nALERT: {out_path} already exists in local dir. Ignore copy operation')
            else:
                print(f'\nCopying from:\n{in_file_path} \nto \n{out_path}')
                start=time.time()
                shutil.copy(in_file_path, out_folder)
                end=time.time()
                print(f'OK {out_path} has been copied. It took {end-start} seconds')
    end_glob=time.time()

    with open(os.path.join(out_folder,'info.txt'),'w') as f:
        f.write("Information")
        f.write("Files not found it Payal's directory:")
        f.writelines(not_in_payal)
        f.write('Time spent:')
        f.write(f'{(end_glob-start_glob)/60} minutes')
        


if __name__=="__main__":
    copy_from_payal(ssp=args.ssp, period=args.period)

