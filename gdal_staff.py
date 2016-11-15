import scipy
import sys
from osgeo import gdal
from osgeo.gdalconst import *
import numpy as np


gdal.AllRegister()
gdal.UseExceptions()

def gdal_write(oname,data,nodata=-9999):    
    OutDataType=gdal.GDT_Float32
    driver=gdal.GetDriverByName("Gtiff")
    nbands=1
    ods=driver.Create(oname,data.shape[1],data.shape[0],nbands,OutDataType)
    ob=ods.GetRasterBand(1)
    ob.SetNoDataValue(nodata)
    ob.WriteArray(data,0,0)
    ob = None
    ods= None

def gdal_read(fname,band):
    ds = gdal.Open(fname,gdal.GA_ReadOnly)
    return ds.GetRasterBand(band).ReadAsArray().astype(np.float)


   
