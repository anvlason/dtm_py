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
import include
gdal.AllRegister()
gdal.UseExceptions()

#if len(sys.argv) < 2:
#    sys.exit(0)

	
fname = "I:\RF\gronoaltaysk_epi\dsm_8x_src_flt.tif"#sys.argv[1]#'DSM_8x_RAW_flt.tif'
oname = os.path.splitext(fname)[0] + '_denoised.tif'
nbands = 3
ds = gdal.Open(fname,gdal.GA_ReadOnly)
nd=ds.GetRasterBand(1).GetNoDataValue()
data=ds.GetRasterBand(1).ReadAsArray().astype(np.float_)
back_mask=(data==-9999)
data[back_mask]=np.NAN
sdata=np.copy(data)
mean_data = np.nanmean(data);
data[back_mask]=mean_data
print "DTM denoise filter"
th = 5
tl = -5
tlg = -15
medf = filters.median_filter(data,(3,3))
diff = data - medf
hi_mask = diff > th
lo_mask = diff < tl
out = np.copy(data)
out[hi_mask] = medf[hi_mask]
out[lo_mask] = medf[lo_mask]
gauf = filters.gaussian_filter(data,5)
diff = out - gauf
glo_mask = diff < tlg

#closed = ndimage.grey_closing(out,5)
out1 = np.copy(out)
out1[glo_mask]=gauf[glo_mask]
out1=ndimage.grey_closing(out1,size=3)
out1=ndimage.grey_openning(out1,size=3)
out[back_mask]=np.NAN
out1[back_mask]=np.NAN
nd=-9999
print "Save"
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
ob=ods.GetRasterBand(3)
ob.WriteArray(diff,0,0)
"""
ob=ods.GetRasterBand(4)
ob.WriteArray(out3,0,0)
"""

print "done"

ob=None
ods=None

