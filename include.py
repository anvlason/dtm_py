import numpy as np
import scipy
from scipy import signal
import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters

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

