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



fname = 'terrassa.tif'
#fname = 'lenag.png'
oname = 'terrassa_out.tif'
#oname = 'lenag_out.tif'
neighborhood_size = np.ones((5,5))
threshold = 15
nbands = 2
ds = gdal.Open(fname,gdal.GA_ReadOnly)
#data = scipy.misc.imread(fname)
nd=ds.GetRasterBand(1).GetNoDataValue()
nd=-9999
data=ds.GetRasterBand(1).ReadAsArray().astype(np.float_)
energy=ds.GetRasterBand(2).ReadAsArray().astype(np.float_)
mask=(data==nd)
data[mask]=np.NAN


def detect_local_minima(arr):
    # http://stackoverflow.com/questions/3684484/peak-detection-in-a-2d-array/3689710#3689710
    """
    Takes an array and detects the troughs using the local maximum filter.
    Returns a boolean mask of the troughs (i.e. 1 when
    the pixel's value is the neighborhood maximum, 0 otherwise)
    """
    # define an connected neighborhood
    # http://www.scipy.org/doc/api_docs/SciPy.ndimage.morphology.html#generate_binary_structure
    neighborhood = ndimage.morphology.generate_binary_structure(len(arr.shape),2)
    # apply the local minimum filter; all locations of minimum value 
    # in their neighborhood are set to 1
    # http://www.scipy.org/doc/api_docs/SciPy.ndimage.filters.html#minimum_filter
    local_min = (filters.minimum_filter(arr, footprint=neighborhood)==arr)
    # local_min is a mask that contains the peaks we are 
    # looking for, but also the background.
    # In order to isolate the peaks we must remove the background from the mask.
    # 
    # we create the mask of the background
    background = (arr==0)
    # 
    # a little technicality: we must erode the background in order to 
    # successfully subtract it from local_min, otherwise a line will 
    # appear along the background border (artifact of the local minimum filter)
    # http://www.scipy.org/doc/api_docs/SciPy.ndimage.morphology.html#binary_erosion
    eroded_background = ndimage.morphology.binary_erosion(
        background, structure=neighborhood, border_value=1)
    # 
    # we obtain the final mask, containing only peaks, 
    # by removing the background from the local_min mask
    detected_minima = local_min - eroded_background
    return np.where(detected_minima)       

def local_minima(array2d):
    return ((array2d <= np.roll(array2d,  1, 0)) &
            (array2d <= np.roll(array2d, -1, 0)) &
            (array2d <= np.roll(array2d,  1, 1)) &
            (array2d <= np.roll(array2d, -1, 1)))

data_scaled=data#[0::5,0::5]
#data_min = data_scaled
#mask_min = local_minima(data_scaled)
#data_scaled[~mask_min] = np.NAN

#remove small holes
maxit = 3
for it in range(0,maxit):
    data_open = ndimage.grey_closing(data_scaled,size=(3,3))
print "small holes filled"
#data_open = ndimage.grey_opening(data_scaled,size=(3,3))
data_open = filters.rank_filter(data_open,3,3)
#data_open = filters.gaussian_filter(data_open,sigma=5/2.0)
#data_open[np.isnan(data_open)]=-9999

#zfy = float(data.shape[0])/data_open.shape[0]
#zfx = float(data.shape[1])/data_open.shape[1]

#data_out = scipy.misc.imresize(data_open,(data.shape[0],data.shape[1]),interp='bilinear').astype(np.float_)
#data_out=ndimage.interpolation.zoom(data_open,(zfy,zfx))

#local_min v2
#set bad_matches to nan
#bad_matches=energy>0.7
#data[bad_matches]=np.NAN
#resample 5x down
data_dwn=np.zeros(data.shape)
data_dwn[:,:]=np.NAN
data_dwn[0::10,0::10]=data[0::10,0::10]
#zfy = float(data.shape[0])/data_dwn.shape[0]
#zfx = float(data.shape[1])/data_dwn.shape[1]
#find local minima
valid_mask = detect_local_minima(data_dwn)
coords = valid_mask
coords_grid = np.array(np.nonzero(data)).T
values = data_dwn[valid_mask[0],valid_mask[1]]
data_lerp = scipy.interpolate.griddata(coords,values,coords_grid,method='linear')
data_lerp = data_lerp.reshape(data.shape)
data_up=data_lerp
#back scale 5x
#data_lerp[np.isnan(data_lerp)]=-9999
#data_up=ndimage.interpolation.zoom(data_lerp,(zfy,zfx))
#data_up=scipy.interpolate.griddata(coords,values,coords_grid,method='linear')

#local_min V1
#valid_mask = local_minima(data)
#coords = np.array(np.nonzero(valid_mask)).T
#values = data[valid_mask]
#it = scipy.interpolate.LinearNDInterpolator(coords,values,fill_value=-9999)
#data_lerp=it(list(np.ndindex(data.shape))).reshape(data.shape)

#data_lerp[valid_mask]=0
data_out=data_open



OutDataType=gdal.GDT_Float32
driver=gdal.GetDriverByName("Gtiff")
ods=driver.Create(oname,data.shape[1],data.shape[0],nbands,OutDataType)
ob=ods.GetRasterBand(1)
ob.SetNoDataValue(nd)
ob.WriteArray(data_out,0,0)
ob=ods.GetRasterBand(2)
ob.WriteArray(data_up,0,0)

ob=None
ods=None

"""
__END__


#data_min = filters.minimum_filter(data, neighborhood_size)
#data_max = filters.maximum_filter(data, footprint=neighborhood_size)
#data_min = filters.minimum_filter(data, footprint=neighborhood_size)
#data_out = data_max-data_min
#data_med = filters.median_filter(data,3)
#data_max = filters.maximum_filter(data_med, neighborhood_size)
#data_min = filters.minimum_filter(data_med, neighborhood_size)
#data_gauss = filters.gaussian_filter(data,3)
#mask=(data_sm<0)
#data_sm[mask] = -9999
#data_med = filters.median_filter(data,3)
#data_rank = filters.rank_filter(data,30,9)
#data_rank_1 = filters.rank_filter(data,25,9)
#data_rank_1_sm = filters.mean(data_rank_1,3)

#data_del = ndimage.morphology.grey_dilation(data_med,6)
#data_del = ndimage.morphology.grey_erosion(data_del,6)
#data_min = filters.minimum_filter(data_del, 8)
#data_diff = data_med-data_min
#maxima = (data == data_max)
#data_min = filters.minimum_filter(data, neighborhood_size)
#data_min = filters.minimum_filter(data_min, 1)
#diff = ((data_max - data_min) > threshold)
#maxima[diff == 0] = 0

#labeled, num_objects = ndimage.label(maxima)
#slices = ndimage.find_objects(labeled)
#x, y = [], []
#for dy,dx in slices:
#    x_center = (dx.start + dx.stop - 1)/2
#    x.append(x_center)
#    y_center = (dy.start + dy.stop - 1)/2    
#    y.append(y_center)
#
#plt.imshow(data)
#plt.savefig('RImHW.png_data.png', bbox_inches = 'tight')
#
#plt.autoscale(False)
#plt.plot(x,y, 'ro')
#plt.savefig('RImHW.png_result.png', bbox_inches = 'tight')
#
#interpolation
#valid_mask = ~np.isnan(data)
#coords = np.array(np.nonzero(valid_mask)).T
#values = data[valid_mask]
#data_lerp = scipy.interpolate.griddata(coords,values,(data.shape[0],data.shape[1]),method='cubic')

#local window
def mean_convoluted(image, N):
    n=2*N+1
    kernel=np.full((n,n),1.0/(n**2))#np.ones(2*N+1,2*N+1)*(1/((2*N+1)**2))
    oim = scipy.signal.convolve2d(image, kernel, mode="same")
#    oim = ndimage.convolve(image, kernel)
    return oim
                                 
# kernel=np.full((3,3),1/9.0)
# ndimage.convolve(data, kernel)
def std_convoluted(image, N):
    im = np.array(image, dtype=float)
    im2 = im**2
    ones = np.ones(im.shape)
    kernel = np.ones((2*N+1, 2*N+1))
    s = scipy.signal.convolve2d(im, kernel, mode="same")
    s2 = scipy.signal.convolve2d(im2, kernel, mode="same")
    ns = scipy.signal.convolve2d(ones, kernel, mode="same")

    return np.sqrt((s2 - s**2 / ns) / ns)

#data_sd = std_convoluted(data,1)
#data_sd = mean_convoluted(data_sm,3)
#data_sd1 = mean_convoluted(data,3)
#data_sd = std_convoluted(data,21)
#oDSMm = mean_convoluted(data,3)
#oDSMDiff = data - oDSMm
#oDSMs = filters.gaussian_filter(data,3)
#oDSMsDiff = oDSMs - oDSMm

#x,y = np.gradient(data_gauss)
#slope_gauss = np.rad2deg(np.pi/2. - np.arctan(np.sqrt(x*x + y*y)))

#x,y = np.gradient(data)
#slope = np.rad2deg(np.pi/2. - np.arctan(np.sqrt(x*x + y*y)))

#slope_diff = slope-slope_gauss

#oMinNeigh = filters.minimum_filter(data, 60)
#dHeightDiff = data - oMinNeigh
data_rank = filters.rank_filter(data_lerp,3,3)
#data_mean = mean_convoluted(data,1)
OutDataType=gdal.GDT_Float32
#OutDataType=gdal.GDT_Byte
driver=gdal.GetDriverByName("Gtiff")
ods=driver.Create(oname,data.shape[1],data.shape[0],nbands,OutDataType)
ob=ods.GetRasterBand(1)
ob.SetNoDataValue(nd)
#ob.WriteArray(slope_gauss,0,0)
#ob.WriteArray(data_out,0,0)
ob.WriteArray(data_rank,0,0)
#ob.WriteArray(data_rank_l_sm,0,0)
ob=ods.GetRasterBand(2)
#oMinNeigh = filters.minimum_filter(data_rank, 60)
#dHeightDiff = data - oMinNeigh
data_med40 = filters.median_filter(data_rank,20)
ob.WriteArray(data_med40,0,0)
#ob.WriteArray(slope,0,0)
#ob.WriteArray(data_min,0,0)
ob=ods.GetRasterBand(3)
#oMinNeigh = filters.minimum_filter(data_rank, 5)
#dHeightDiff = data - oMinNeigh
data_med4 = filters.median_filter(data_rank,2)
ob.WriteArray(data_med4,0,0)
#ob.WriteArray(data_sm,0,0)
ob=ods.GetRasterBand(4)
#oMinNeigh = filters.minimum_filter(data_rank, 3)
dHeightDiff = data_med4 - data_med40

ob.WriteArray(dHeightDiff,0,0)

#ob=ods.GetRasterBand(5)
#ob.WriteArray(data_del,0,0)
#ob=ods.GetRasterBand(6)
#ob.WriteArray(data_diff,0,0)

ob=None
ods=None
"""
