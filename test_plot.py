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
gdal.AllRegister()
gdal.UseExceptions()

def dtm_rank(data,size):
    rmin = int(size[0]*size[1]*0.05)
    rmax = int(size[0]*size[1]*0.95)
    print "flter param:", rmin,rmax,size[0],size[1]
    rX = filters.rank_filter(data,rmin,(size[0],size[1]))
    rY = filters.rank_filter(data,rmin,(size[1],size[0]))
    rX = filters.rank_filter(rX,rmax,(size[0],size[1]))
    rY = filters.rank_filter(rY,rmax,(size[1],size[0]))

    return (rX+rY)/2.0

def mean_convoluted(image, m, n):
    kernel=np.full((m,n),1.0/(m*n))
    return scipy.signal.convolve2d(image, kernel, mode="same", boundary="symm")


def dist_flt(nx,ny,ps,data):
    y = np.arange(-1,2,1)
    x = np.arange(-10,11,1)
    xv, yv = np.meshgrid(x,y)
    xv*=ps
    yv*=ps
    z = np.sqrt(xv*xv+yv*yv)
    print z
    return scipy.signal.convolve2d(data,z,mode="same",boundary="symm")



fname = "I:\RF\gronoaltaysk_epi\dsm_8x_flt_clip.tif"#sys.argv[1]
oname = os.path.splitext(fname)[0] + '_ga_3.tif'

ds = gdal.Open(fname,gdal.GA_ReadOnly)
#data = scipy.misc.imread(fname)
nd=ds.GetRasterBand(1).GetNoDataValue()
data=ds.GetRasterBand(1).ReadAsArray().astype(np.float_)
nbands = 1
#data[data==nd]=np.NAN
#out = filters.gaussian_filter(data,5)
#minf = filters.minimum_filter(data,(3,21))
#maxf = filters.maximum_filter(data,(3,21))
#rank = dtm_rank(data,(3,21))
#medianf = mean_convoluted(data,1,21)#filters.median_filter(data,(1,21))
#dist = dist_flt(3,21,4,out)
#mincorr = minf+dist
ps = ds.GetGeoTransform()[1]
print ps
max_a=30
w = 5

#dif = data - filters.minimum_filter(data,(w,w))
#out = np.copy(data)
#tt = (w*ps)*np.math.tan(np.deg2rad(max_a))
#print tt
#out[dif > tt] = np.NAN

#out = ndimage.generic_filter(data,np.nanstd,(5,5))
#out = filters.median_filter(data,(3,3)) - filters.median_filter(data,(9,9))
out = data - filters.gaussian_filter(data,3)

#save
print "save result"
OutDataType=gdal.GDT_Float32
driver=gdal.GetDriverByName("Gtiff")
ods=driver.Create(oname,data.shape[1],data.shape[0],nbands,OutDataType)
ods.SetGeoTransform(ds.GetGeoTransform())
ods.SetProjection(ds.GetProjection())
ob=ods.GetRasterBand(1)
ob.SetNoDataValue(nd)
ob.WriteArray(out,0,0)
#ob=ods.GetRasterBand(2)
#ob.WriteArray(out_lerp,0,0)

ob=None
ods=None

#plt.show()

