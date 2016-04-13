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

#--------------------------------------------
def fspecial_gauss(size, sigma):

    """Function to mimic the 'fspecial' gaussian MATLAB function
    """
    x, y = np.mgrid[-size//2 + 1:size//2 + 1, -size//2 + 1:size//2 + 1]
    g = np.exp(-((x**2 + y**2)/(2.0*sigma**2)))
    return g/g.sum()
#--------------------------------------------
def fill(sdata, invalid=None):
    """
    Replace the value of invalid 'data' cells (indicated by 'invalid') 
    by the value of the nearest valid data cell

    Input:
        data:    numpy array of any dimension
        invalid: a binary array of same shape as 'data'. 
                 data value are replaced where invalid is True
                 If None (default), use: invalid  = np.isnan(data)

    Output: 
        Return a filled array. 
    """    
    if invalid is None: invalid = np.isnan(sdata)

    ind = ndimage.distance_transform_edt(invalid, 
                                    return_distances=False, 
                                    return_indices=True)
    return sdata[tuple(ind)]
#--------------------------------------------
def local_diff(sdata,size):

    localmin = filters.minimum_filter(sdata, size)
    localmax = filters.maximum_filter(sdata, size)
    return (localmax-localmin)
#--------------------------------------------
def lerp(sdata,condition):
    xx,yy = np.meshgrid(np.arange(sdata.shape[1]),np.arange(sdata.shape[0]))
    xym = np.vstack( (np.ravel(xx[condition]), np.ravel(yy[condition])) ).T
    values=np.ravel(sdata[:,:][condition])
    interp=scipy.interpolate.LinearNDInterpolator(xym,values)
    return interp(np.ravel(xx), np.ravel(yy)).reshape( xx.shape )
#--------------------------------------------
def localmin(sdata,size,threshold):
    localmin = filters.minimum_filter(sdata, size)
    localdif = sdata-localmin
    with np.errstate(invalid='ignore'):
        return (localdif < threshold)
#        return np.where(localdif < threshold)
#--------------------------------------------
def lerpNANdwn(sdata,step):
    data_back=np.zeros(sdata.shape)
    data_back[:,:]=np.NAN
    data_ds=data[0::step,0::step]
    data_back[0::step,0::step]=data_ds
    coords_val = np.array(np.nonzero(~np.isnan(data_back))).T
    coords_out = np.array(np.nonzero(data_back)).T
    value = data_back[coords_val[:,0],coords_val[:,1]]
    return scipy.interpolate.griddata(coords_val,value,coords_out,method='cubic').reshape(sdata.shape)
#--------------------------------------------
def lerpgrd(sdata,condition):
    coords_val = np.array(np.nonzero(condition)).T
    coords_out = np.array(np.nonzero(sdata)).T
    value = sdata[coords_val[:,0],coords_val[:,1]]
    return scipy.interpolate.griddata(coords_val,value,coords_out,method='cubic').reshape(sdata.shape)
#--------------------------------------------
def mean_convoluted(image, m, n):
    kernel=np.full((m,n),1.0/(m*n))
    return scipy.signal.convolve2d(image, kernel, mode="same", boundary="symm")
#--------------------------------------------
def packet_mean(data):
    return (mean_convoluted(data,3,3)+mean_convoluted(data,5,5)+mean_convoluted(data,9,9)+mean_convoluted(data,21,21)+mean_convoluted(data,43,43)+mean_convoluted(data,86,86))/6.0
#--------------------------------------------
def dtm_rank(data,size):
    rmin = int(size[0]*size[1]*0.05)
    rmax = int(size[0]*size[1]*0.95)
    print "flter param:", rmin,rmax,size[0],size[1]
    rX = filters.rank_filter(data,rmin,(size[0],size[1]))
    rY = filters.rank_filter(data,rmin,(size[1],size[0]))
    rX = filters.rank_filter(rX,rmax,(size[0],size[1]))
    rY = filters.rank_filter(rY,rmax,(size[1],size[0]))

    return (rX+rY)/2.0
#--------------------------------------------
#--------------------------------------------
def dtm_rank2(data,size,tr):
    rmin = int(size[0]*size[1]*0.05)
    rmax = int(size[0]*size[1]*0.95)
    print "flter param:", rmin,rmax,size[0],size[1]
    rX = filters.rank_filter(data,rmin,(size[0],size[1]))
    rY = filters.rank_filter(data,rmin,(size[1],size[0]))
    rX = filters.rank_filter(rX,rmax,(size[0],size[1]))
    rY = filters.rank_filter(rY,rmax,(size[1],size[0]))
    diff = data-((rX+rY)/2.0)
    out = data[:,:]
    mask = diff>tr
    out[mask]=data[mask]-diff[mask]
    return out


fname = 'DSM_8x_RAW_flt.tif'
#fname = 'lenag.png'
oname = 'DSM_8x_RAW_flt_rank90_it5_t1.tif'
#oname = 'lenag_out.tif'
neighborhood_size = np.ones((5,5))
threshold = 15
nbands = 1
ds = gdal.Open(fname,gdal.GA_ReadOnly)
#data = scipy.misc.imread(fname)
nd=ds.GetRasterBand(1).GetNoDataValue()
data=ds.GetRasterBand(1).ReadAsArray().astype(np.float_)
data[data==-9999]=np.NAN
print "DTM rank filter"
#out=dtm_rank(data,(8,90))
#out=dtm_rank(data,(3,400))
for i in range(0,15):
    print "mean data", np.nanmean(data)
    out=dtm_rank2(data,(3,90),1.0)
    data=out
#out[out<0]=np.NAN
#out=local_diff(data,9)
out[out>300]=np.NAN
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
"""
ob=ods.GetRasterBand(2)
ob.WriteArray(out1,0,0)
ob=ods.GetRasterBand(3)
ob.WriteArray(out2,0,0)
ob=ods.GetRasterBand(4)
ob.WriteArray(out3,0,0)
"""

print "done"

ob=None
ods=None

