#Start
import os
import numpy as np  
from osgeo import gdal
#from gdalconst import GA_ReadOnly
from osgeo import ogr
from osgeo import osr
import rasterio
import operator
import time
import ntpath
import sys
import subprocess

from rasterstats import zonal_stats

import argparse
parser= argparse.ArgumentParser(description='Program to generate australian future bioclim from global future bioclim')
parser.add_argument('-i','--input_file_path', type=str, metavar='', help='specify the folder where the tif files to be averaged are')
parser.add_argument('-o','--output_directory', type=str, metavar='', help='specify the folder where the resulting file will be stored')
args = parser.parse_args()

# Defining input and output directories
input_file_path=args.input_file_path #"/home/ubuntu/mnt/Alex/gsdms_alex/outputs/out_ssp126_2021-2040"
output_dir= args.output_directory #"/home/ubuntu/mnt/Alex/aus-ppms_alex/outputs"

## String for the wgs projection
wgs_crs = "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"
path_mask1="/home/ubuntu/mnt/Alex/aus-ppms_alex/data/ausmask_noaa_1kmWGS_NA.tif"
path_mask250="/home/ubuntu/mnt2/outputs/mask/ausmask_nesp_250mAlbersEA.tif"
new_crs = "EPSG:4326" 

gsdms_dir = "/home/ubuntu/mnt3" # "/tempdata/research-cifs/6300-payalb/uom_data/gsdms_data" in Payal's drive
aus_dir = "/home/ubuntu/mnt2" # "/tempdata/research-cifs/6300-payalb/uom_data/aus-ppms_data" in Payal's drive
data_dir = "/home/ubuntu/mnt/aus-ppms_alex/data"
temp_dir="/home/ubuntu/mnt/Alex/aus-ppms_alex/temp" #Where I'll store temporal files produced by intermediate steps


def change_nodata_value(infile_path, outfolder):
    filename=ntpath.basename(infile_path)
    out_filename=filename.replace(".tif","nodata.tif") #TODO Handle this assumption later
    outfile_path=os.path.join(outfolder,out_filename)

    os.system(f"gdalwarp -dstnodata -9999 {infile_path} {outfile_path} ")

    return outfile_path

def mask_ones(infile_path,outfolder):

    filename=ntpath.basename(infile_path)
    out_filename=filename.replace(".tif","mask_ones.tif") #TODO Handle this assumption later
    outfile_path=os.path.join(outfolder,out_filename)
    print(f"inside mask_ones")
    call=f'gdal_calc.py -A {infile_path} --outfile {outfile_path} --calc="numpy.where(A!=-9999,1,-9999)" --NoDataValue=-9999'  
    os.system(call)
    print(f"finished call {call}")
    return outfile_path


def get_shapefile(infile_path):
    
    outfile_path = str(infile_path).replace(".tif",".shp")
    out_filename = ntpath.basename(outfile_path)
    
    call = f"gdaltindex {outfile_path} {infile_path}"

    os.system(call)

    print(f"\nGetting index for {infile_path}\n")

    return outfile_path


def get_stats_raster(infile_path, silent=True):
    shapefile_path=get_shapefile(infile_path)
    if not silent:
       print(f'Getting stats for {ntpath.basename(infile_path)}')

    stats = zonal_stats(shapefile_path, infile_path, stats=['min', 'max', 'median', 'majority', 'range' , 
                                                            'nodata', 'percentile_25.0', 'percentile_75.0'])
    
    
    # Deletes .shp, .dbf, .prj and .shx files
    target_dir=os.path.dirname(infile_path)
    junk_extensions=[".dbf",".prj",".shx",".shp"]
    for j in junk_extensions:
        command=f'rm *{j}'
        p=subprocess.Popen(command, cwd=target_dir, shell=True)
        p.wait()

    print(stats[0])
    raster_stats=stats[0]

    return raster_stats

if __name__=="__main__":

    temp_in = input_file_path
    '''temp_dir=output_dir
    temp_out = change_nodata_value(temp_in,temp_dir)
    
    temp_in = temp_out
    temp_out=mask_ones(temp_in,temp_dir)
    
    temp_in=temp_out
    '''

    print(get_stats_raster(temp_in))


    



