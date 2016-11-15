import numpy as np
import scipy
from scipy import signal
import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters
import matplotlib.pyplot as plt
import sys
from osgeo import gdal
from osgeo.gdalconst import *
#import numpy as np
import numpy.ma as ma
import os.path
from pyparsing import (Word,Suppress,alphas,nums)
import datetime

def mtl_parser(mtl_file):

    pos1 = Word(alphas + "_" + nums + alphas)
    pos2 = Word(alphas + '"' + nums + "_" + "." + "-" + "+")
    meso = Suppress("=")
    parser = pos1 + meso + pos2

    mtl = open(mtl_file, mode="r")

    mtl_lib = {}
    group = ""
    for line in mtl:
        if len(line.split("=")) == 2:
            parser_line = parser.parseString(line)

            if parser_line[0] == "GROUP" and parser_line[1] != "L1_METADATA_FILE":
                group = parser_line[1]
                mtl_lib[parser_line[1]] = {}

            elif parser_line[0] != "GROUP" and parser_line[0] != "END_GROUP":
                mtl_lib[group][parser_line[0]] = parser_line[1]

    mtl.close()
    return mtl_lib

if len(sys.argv)<2:
    print "Usage:calibrate_l5.py <MTL_file> [scale]"
    exit(0)

	
gdal.AllRegister()
gdal.UseExceptions()


if sys.argv<3:
    scale = 1
    scale_t = scale
else:
    scale=10000
    scale_t=scale/10
print "scale=%d"%(scale)

#read metadata from MTL
mtl_name = sys.argv[1]#"I:\\6S_TST\\Landsat5\\LT51770242011153KIS01\\L5177024_02420110602_MTL.txt"#sys.argv[1]
mtl=mtl_parser(mtl_name)
gain=np.zeros(7)
bias=np.zeros(7)
im_names = []
o_names = []
sun_elevation=float(mtl['PRODUCT_PARAMETERS']['SUN_ELEVATION'])
sun_azimuth = float(mtl['PRODUCT_PARAMETERS']['SUN_AZIMUTH'])
date=mtl['PRODUCT_METADATA']['ACQUISITION_DATE']
for i in range(0,7):
    num=float(mtl['MIN_MAX_RADIANCE'][sorted(mtl['MIN_MAX_RADIANCE'].keys())[i]])- float(mtl['MIN_MAX_RADIANCE'][sorted(mtl['MIN_MAX_RADIANCE'].keys())[i+7]])
    den=float(mtl['MIN_MAX_PIXEL_VALUE'][sorted(mtl['MIN_MAX_PIXEL_VALUE'].keys())[i]])#- float(mtl['MIN_MAX_PIXEL_VALUE'][sorted(mtl['MIN_MAX_PIXEL_VALUE'].keys())[i+7]])
    gain[i]=num/den
    bias[i]=float(mtl['MIN_MAX_RADIANCE'][sorted(mtl['MIN_MAX_RADIANCE'].keys())[i+7]])#-(gain[i]*float(mtl['MIN_MAX_PIXEL_VALUE'][sorted(mtl['MIN_MAX_PIXEL_VALUE'].keys())[i+7]]))
    im_names.append(mtl_name.replace("_MTL.txt","_B"+str((i+1)*10)+".TIF"))
    o_names.append(os.path.splitext(im_names[i])[0] + "_DOS.TIF")

date = str.split(mtl['PRODUCT_METADATA']['ACQUISITION_DATE'],"-")
#compute parameters
doy=datetime.date(int(date[0]),int(date[1]),int(date[2])).timetuple().tm_yday
d = (1.0-0.01672*np.cos(np.deg2rad(0.9856*doy-4)))
Tz = np.ones(7)#(0.85,0.85,0.85,0.91,0.91,-9999,0.91)
#ESUNL5 = (1957.0,1826.0,1554.0,1036.0,215.0,-9999,80.67)
ESUNL5 = (1957.0,1826.0,1558.618,1036.0,215.0,-9999,80.67)
K1 = 607.76
K2 = 1260.56

#process all bands
for band in range(0,7):
    fname=im_names[band]
    oname=o_names[band]
    if(os.path.isfile(fname)):
        print "Start processing for band %d"%(band+1)
        ds = gdal.Open(fname,gdal.GA_ReadOnly)
        nd=ds.GetRasterBand(1).GetNoDataValue()
        if(nd==None):
            nd=0
        nbands = 1
        data=ds.GetRasterBand(1).ReadAsArray().astype(np.float_)
#remove bumper data
        mask = np.zeros(data.shape)
        mask[data>0]=1
        mask = ndimage.binary_erosion(mask,iterations=40)
        mask = ndimage.binary_dilation(mask,iterations=40)
        data[mask==0]=np.NAN
#calc Temperature
        if(band==5):
            out = (K2/np.log(K1/(data*gain[band]+bias[band])+1))*scale_t
        else:
#calc DOS
            hist=np.histogram(data[~np.isnan(data)],bins=255)
            mm=np.where(hist[0]>(hist[0].sum()*0.01))
            DnMin=hist[1][mm[0][0]-2]
            den = 1.0/(ESUNL5[band]*np.sin(np.deg2rad(sun_elevation))*Tz[band])
            L1 = 0.01*np.sin(np.deg2rad(sun_elevation))*Tz[band]*ESUNL5[band]/(np.pi*(d*d))
            Lp = (DnMin*gain[band]+bias[band])-L1
            sun_rad = (np.sin(np.deg2rad(sun_elevation))*Tz[band]*ESUNL5[band])/(np.pi*(d*d))
            rad_path = (DnMin*gain[band]+bias[band])-sun_rad*0.01
            out = (((data*gain[band]+bias[band])-rad_path)/sun_rad)*scale
#save output data
        print "save result for band %d"%(band+1)
        if(scale==1):
            OutDataType=gdal.GDT_Float32
        else:
            OutDataType=gdal.GDT_UInt16
        driver=gdal.GetDriverByName("Gtiff")
        ods=driver.Create(oname,data.shape[1],data.shape[0],nbands,OutDataType)
        ods.SetGeoTransform(ds.GetGeoTransform())
        ods.SetProjection(ds.GetProjection())
        ob=ods.GetRasterBand(1)
        ob.SetNoDataValue(-9999)
        ob.WriteArray(out,0,0)
        ob=None
        ods=None
        ds=None

print "All done"
