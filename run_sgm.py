import sys
from osgeo import gdal
from osgeo.gdalconst import *
import numpy as np
import numpy.ma as ma
import scipy.ndimage as ndimage
import os.path
import re
import cv2
import matplotlib.pyplot as plt

def parce_stat(fname):
    data = np.loadtxt(fname, dtype=np.float_,skiprows=1,comments="#")
    dx = data[:,2]-data[:,0]
    max_disp = abs(np.min(dx))+abs(np.max(dx))
#    shift = np.minimum(abs(np.min(dx)),abs(np.max(dx)))
    max_h = (np.max(data[:,4]))
    min_h = (np.min(data[:,4]))
    bias,gain = get_scale(fname)
    shift = int(bias/gain+0.5)
#    print "max_disp = %f"%(max_disp)
#    print "min par = %f"%(np.min(dx))
#    print "max par = %f"%(np.max(dx))
#    print "max height = %f"%(np.max(data[:,4]))
#    print "min height = %f"%(np.min(data[:,4]))
    return shift,max_disp,min_h,max_h,bias,gain

def get_scale(fname):
   f = open(fname,"rb")

   lines = f.readlines()
#   print lines[-1]
   m = (re.findall(r"[-+]?\d*\.\d+|\d+",lines[-1]))
   f.close()
   return float(m[0]), float(m[1])

def to_byte(name,oname,size):
    ds = gdal.Open(name,gdal.GA_ReadOnly)
    data=ds.GetRasterBand(1).ReadAsArray().astype(np.float)
    ds = None
    smin=np.min(data[data!=0])
    smax=np.max(data[data!=0])
    osize = [data.shape[0]/size+1,data.shape[1]/size+1]
    OutDataType=gdal.GDT_Byte
    onodata=0
#Create output
    driver=gdal.GetDriverByName("Gtiff")
    ods=driver.Create(oname,osize[1],osize[0],1,OutDataType)
    ob=ods.GetRasterBand(1)
    ob.SetNoDataValue(onodata)
#    cdata=(cdata-np.min(data))*(255.0/(np.max(data)-np.min(data)))
    scale = 255.0/(smax-smin)
    ob.WriteArray((data[::size,::size]-smin)*scale,0,0)
    ob = None
    ods = None

def to_byte_flip(name,oname,size):
    ds = gdal.Open(name,gdal.GA_ReadOnly)
    data=ds.GetRasterBand(1).ReadAsArray().astype(np.float)
    ds = None
    smin=np.min(data[data!=0])
    smax=np.max(data[data!=0])
    osize = [data.shape[0]/size+1,data.shape[1]/size+1]
    OutDataType=gdal.GDT_Byte
    onodata=0
#Create output
    driver=gdal.GetDriverByName("Gtiff")
    ods=driver.Create(oname,osize[1],osize[0],1,OutDataType)
    ob=ods.GetRasterBand(1)
    ob.SetNoDataValue(onodata)
#    cdata=(cdata-np.min(data))*(255.0/(np.max(data)-np.min(data)))
    scale = 255.0/(smax-smin)
    ob.WriteArray((np.fliplr(data[::size,::size])-smin)*scale,0,0)
    ob = None
    ods = None

def scale_to_height(name,h_scale,h_offset,p_offset,size,h_min,h_max,perc=0.1,fill=-9999.0):
    ds = gdal.Open(name,gdal.GA_ReadOnly)
    data=ds.GetRasterBand(1).ReadAsArray().astype(np.float)
    ndmask = data==-16
    odata = data.copy()
    odata=(((odata)/16-p_offset)*size)
    odata = odata*float(h_scale)+float(h_offset)
    tr =(h_max-h_min)*perc
    print "tr=%f"%tr
    print "h_diff=%f"%(h_max-h_min)
    odata[odata<(h_min-tr)]=fill
    odata[odata>(h_max+tr)]=fill
#    odata[odata<(h_min-10)]=fill
#    odata[odata>(h_max+100)]=fill
    odata[ndmask]=fill
    ds =None
    del data, ndmask
    return odata


def get_background(left,right):
    lds = gdal.Open(left,gdal.GA_ReadOnly)
    tdata=lds.GetRasterBand(1).ReadAsArray().astype(np.float)
#    print tdata.shape
    lmask = tdata==0
    del(tdata)
    del(lds)
#print lmask.shape
    rds = gdal.Open(right,gdal.GA_ReadOnly)
    tdata=rds.GetRasterBand(1).ReadAsArray().astype(np.float)
    rmask = tdata==0
    del(tdata)
    del(rds)
    return lmask+rmask

def write_dsm(oname,data,nodata=-9999):    
    OutDataType=gdal.GDT_Float32
    driver=gdal.GetDriverByName("Gtiff")
    nbands=1
    ods=driver.Create(oname,data.shape[1],data.shape[0],nbands,OutDataType)
    ob=ods.GetRasterBand(1)
    ob.SetNoDataValue(nodata)
    ob.WriteArray(data,0,0)
    ob = None
    ods= None

def write_dsm_flip(oname,data,nodata=-9999):    
    OutDataType=gdal.GDT_Float32
    driver=gdal.GetDriverByName("Gtiff")
    nbands=1
    ods=driver.Create(oname,data.shape[1],data.shape[0],nbands,OutDataType)
    ob=ods.GetRasterBand(1)
    ob.SetNoDataValue(nodata)
    ob.WriteArray(np.fliplr(data),0,0)
    ob = None
    ods= None

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

def extract_labels(data,min_size=500):
    label_im, nb_labels = ndimage.label(data)
    sizes = ndimage.sum(data,label_im,range(nb_labels+1))
    mask_size = sizes < min_size
    remove_pixel = mask_size[label_im]
    label_im[remove_pixel] = 0
    labels = np.unique(label_im)
    label_im = np.searchsorted(labels, label_im)
    labels = np.unique(label_im)
    return label_im

def watermask(left,minsize=500):
    lds = gdal.Open(left,gdal.GA_ReadOnly)
    tdata=lds.GetRasterBand(1).ReadAsArray().astype(np.uint8)
    del(lds)
    meanshift = cv2.pyrMeanShiftFiltering(cv2.cvtColor(tdata.astype(np.uint8),cv2.COLOR_GRAY2BGR),1,30)[:,:,0]
    del(tdata)
    threshold = np.percentile(meanshift[meanshift>5],10)
    return extract_labels(np.logical_and(meanshift>5,meanshift<=threshold),minsize)>0


#oname, ext = os.path.splitext(os.path.basename(sys.argv[1]))
#dir = os.path.dirname(sys.argv[1])
gdal.AllRegister()
gdal.UseExceptions()

left = sys.argv[1]
right = sys.argv[2]
stat = sys.argv[3]
size = int(sys.argv[4])
size = np.maximum(1,size)
fill_holes = 0
mk_water = 0
mk_dsm = 1
mk_scale=1
mk_disp=1

olname = os.path.splitext(left)[0] + "_byte_%d.tif"%(size)
orname = os.path.splitext(right)[0] + "_byte_%d.tif"%(size)
odname = os.path.splitext(left)[0] + "_right_disparity_%d.bin"%(size)
odsmname = os.path.splitext(left)[0] + "_right_dsm_%d.tif"%(size)

invert=1
offset,max_disp,h_min,h_max,h_offset,h_scale = parce_stat(stat)
print offset,max_disp,h_min,h_max

#h_offset, h_scale = get_scale(stat)
print h_offset, h_scale

if(mk_scale!=0):
    to_byte(left,olname,size)
    to_byte(right,orname,size)

confidence = 48#int(((h_max-h_min)/abs(float(h_scale)))+32.5)/size
print confidence
s_p_offset = int(offset/size)#+confidence)
s_max_disp = int(((max_disp+confidence)/size)/16)*16

if(mk_disp!=0):
    os.system("stereo-example-sample.exe -P1=100 -P2=1000 -b=5 -d=%d -rs=%d %s %s %s"%(s_max_disp,s_p_offset,olname,orname,odname))
#    os.system("stereo-example-sample.exe -P1=8 -P2=80 -b=2 -w=5 -k=3 -d=%d -rs=%d %s %s %s"%(s_max_disp,s_p_offset,olname,orname,odname))
s_p_offset=s_p_offset*invert+6
h_scale=h_scale*invert
if(mk_dsm!=0):
    odata = scale_to_height(odname,h_scale,h_offset,s_p_offset,size,h_min,h_max,perc=0.2)
    bmask = get_background(olname,orname)
    ndmask = ndimage.morphology.binary_fill_holes(odata==-9999)
    odata[bmask]=np.nan
    odata[ndmask]=np.nan
    if(mk_water==1):
        wmask = watermask(olname,50)
        odata[wmask]=-50
    #plt.imshow(odata)
    #plt.show()
    if(fill_holes==1):
        odata = fill(odata)
    odata[bmask]=-100
    write_dsm(odsmname,odata)

exit(0)
