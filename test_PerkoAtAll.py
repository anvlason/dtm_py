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

def mean_convoluted(image, m, n):
    kernel=np.full((m,n),1.0/(m*n))
    return scipy.signal.convolve2d(image, kernel, mode="same", boundary="symm")

def packet_mean(data):
    data3 = mean_convoluted(data,3,3)
    data6 = mean_convoluted(data3,3,3)
    data12 = mean_convoluted(data6,3,3)
    data24 = mean_convoluted(data12,3,3)
    data48 = mean_convoluted(data24,3,3)
    data86 = mean_convoluted(data48,3,3)
    return (data3+data6+data12+data24+data48+data86)/6.0
#    return mean_convoluted(data,11,11)
#    return (mean_convoluted(data,3,3)+mean_convoluted(data,5,5)+mean_convoluted(data,9,9)+mean_convoluted(data,21,21)+mean_convoluted(data,43,43)+mean_convoluted(data,86,86))/6.0


fname = 'terrassa_clip.tif'
#fname = 'lenag.png'
oname = 'terrassa_clip_out.tif'
#oname = 'lenag_out.tif'
#neighborhood_size = np.ones((5,5))
#threshold = 15
nbands = 2
ds = gdal.Open(fname,gdal.GA_ReadOnly)
#data = scipy.misc.imread(fname)
nd=ds.GetRasterBand(1).GetNoDataValue()
data=ds.GetRasterBand(1).ReadAsArray().astype(np.float_)
#energy=ds.GetRasterBand(2).ReadAsArray().astype(np.float_)

#set low correlation to NAN
#data[np.where(energy > 0.4)]=np.NAN

"""
filt_size = 5
ps = 1.4
maxit = 3

max_slope = np.deg2rad(30)
max_dh = np.math.tan(max_slope)*ps*filt_size

#cm = np.zeros(energy.shape)
#cm[np.where(energy>0.4)]=1
#filled=fill(data,cm)

#find local minimum
lm = localmin(data,21,2)
#lp = lerp(data,lm)
lp = lerpgrd(data,lm)
dif = data-lp
with np.errstate(invalid='ignore'):
    out = lerpgrd(data,(dif < 2))
#    out = lerp(data,np.where(dif < 2))

out0 = out[:,:]

for i in range(0,maxit):
    print "iteration: ", i
    lm = localmin(out,21,2)
#    lp = lerp(out,lm)
    lp = lerpgrd(out,lm)
    dif = out-lp
    with np.errstate(invalid='ignore'):
        out = lerpgrd(out,(dif < 2))        
#        out = lerp(out,np.where(dif < 2))

#rmbad = fill(data)
#rmbad = lerp(data,np.where(data!=np.NAN))
rmbad = lerpNANdwn(data,1)        
gauss = filters.gaussian_filter(rmbad,5)
gauss1 = filters.gaussian_filter(out0,5)
"""
ps=1.4
max_slope = np.deg2rad(5)
max_dh = np.math.tan(max_slope)*ps*2
print "max_dh=", max_dh

#oDSMm = mean_convoluted(data,8,91)#filters.median_filter(data,size=(8,91))
#DSMminX = filters.minimum_filter(data,size=(4,8))
#DSMminY = filters.minimum_filter(data,size=(8,4))
#DSMmin = (DSMminX+DSMminY)/2.0
#DSMdh = data - DSMmin
#DSMs= filters.gaussian_filter(data,5)
#LS = data - DSMs
#NG1 = np.ones(data.shape)
#NG1[DSMdh>3]=0
#LS = np.rad2deg(np.arctan(local_dif(data,2)/(ps*2)))
#LS2 = np.rad2deg(np.arctan(local_dif(data,8)/(ps*4)))
#NG2 = np.zeros(data.shape)
#NG2[LS<max_dh]=1
#8x8
#lm=filters.minimum_filter(data,3)
out=data[:,:]
print "mean source=", np.mean(out)
#packet = packet_mean(out)#(mean_convoluted(data,3,3)+mean_convoluted(data,5,5)+mean_convoluted(data,9,9)+mean_convoluted(data,21,21)+mean_convoluted(data,43,43)+mean_convoluted(data,86,86))/6.0
"""
gauss8 = data-mean_convoluted(data,3,3)#filters.gaussian_filter(lm,25,truncate=2) #(w - 1)/2 = int(truncate*sigma + 0.5)#trunc=sigma/((w-1)/2)+0.5
#16x16
gauss16 = data-mean_convoluted(data,5,5)#filters.gaussian_filter(lm,20,truncate=2) #(w - 1)/2 = int(truncate*sigma + 0.5)#trunc=sigma/((w-1)/2)+0.5
#32x32
gauss32 = data-mean_convoluted(data,9,9)#filters.gaussian_filter(lm,15,truncate=2) #(w - 1)/2 = int(truncate*sigma + 0.5)#trunc=sigma/((w-1)/2)+0.5
#64x64
gauss64 = data-mean_convoluted(data,21,21)#filters.gaussian_filter(lm,10,truncate=2) #(w - 1)/2 = int(truncate*sigma + 0.5)#trunc=sigma/((w-1)/2)+0.5
#64x64
gauss128 = data-mean_convoluted(data,43,43)#filters.gaussian_filter(lm,5,truncate=2) #(w - 1)/2 = int(truncate*sigma + 0.5)#trunc=sigma/((w-1)/2)+0.5
#64x64
gauss256 = data-mean_convoluted(data,86,86)#filters.gaussian_filter(lm,2.5,truncate=2) #(w - 1)/2 = int(truncate*sigma + 0.5)#trunc=sigma/((w-1)/2)+0.5
merge = (gauss8+gauss16+gauss32+gauss64+gauss128+gauss256)/6.0
"""
#maskk=out-packet
#out[maskk>2]=packet[maskk>2]
maxit = 30

tr = 0.5#(5.0,4.0,3.0,2.5,2.0)

for it in range(0,maxit):
    print "itrration ", it+1
    packet = packet_mean(out)
    maskk=out-packet
#    out[maskk>tr[it]]=np.NAN
#    maskk[maskk>tr[it]]=np.NAN
    minf=filters.rank_filter(out,45,11)#filters.minimum_filter(out,11)
    minf=filters.gaussian_filter(minf,3)
    out[maskk>tr]=minf[maskk>tr]
#    out[maskk>tr]=filters.gaussian_filter(out[maskk>tr],3)
#    out[maskk>tr[it]]=minf[maskk>tr[it]]
#    out=fill(out)
#    out[maskk>tr[it]]=packet[maskk>tr[it]]
    print "tr value =", tr#[it]
    print "mean value =", np.mean(out)
    
#mm=np.zeros(maskk.shape)
#mm[maskk>1.2]=1
#open_square = ndimage.binary_opening(mm)
#reconstruction = ndimage.binary_fill_holes(mm)
#reconstruction=fill(out,


print "save result"
OutDataType=gdal.GDT_Float32
driver=gdal.GetDriverByName("Gtiff")
ods=driver.Create(oname,data.shape[1],data.shape[0],nbands,OutDataType)
ob=ods.GetRasterBand(1)
ob.SetNoDataValue(nd)
ob.WriteArray(maskk,0,0)
ob=ods.GetRasterBand(2)
ob.WriteArray(out,0,0)
"""
ob=ods.GetRasterBand(3)
ob.WriteArray(packet,0,0)
ob=ods.GetRasterBand(4)
ob.WriteArray(maskk,0,0)
ob=ods.GetRasterBand(5)
ob.WriteArray(out,0,0)
ob=ods.GetRasterBand(6)
ob.WriteArray(gauss64,0,0)
ob=ods.GetRasterBand(7)
ob.WriteArray(gauss128,0,0)
ob=ods.GetRasterBand(8)
ob.WriteArray(gauss256,0,0)
ob=ods.GetRasterBand(9)
ob.WriteArray(merge,0,0)
"""
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
