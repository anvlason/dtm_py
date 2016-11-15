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
import cv2
import time


def geodesic_dilation(marker,mask):
    """ Perform geodesic dilation based on algorithm
        on p. 185 of Soille (2002).
    
    """
    # Compute the size for the filter based on the shape
    # of the marker array
    mshape = len(marker.shape)
    msize = (3,) * mshape
    
    marker_dilation = ndimage.maximum_filter(marker, size=msize)
    return np.where(mask <= marker_dilation, mask, marker_dilation)

def recon_by_dilation(marker,mask,max_iter=10000):
    """ Iterate over geodesic dilation operations
        until dilation(j+1) = dilation(j).
        Perform Geodesic dilation based on
        algorithm on p. 190-191, P. Soille, 2002. 
        This can be referenced as:
          R^delta_mask(marker)
    """
    print "Start reconstruction"
    dilation_i = marker
    for i in xrange(max_iter):
        sys.stdout.write("Iteration %d   \r"%(i+1))
        sys.stdout.flush()
        dilation_i1 = geodesic_dilation(dilation_i,mask)
        if i > 0 and np.sum(np.equal(dilation_i.ravel(),dilation_i1.ravel())) == dilation_i.size:
            break     
        else:
            dilation_i = dilation_i1.copy()
    del dilation_i1
    print "Done. Total iterations: %d"%i    
    return dilation_i

def gdal_write(oname,data,nodata=-9999):    
    OutDataType=gdal.GDT_Float32
    driver=gdal.GetDriverByName("Gtiff")
    nbands=1
    ods=driver.Create(oname,data.shape[1],data.shape[0],nbands,OutDataType)
    ob=ods.GetRasterBand(1)
    ob.SetNoDataValue(nodata)
    ob.WriteArray(data,0,0)
    ob = None
    ods= None

def gdal_read(fname,band=1):
    ds = gdal.Open(fname,gdal.GA_ReadOnly)
    return ds.GetRasterBand(band).ReadAsArray().astype(np.float)

def calc_LRV(data,size=(3,3),tmax = 1000):
    min_area = ndimage.minimum_filter(data,size)
    max_area = ndimage.maximum_filter(data,size)
    out = max_area-min_area
    out[out>tmax]=0
    return out

def extract_contour(mask, iteration=1):
    erode = ndimage.morphology.binary_erosion(mask,iterations=iteration)
    out = np.copy(mask)
    out[erode==1]=0
    return out

def extract_labels(data,min_size=10):
    label_im, nb_labels = ndimage.label(data)
    sizes = ndimage.sum(data,label_im,range(nb_labels+1))
    mask_size = sizes < min_size
    remove_pixel = mask_size[label_im]
    label_im[remove_pixel] = 0
    labels = np.unique(label_im)
    label_im = np.searchsorted(labels, label_im)
    labels = np.unique(label_im)
    return label_im

def reg_median_cont1(data,label_im):
    print "Start regional statistic calculation"
    label_con = extract_contour(label_im)
    out = np.array(label_im,dtype=np.float)
    labels = np.unique(label_im)
    for lab in labels:
        if( lab==0 ): continue
        try:
#            print "n %d from %d"%(lab,len(labels))
            slice_x, slice_y = ndimage.find_objects(label_im==lab)[0]
        except IndexError:
            print ("Bad index: "%lab)
            continue
#        print lab
        roi_data = data[slice_x, slice_y]
        tmask = label_im==lab
        cmask = label_con==lab
        roi_lab = tmask[slice_x, slice_y]
        roi_con = cmask[slice_x, slice_y]
        roi_out = out[slice_x, slice_y]
        mean = np.ma.median(np.ma.array(roi_data,mask=~roi_con))
        roi_out[roi_lab] = mean
    print "Done. Total regions: %d"%lab
    return out

def filter_none_ground(data,lrv,h,tsd=3,t=2,nd=-9999):
    ndmask = data==nd
    mask = np.copy(data)
    data = None
    marker = mask[:]-h
    marker[ndmask]=nd
    imrec=recon_by_dilation(marker,mask)
    print "Mask & Marker means: %f %f"%(np.mean(mask[mask!=nd]),np.mean(marker[mask!=nd]))
    nDSM0 = mask[:]-imrec[:]
    print "Clip threshold %f std %f"%(np.std(nDSM0)*tsd,np.std(nDSM0))
#    lab = extract_labels(nDSM0 > np.std(nDSM0)*tsd)
    lab = extract_labels(nDSM0 > tsd)
    print "Total regions: %d"%len(lab)
    reg = reg_median_cont1(lrv,lab)
    print "Regions mean: %f"%np.mean(reg)
    mask[reg>t]=nd
    return mask#, imrec#(imrec, nDSM0, lab, reg, mask)

def reduce(data,factor):
    osize = [data.shape[0]/factor+1,data.shape[1]/factor+1]
    out = np.zeros(osize,dtype=np.float)
    out = data[::factor,::factor]
    return out

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

if __name__ == '__main__':
    stime = time.time()
    gdal.AllRegister()
    gdal.UseExceptions()
    data = gdal_read(sys.argv[1])
    oname = os.path.splitext(sys.argv[1])[0] + "_out.tif"
    sfactor = int(sys.argv[2])#8
    nit = 10
    if(sfactor!=1):
       data=reduce(data,sfactor)
    data = fill(data,data==-9999)
    lrv = calc_LRV(data)
    maxh = np.percentile(lrv,95)#50#np.max(lrv)
    print np.max(lrv)#np.percentile(lrv,99)
    inc = maxh/nit
    h = maxh
    print "max lrv = %f inc = %f"%(maxh,inc)
    out = np.copy(data)
    for i in range(0,nit):
        print "\n\nGlobal iteration %d current h %f"%(i+1,h)
        out = filter_none_ground(out,lrv,h,tsd=3,t=1)
        h-=inc
    gdal_write(oname,out)
    print("--- Total: %s seconds ---" % (time.time() - stime))
    exit(0)
