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
from pyparsing import (Word,Suppress,alphas,nums)
import datetime

def mtl_parser(mtl_file):

    pos1 = Word(alphas + "_" + nums + alphas)
    pos2 = Word(alphas + '"' + nums + "_" + "." + "-" + "+")
    meso = Suppress("=")
    parser = pos1 + meso + pos2

    mtl = open(mtl_file, mode="r")

    mtl_lib = {}
    group = ""
    for line in mtl:
        if len(line.split("=")) == 2:
            parser_line = parser.parseString(line)

            if parser_line[0] == "GROUP" and parser_line[1] != "L1_METADATA_FILE":
                group = parser_line[1]
                mtl_lib[parser_line[1]] = {}

            elif parser_line[0] != "GROUP" and parser_line[0] != "END_GROUP":
                mtl_lib[group][parser_line[0]] = parser_line[1]

    mtl.close()
    return mtl_lib
	

gdal.AllRegister()
gdal.UseExceptions()

fname = "test\L5177024_02420110602_B30.TIF"#sys.argv[1]
oname = "test\B30_dos.TIF"#os.path.splitext(fname)[0] + '_dos.tif'

nbands = 1
#ds = gdal.Open(fname,gdal.GA_Update)
ds = gdal.Open(fname,gdal.GA_ReadOnly)
nd=ds.GetRasterBand(1).GetNoDataValue()
if(nd==None):
    nd=0

data=ds.GetRasterBand(1).ReadAsArray().astype(np.float_)

mask = np.zeros(data.shape)
mask[data>0]=1
mask = ndimage.binary_erosion(mask,iterations=40)
mask = ndimage.binary_dilation(mask,iterations=40)
data[mask==0]=np.NAN

mtl=mtl_parser("L5177024_02420110602_MTL.txt")
gain=np.zeros(7)
bias=np.zeros(7)
sun_elevation=float(mtl['PRODUCT_PARAMETERS']['SUN_ELEVATION'])
sun_azimuth = float(mtl['PRODUCT_PARAMETERS']['SUN_AZIMUTH'])
date=mtl['PRODUCT_METADATA']['ACQUISITION_DATE']
for i in range(0,7):
    num=float(mtl['MIN_MAX_RADIANCE'][sorted(mtl['MIN_MAX_RADIANCE'].keys())[i]])- float(mtl['MIN_MAX_RADIANCE'][sorted(mtl['MIN_MAX_RADIANCE'].keys())[i+7]])
    den=float(mtl['MIN_MAX_PIXEL_VALUE'][sorted(mtl['MIN_MAX_PIXEL_VALUE'].keys())[i]])#- float(mtl['MIN_MAX_PIXEL_VALUE'][sorted(mtl['MIN_MAX_PIXEL_VALUE'].keys())[i+7]])
    gain[i]=num/den
    bias[i]=float(mtl['MIN_MAX_RADIANCE'][sorted(mtl['MIN_MAX_RADIANCE'].keys())[i+7]])#-(gain[i]*float(mtl['MIN_MAX_PIXEL_VALUE'][sorted(mtl['MIN_MAX_PIXEL_VALUE'].keys())[i+7]]))

date = str.split(mtl['PRODUCT_METADATA']['ACQUISITION_DATE'],"-")

band_prc=2

doy=datetime.date(int(date[0]),int(date[1]),int(date[2])).timetuple().tm_yday
d = (1.0-0.01672*np.cos(np.deg2rad(0.9856*doy-4)))
Tz = np.ones(7)#(0.85,0.85,0.85,0.91,0.91,-9999,0.91)
#ESUNL5 = (1957.0,1826.0,1554.0,1036.0,215.0,-9999,80.67)
ESUNL5 = (1957.0,1826.0,1558.618,1036.0,215.0,-9999,80.67)
hist=np.histogram(data[~np.isnan(data)],bins=255)
mm=np.where(hist[0]>(hist[0].sum()*0.01))
DnMin=hist[1][mm[0][0]-2]
den = 1.0/(ESUNL5[band_prc]*np.sin(np.deg2rad(sun_elevation))*Tz[band_prc])
L1 = 0.01*np.sin(np.deg2rad(sun_elevation))*Tz[band_prc]*ESUNL5[band_prc]/(np.pi*(d*d))
Lp = (DnMin*gain[band_prc]+bias[band_prc])-L1

#out = data*gain[band_prc]+bias[band_prc]
sun_rad = (np.sin(np.deg2rad(sun_elevation))*Tz[band_prc]*ESUNL5[band_prc])/(np.pi*(d*d))
rad_path = (DnMin*gain[band_prc]+bias[band_prc])-sun_rad*0.01
out = ((data*gain[band_prc]+bias[band_prc])-rad_path)/sun_rad


#out = localmaxmin(data,(h,w))

print "save result"
OutDataType=gdal.GDT_Float32
driver=gdal.GetDriverByName("Gtiff")
ods=driver.Create(oname,data.shape[1],data.shape[0],nbands,OutDataType)
ods.SetGeoTransform(ds.GetGeoTransform())
ods.SetProjection(ds.GetProjection())
ob=ods.GetRasterBand(1)
#ob=ds.GetRasterBand(1)
ob.SetNoDataValue(-9999)
ob.WriteArray(out,0,0)
ob=None
ods=None
ds=None

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
