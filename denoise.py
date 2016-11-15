import numpy as np
import scipy
from scipy import signal
import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters
import matplotlib.pyplot as plt
import sys
from osgeo import gdal
from osgeo.gdalconst import *
import numpy as np
import numpy.ma as ma
import os.path
import include
gdal.AllRegister()
gdal.UseExceptions()

def usage():
    print "Usage: denoise.py [input] [max_dif] [min_dif] <nbands>\n"

if len(sys.argv) < 4:
    print "Bad arguments\n"
    usage()
    sys.exit(0)

fname = sys.argv[1]#"I:\RF\gronoaltaysk_epi\dsm_8x_src_flt.tif"#sys.argv[1]#'DSM_8x_RAW_flt.tif'
oname = os.path.splitext(fname)[0] + '_denoised.tif'
nbands = 2
if len(sys.argv) == 5:
    nbands = int(sys.argv[4])

ds = gdal.Open(fname,gdal.GA_ReadOnly)
nd=ds.GetRasterBand(1).GetNoDataValue()
data=ds.GetRasterBand(1).ReadAsArray().astype(np.float_)
back_mask=(data==-9999)
data[back_mask]=np.NAN
sdata=np.copy(data)
mean_data = np.nanmean(data);
data[back_mask]=mean_data
#print back_mask.shape

#remove small gaps in back_mask
print "Bad mask generation"
label_im,nd_labels = ndimage.label(back_mask)
sizes = ndimage.sum(back_mask,label_im,range(nd_labels+1))
mask_size=sizes < 5 #min hole = 1 pix
remove_pixel=mask_size[label_im]
label_im[remove_pixel]=0
labels =np.unique(label_im)
back_mask = np.searchsorted(labels,label_im)
label_im = None
nd_labels = None
mask_size = None
remove_pixel = None
sizes = None
labels = None
#print back_mask.shape




print "DTM denoise filter"
th = float(sys.argv[2])#1
tl = float(sys.argv[3])##-1
tlg = -15
print "Median filter"
medf = filters.median_filter(data,(7,7))
print "Difference calculation"
diff = data - medf
hi_mask = diff > th
lo_mask = diff < tl
out = np.copy(data)
out[hi_mask] = medf[hi_mask]
out[lo_mask] = medf[lo_mask]
if nbands == 2:
    gauf = filters.gaussian_filter(data,5)
    diff = out - gauf
    glo_mask = diff < tlg
    #closed = ndimage.grey_closing(out,5)
    out1 = np.copy(out)
    out1[glo_mask]=gauf[glo_mask]
    out1=ndimage.grey_closing(out1,size=3)
    out1=ndimage.grey_opening(out1,size=3)
    out1[back_mask]=np.NAN
print "Insert nodata"
out[back_mask>0]=np.NAN

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
if nbands == 2:
    ob=ods.GetRasterBand(2)
    ob.WriteArray(out1,0,0)
"""
ob=ods.GetRasterBand(3)
ob.WriteArray(diff,0,0)
ob=ods.GetRasterBand(4)
ob.WriteArray(out3,0,0)
"""

print "done"

ob=None
ods=None

