
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
parser.add_argument('-i','--input_directory', type=str, metavar='', help='specify the folder where the tif files to be averaged are')
parser.add_argument('-o','--output_directory', type=str, metavar='', help='specify the folder where the resulting file will be stored')
args = parser.parse_args()

# Defining input and output directories
input_dir=args.input_directory #"/home/ubuntu/mnt/Alex/gsdms_alex/outputs/out_ssp126_2021-2040"
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

def translate_step1(crs, infile_path, outfolder):
    
    #Get the infile name from the path
    filename=ntpath.basename(infile_path)
    out_filename=filename.replace(".tif","_wgs.tif")
    outfile_path=os.path.join(outfolder,out_filename)

    #Makes system call to gdal
    os.system(f"gdal_translate -ot Float32 -a_srs '{crs}' {infile_path} {outfile_path} ")

    return outfile_path


def get_extent(ds):

    """ Return list of corner coordinates from a gdal Dataset
        Taken from: https://gis.stackexchange.com/questions/57834/how-to-get-raster-corner-coordinates-using-python-gdal-bindings
    """
    xmin, xpixel, _, ymax, _, ypixel = ds.GetGeoTransform()
    width, height = ds.RasterXSize, ds.RasterYSize
    xmax = xmin + width * xpixel
    ymin = ymax + height * ypixel

    all_corners=[(xmin, ymax), (xmax, ymax), (xmax, ymin), (xmin, ymin)] #maybe useful later
    min_coord, max_coord =(xmin, ymin), (xmax, ymax)   
    
    return [min_coord , max_coord]


def reduce_layer_extent_step2(path_mask1, infile_path, outfolder):
    
    filename=ntpath.basename(infile_path)
    out_filename=filename.replace("_wgs.tif","_clip.tif") #TODO Handle this assumption later
    outfile_path=os.path.join(outfolder,out_filename)
    
    mask_ds=gdal.Open(path_mask1)
    extent = get_extent(mask_ds)

    os.system(f"gdalwarp -overwrite -ot Float32 -te {extent[0][0]} {extent[0][1]} \
                                                {extent[1][0]} {extent[1][1]} \
                                                {infile_path} {outfile_path}")
    
    return outfile_path


def get_resolution(ds):
    xres, yres = operator.itemgetter(1,5)(ds.GetGeoTransform())
    return xres, -yres


def reproject_to_albers_step3(crs, path_mask250,infile_path, outfolder):

    filename=ntpath.basename(infile_path)
    out_filename=filename.replace("_clip.tif","_reproj.tif") #TODO Handle this assumption later
    outfile_path=os.path.join(outfolder,out_filename)
    
    #Getting mask resolution
    aus_mask=gdal.Open(path_mask250)
    resX, resY = get_resolution(aus_mask)
    print(f"Mask resolution is: ({resX},{-resY}) ")

    #Getting mask crs
    crs_mask=""
    with rasterio.open(path_mask250) as src:
        print ("CRS according to rasterio is:",type(src.crs),str(src.crs))
        crs_mask=str(src.crs)
    
    print("Mask CRS is: ",crs_mask)

    os.system(f"gdalwarp -overwrite -ot Float32 -r bilinear -tr {resX} {resY} \
                            -s_srs '{wgs_crs}' -t_srs '{crs_mask}' {infile_path} {outfile_path}")
    
    # TODO change wgs_crs to crs and pass wgr_crs as parameter in the main function

    return outfile_path


def clip_layer_st_step4(path_mask250, infile_path, outfolder):
    
    filename=ntpath.basename(infile_path)
    out_filename=filename.replace("_reproj.tif","_clip2.tif") #TODO Handle this assumption later
    outfile_path=os.path.join(outfolder,out_filename)

    aus_mask=gdal.Open(path_mask250)

    mask_extent = get_extent(aus_mask)

    os.system(f"gdalwarp -overwrite -ot Float32 -te {mask_extent[0][0]} {mask_extent[0][1]} \
                                                    {mask_extent[1][0]} {mask_extent[1][1]} \
                                                    {infile_path} {outfile_path}")
    return outfile_path


def set_no_datavalue_step5(infile_path, outfolder):
    filename=ntpath.basename(infile_path)
    out_filename=filename.replace("_clip2.tif","nodata.tif") #TODO Handle this assumption later
    outfile_path=os.path.join(outfolder,out_filename)

    os.system(f"gdalwarp -dstnodata -9999 {infile_path} {outfile_path} ")

    return outfile_path

def last_mask_step6(path_mask250, infile_path, outfolder):

    filename=ntpath.basename(infile_path)
    out_filename=filename.replace("nodata.tif",".tif") #TODO Handle this assumption later
    out_filename="aus_future_"+out_filename
    outfile_path=os.path.join(outfolder,out_filename)

    os.system(f"gdal_calc.py -A {infile_path} -B {path_mask250} \
                        --calc='((B==1)*A)+(-9999*(B!=1))' --NoDataValue=-9999  --outfile={outfile_path}")

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

def get_stats_directory(input_dir, output_dir=None):
    #Creating summary of stats for all the tif files in the output directory
    
    infiles=[]
    for file in os.listdir(input_dir):
        # check only text files
        if file.endswith('.tif'):
            infiles.append(file)
    
    if not output_dir:
        output_dir=input_dir

    stats_out_path=os.path.join(output_dir,'report.txt')
    with open(stats_out_path,'w') as f:
        for filename in infiles:
            file_to_stats=os.path.join(output_dir,filename)
            f.write(f'\nStats for {filename} :\n')
            stats=get_stats_raster(file_to_stats)
            for key, value in stats.items():
                f.write(f'{key} : ')
                f.write(f'{value}')
                f.write('\n')



def run_pipeline(infile_path, new_crs, wgs_crs, path_mask1, path_mask250, temp_dir, output_dir):
    #STEP 1
    print("\nSTEP 1 in progress...")
    temp_out=translate_step1(new_crs,infile_path,temp_dir)

    #STEP 2
    print("\nSTEP 2 in progress...")
    temp_in=temp_out
    temp_out=reduce_layer_extent_step2(path_mask1,temp_in,temp_dir)

    #STEP 3
    print("\nSTEP 3 in progress...")
    temp_in=temp_out
    temp_out=reproject_to_albers_step3(wgs_crs, path_mask250, temp_in, temp_dir)

    #STEP 4
    print("\nSTEP 4 in progress...")
    temp_in=temp_out
    temp_out = clip_layer_st_step4(path_mask250,temp_in,temp_dir)

    #STEP 5
    print("\nSTEP 5 in progress...")
    temp_in=temp_out
    temp_out = set_no_datavalue_step5(temp_in,temp_dir)

    # STEP 6
    print("\nSTEP 6 in progress...")
    temp_in=temp_out
    temp_out= last_mask_step6(path_mask250,temp_in, output_dir)

def run_pipeline_directory(input_dir, output_dir):
    rasters = []

    # Iterate directory 
    for file in os.listdir(input_dir):
        # check only .tif files
        if file.endswith('.tif'):
            rasters.append(file)
    
    for raster in rasters:
        temp_in=os.path.join(input_dir,raster)
        run_pipeline(temp_in,new_crs,wgs_crs,path_mask1,path_mask250, temp_dir, output_dir)

    #Now I need the stats of the files I just processed.
    #Therefore, the output_dir becomes the new input_dir for the stats function
    input_dir=output_dir 

    get_stats_directory(input_dir)


def remove_junk_extensions(target_dir):
    junk_extensions=[".dbf",".prj",".shx",".shp"]
    for j in junk_extensions:
        command=f'rm *{j}'
        p=subprocess.Popen(command, cwd=target_dir, shell=True)
        p.wait()



if __name__=="__main__":

    #"/home/ubuntu/mnt/Alex/gsdms_alex/outputs/out_ssp126_2021-2040"

    #/home/ubuntu/mnt/Alex/aus-ppms_alex/outputs
    
    #Code to process all the ssp's and periods.

    '''ssps=["ssp126","ssp245","ssp370","ssp585"]
    periods=["2021-2040","2041-2060","2061-2080","2081-2100"]

    for ssp in ssps:
        for per in periods:
            print(f"\nProcessing australia future bioclim variables for {ssp} and period {per}")
            
            input_dir_loc=os.path.join(input_dir,f"out_{ssp}_{per}")
            output_dir_loc=os.path.join(output_dir,f"out_aus_{ssp}_{per}")
            temp_dir_loc=os.path.join(temp_dir,f"temp_aus_{ssp}_{per}")

            print(f"input dir is: {input_dir}")
            print(f"output dir is: {output_dir}")
            
            if not os.path.exists(output_dir_loc):
                os.makedirs(output_dir_loc)
            else:
                continue
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            run_pipeline_directory(input_dir_loc,output_dir_loc)

    '''
    






