import numpy as np
import scipy
from scipy import signal
import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters
import matplotlib.pyplot as plt
import sys
from osgeo import gdal
from osgeo.gdalconst import *
import numpy.ma as ma
import os.path
import include
gdal.AllRegister()
gdal.UseExceptions()

#if len(sys.argv) < 2:
#    sys.exit(0)

	
fname = sys.argv[1]#'DSM_8x_RAW_flt.tif'
#fname = 'I:\\RF\\bakhchisaray\\dsm_8x.tif'
oname = os.path.splitext(fname)[0] + '_flt.tif'#'DSM_8x_RAW_flt_rank90_it5_t1.tif'

nbands = 2
thresh = 0.75
rmin = sys.argv[2]
rmax = sys.argv[3]

print oname
print "rmin=%f rmax=%f",(rmin,rmax)

ds = gdal.Open(fname,gdal.GA_ReadOnly)
nd=ds.GetRasterBand(1).GetNoDataValue()
data=ds.GetRasterBand(1).ReadAsArray().astype(np.float_)
energy=ds.GetRasterBand(2).ReadAsArray().astype(np.float_)
data[data==nd]=np.NAN

#morphology
openma = ndimage.binary_opening((energy>thresh).astype(np.int),structure=np.ones((3,3))).astype(np.int)
bad_mask = ndimage.binary_closing(openma,structure=np.ones((3,3))).astype(np.int)


#calc regions nd regions & make background mask
background, nb = ndimage.label(np.isnan(data).astype(np.int))
print nb
sizes = ndimage.sum(np.isnan(data), background, range(nb + 1))
mask_size = (sizes < np.max(sizes))
remove_pixel = mask_size[background]
background[remove_pixel]=0
background=ndimage.binary_dilation((background>0).astype(np.int),iterations=10)

#make low correlation mask
labels, nb = ndimage.label(bad_mask)
print nb
sizes = ndimage.sum(bad_mask, labels, range(nb + 1))
mask_size = (sizes < 200)
remove_pixel = mask_size[labels]
labels[remove_pixel]=0

data[bad_mask>0]=np.NAN
data[data<rmin]=np.NAN
data[data>rmax]=np.NAN
data=include.fill(data)
data[background>0]=nd

out = data
out1 = ((labels>0).astype(np.int))
out1[(background>0)] = 2


#save
OutDataType=gdal.GDT_Float32
driver=gdal.GetDriverByName("Gtiff")
ods=driver.Create(oname,data.shape[1],data.shape[0],nbands,OutDataType)
ods.SetGeoTransform(ds.GetGeoTransform())
ods.SetProjection(ds.GetProjection())
ob=ods.GetRasterBand(1)
ob.SetNoDataValue(nd)
ob.WriteArray(out,0,0)
ob=ods.GetRasterBand(2)
ob.WriteArray(out1,0,0)
"""
ob=ods.GetRasterBand(3)
ob.WriteArray(closema,0,0)
ob=ods.GetRasterBand(4)
ob.WriteArray(labels,0,0)
"""

print "done"

ob=None
ods=None

