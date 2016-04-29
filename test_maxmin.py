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

def local_dif(sdata,size):

    localmin = filters.minimum_filter(sdata, size)
    localmax = filters.maximum_filter(sdata, size)
    return (localmax-localmin)

def lerp(sdata,condition):
    xx,yy = np.meshgrid(np.arange(sdata.shape[1]),np.arange(sdata.shape[0]))
    xym = np.vstack( (np.ravel(xx[condition]), np.ravel(yy[condition])) ).T
    values=np.ravel(sdata[:,:][condition])
    interp=scipy.interpolate.LinearNDInterpolator(xym,values)
    return interp(np.ravel(xx), np.ravel(yy)).reshape( xx.shape )

def localmin(sdata,size,threshold):
    localmin = filters.minimum_filter(sdata, size)
    localdif = sdata-localmin
    with np.errstate(invalid='ignore'):
        return (localdif < threshold)
#        return np.where(localdif < threshold)

def lerpNANdwn(sdata,step):
    data_back=np.zeros(sdata.shape)
    data_back[:,:]=np.NAN
    data_ds=data[0::step,0::step]
    data_back[0::step,0::step]=data_ds
    coords_val = np.array(np.nonzero(~np.isnan(data_back))).T
    coords_out = np.array(np.nonzero(data_back)).T
    value = data_back[coords_val[:,0],coords_val[:,1]]
    return scipy.interpolate.griddata(coords_val,value,coords_out,method='cubic').reshape(sdata.shape)

def lerpgrd(sdata,condition):
    coords_val = np.array(np.nonzero(condition)).T
    coords_out = np.array(np.nonzero(sdata)).T
    value = sdata[coords_val[:,0],coords_val[:,1]]
    return scipy.interpolate.griddata(coords_val,value,coords_out,method='cubic').reshape(sdata.shape)
	
def localmaxmin(sdata,size):
    localmin = filters.minimum_filter(sdata, size)
    localmax = filters.maximum_filter(sdata, size)
    with np.errstate(invalid='ignore'):
        return (localmin - localmax)

h = int(sys.argv[1])
w = int(sys.argv[2])

fname = fname = sys.argv[3]
oname = os.path.splitext(fname)[0] + '_maxmin.tif'

nbands = 1
ds = gdal.Open(fname,gdal.GA_ReadOnly)
#data = scipy.misc.imread(fname)
nd=ds.GetRasterBand(1).GetNoDataValue()
data=ds.GetRasterBand(1).ReadAsArray().astype(np.float_)
data[data==nd]=np.NAN

#out = localmaxmin(data,(h,w))
out = ndimage.gaussian_gradient_magnitude(data,1)


print "save result"
OutDataType=gdal.GDT_Float32
driver=gdal.GetDriverByName("Gtiff")
ods=driver.Create(oname,data.shape[1],data.shape[0],nbands,OutDataType)
ob=ods.GetRasterBand(1)
ob.SetNoDataValue(nd)
ob.WriteArray(out,0,0)
ob=None
ods=None

"""
__END__

mask=(data==nd)
data[mask]=np.NAN
mask=(data==-9999)
data[mask]=np.NAN
print "run step 1"
step = 10

#local minima
data_min = filters.minimum_filter(data, 3)
data_ds=data_min[0::step,0::step]
#do something with data_ds
data_ds=filters.minimum_filter(data_ds,3)
#upscale back
data_back=np.zeros(data.shape)
data_back[:,:]=np.NAN
data_back[0::step,0::step]=data_ds
coords_val = np.array(np.nonzero(~np.isnan(data_back))).T
coords_out = np.array(np.nonzero(data_back)).T
value = data_back[coords_val[:,0],coords_val[:,1]]

out_lerp = scipy.interpolate.griddata(coords_val,value,coords_out,method='cubic').reshape(data.shape)

data_back=None
data_ds=None
coords_val=None
coords_out=None
value=None


print "lerp fin"
diff = data - out_lerp
out_lerp=None

rm_mask = (diff>1)
step=5
data_back=np.zeros(data.shape)
data_back[:,:]=np.NAN
data_ds=data[0::step,0::step]
data_back[0::step,0::step]=data_ds
data_back[rm_mask]=np.NAN
coords_val = np.array(np.nonzero(~np.isnan(data_back))).T
coords_out = np.array(np.nonzero(data_back)).T
value = data_back[coords_val[:,0],coords_val[:,1]]

out_lerp = scipy.interpolate.griddata(coords_val,value,coords_out,method='cubic').reshape(data.shape)


#__END__
#out_lerp = scipy.interpolate.griddata(coords_val,value,coords_out,method='cubic').reshape(data.shape)
#lerp 33
#mask1=~np.isnan(data_copy)
#xx,yy = np.meshgrid(np.arange(data_copy.shape[1]),np.arange(data.shape[0]))
#xym = np.vstack( (np.ravel(xx[mask1]), np.ravel(yy[mask1])) ).T
#data0=np.ravel(data_copy[:,:][mask1])
#interp0=scipy.interpolate.LinearNDInterpolator(xym,data0)
#result0 = interp0(np.ravel(xx), np.ravel(yy)).reshape( xx.shape )

def fill(data, invalid=None):
    """
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
"""
    if invalid is None: invalid = np.isnan(data)

    ind = ndimage.distance_transform_edt(invalid, 
                                    return_distances=False, 
                                    return_indices=True)
    return data[tuple(ind)]

#data_copy1=fill(data_copy)



#save
print "save result"
OutDataType=gdal.GDT_Float32
driver=gdal.GetDriverByName("Gtiff")
ods=driver.Create(oname,data.shape[1],data.shape[0],nbands,OutDataType)
ob=ods.GetRasterBand(1)
ob.SetNoDataValue(nd)
ob.WriteArray(out_lerp,0,0)
#ob=ods.GetRasterBand(2)
#ob.WriteArray(out_lerp,0,0)

ob=None
ods=None

"""
