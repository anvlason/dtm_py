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

import inpaint

gdal.AllRegister()
gdal.UseExceptions()

#dtmin = filters.minimum_filter(dt,(1,100))
#fname = "J:\\DSM_DTM\\clip_terrassa.tif"
#ds = gdal.Open(fname,gdal.GA_ReadOnly)
#data=ds.GetRasterBand(1).ReadAsArray().astype(np.float)
#data[data==-9999]=np.nan

#OutDataType=gdal.GDT_Float32
#driver=gdal.GetDriverByName("Gtiff")
#ods=driver.Create(oname,data.shape[1],data.shape[0],2,OutDataType)
#ob=ods.GetRasterBand(1)
#ob.WriteArray(minf_x,0,0)

#dddd = np.copy(data)
#nans = np.array(np.where(dif>10)).T
#nonans = np.array(np.where(dif<=10)).T
#for p in nans:
#	dddd[p[0],p[1]]=sum(dddd[q[0],q[1]]*np.exp(-(sum((p-q)**2))/2.) for q in nonans)

#x,y = np.indices(dddd.shape)
#interp = np.array(dddd)
#interp[np.isnan(interp)] = scipy.interpolate.griddata((x[~np.isnan(dddd)],y[~np.isnan(dddd)]),dddd[~np.isnan(dddd)],(x[np.isnan(dddd)],y[np.isnan(dddd)]))

def interp(dddd):
    x,y = np.indices(dddd.shape)
    interp = np.array(dddd)
    interp[np.isnan(interp)] = scipy.interpolate.griddata((x[~np.isnan(dddd)],y[~np.isnan(dddd)]),dddd[~np.isnan(dddd)],(x[np.isnan(dddd)],y[np.isnan(dddd)]),method='cubic')
    return interp

def dtm_v3(data,rank,shape,tr):
    tdata = np.copy(data)
    data=None
    ranked = filters.rank_filter(tdata,rank,shape)
    diff = tdata - ranked
    tdata[diff>tr]=np.nan
    lerp = filters.gaussian_filter(interp(tdata),1.2)
    return lerp

def dtm_rank2(data,size,tr):
    datat = np.copy(data)
    data = None
    rmin = int(size[0]*size[1]*0.05)
    rmax = int(size[0]*size[1]*0.95)
#    print "flter param:", rmin,rmax,size[0],size[1]
    rX = filters.rank_filter(datat,rmin,(size[0],size[1]))
    rY = filters.rank_filter(datat,rmin,(size[1],size[0]))
    rX = filters.rank_filter(rX,rmax,(size[0],size[1]))
    rY = filters.rank_filter(rY,rmax,(size[1],size[0]))
    diff = datat-((rX+rY)/2.0)
    out = datat[:,:]
    mask = diff>tr
    out[mask]=datat[mask]-diff[mask]
    return out

def dtm_krauss_2015(dsm,ps,minf_r):
    nx,ny = dsm.shape
    scale = 20.0/ps
    nnx = int(nx/scale+0.5)
    nny = int(ny/scale+0.5)
    scale_int = int(scale+0.5)
    print scale
    print scale_int
    minf = filters.minimum_filter(dsm,minf_r)
    dwn = cv2.resize(minf,(nny,nnx),interpolation = cv2.INTER_NEAREST)
#    dwn = scipy.misc.imresize(minf,(nnx,nny),interp='cubic')
    dwn_o = ndimage.grey_opening(dwn,5)
    dwn_g = filters.gaussian_filter(dwn_o,2.5)
#    return scipy.misc.imresize(dwn_g,(nx,ny),interp='cubic')
    return cv2.resize(dwn_g,(ny,nx),interpolation = cv2.INTER_CUBIC)


def dtm_krauss_2015_rank(dsm,ps,minf_r,t_ps):
    nx,ny = dsm.shape
    scale = t_ps/ps
    nnx = int(nx/scale+0.5)
    nny = int(ny/scale+0.5)
    scale_int = int(scale+0.5)
    print scale
    print scale_int
    rmin = int(minf_r*minf_r*0.05)
#    minf = filters.minimum_filter(dsm,minf_r)
    minf = filters.rank_filter(dsm,rmin,(minf_r,minf_r))
    dwn = cv2.resize(minf,(nny,nnx),interpolation = cv2.INTER_NEAREST)
#    dwn = scipy.misc.imresize(minf,(nnx,nny),interp='cubic')
    dwn_o = ndimage.grey_opening(dwn,5)
    dwn_g = filters.gaussian_filter(dwn_o,2.5)
#    return scipy.misc.imresize(dwn_g,(nx,ny),interp='cubic')
    return cv2.resize(dwn_g,(ny,nx),interpolation = cv2.INTER_CUBIC)

def dtm_kraus_median(data,tr,lo,hi,ml=(4,4),mh=(40,40)):
    med4 = filters.median_filter(data,ml)
    med40 = filters.median_filter(data,mh)
    diff = med4 - med40
    med4 = None
    med40 = None
    mask = diff > tr
    mask = ndimage.morphology.binary_erosion(mask,iterations=1)
    out = np.copy(data)
    out[mask] = out[mask] - diff[mask]
    out = denoise(out,lo,hi,(3,3))
    return out

def dtm_my_median(data,size,tr,lo,hi):
    med4 = filters.median_filter(data,(4,4))
    med40 = filters.median_filter(data,(size,size))
    diff = med4 - med40
    med4 = None
    med40 = None
    mask = diff > tr
    mask = ndimage.morphology.binary_erosion(mask,iterations=1)
    out = np.copy(data)
    out[mask] = out[mask] - diff[mask]
    out = denoise(out,lo,hi,(3,3))
    return out

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

def gdal_read(fname,band):
    ds = gdal.Open(fname,gdal.GA_ReadOnly)
    return ds.GetRasterBand(band).ReadAsArray().astype(np.float)

def reg_mean(data,mask,min_size):
    label_im, nb_labels = ndimage.label(mask)
    sizes = ndimage.sum(mask,label_im,range(nb_labels+1))
    mask_size = sizes < min_size
    remove_pixel = mask_size[label_im]
    label_im[remove_pixel] = 0
    labels = np.unique(label_im)
    label_im = np.searchsorted(labels, label_im)
    labels = np.unique(label_im)
    out = np.array(label_im,dtype=np.float)
    for lab in labels:
        if( lab==0 ): continue
        try:
            slice_x, slice_y = ndimage.find_objects(label_im==lab)[0]
        except IndexError:
            print ("Bad index: "%lab)
            continue
#        print lab
        rois = data[slice_x, slice_y]
        tmask = label_im==lab 
        roim = tmask[slice_x, slice_y]
        roio = out[slice_x, slice_y]
        mean = np.ma.mean(np.ma.array(rois,mask=~roim))
        roio[roim] = mean

    return out

def reg_median(data,mask,min_size):
    label_im, nb_labels = ndimage.label(mask)
    sizes = ndimage.sum(mask,label_im,range(nb_labels+1))
    mask_size = sizes < min_size
    remove_pixel = mask_size[label_im]
    label_im[remove_pixel] = 0
    labels = np.unique(label_im)
    label_im = np.searchsorted(labels, label_im)
    labels = np.unique(label_im)
    out = np.array(label_im,dtype=np.float)
    for lab in labels:
        if( lab==0 ): continue
        try:
            slice_x, slice_y = ndimage.find_objects(label_im==lab)[0]
        except IndexError:
            print ("Bad index: "%lab)
            continue
#        print lab
        rois = data[slice_x, slice_y]
        tmask = label_im==lab 
        roim = tmask[slice_x, slice_y]
        roio = out[slice_x, slice_y]
        mean = np.ma.median(np.ma.array(rois,mask=~roim))
        roio[roim] = mean

    return out

def reg_median_cont(data,mask,min_size):
    emask = ndimage.morphology.binary_erosion(mask,iterations=2)
    cmask = mask[:]
    cmask[emask==1]=0
    label_im, nb_labels = ndimage.label(cmask)
    sizes = ndimage.sum(cmask,label_im,range(nb_labels+1))
    mask_size = sizes < min_size
    remove_pixel = mask_size[label_im]
    label_im[remove_pixel] = 0
    labels = np.unique(label_im)
    label_im = np.searchsorted(labels, label_im)
    labels = np.unique(label_im)
    out = np.array(label_im,dtype=np.float)
    for lab in labels:
        if( lab==0 ): continue
        try:
            slice_x, slice_y = ndimage.find_objects(label_im==lab)[0]
        except IndexError:
            print ("Bad index: "%lab)
            continue
#        print lab
        rois = data[slice_x, slice_y]
        tmask = label_im==lab 
        roim = tmask[slice_x, slice_y]
        roio = out[slice_x, slice_y]
        mean = np.ma.median(np.ma.array(rois,mask=~roim))
        roio[roim] = mean

    return out



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


def denoise(data,lo,hi,size):
    medf = filters.median_filter(data,size)
    diff = data - medf
    hi_mask = diff > hi
    lo_mask = diff < lo
    out = np.copy(data)
    out[hi_mask] = medf[hi_mask]
    out[lo_mask] = medf[lo_mask]
    return out

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


def geodesic_dilation_v2(marker,mask):
    marker_dilation = ndimage.morphology.grey_dilation(marker,(3,3))
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
#    mask_mean = np.nanmean(mask)
    #mean_prev = np.nanmean(dilation_i)
    for i in xrange(max_iter):
#        mean_cur = np.nanmean(dilation_i)
#        print "iteration %d %f %f"%(i,mean_cur,mask_mean)
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

def recon_by_dilation_v2(marker,mask,max_iter=10000):
    """ Iterate over geodesic dilation operations
        until dilation(j+1) = dilation(j).
        Perform Geodesic dilation based on
        algorithm on p. 190-191, P. Soille, 2002. 
        This can be referenced as:
          R^delta_mask(marker)
    """
    
    print "Start reconstruction"
    dilation_i = marker
#    mask_mean = np.nanmean(mask)
#    mean_prev = np.nanmean(dilation_i)
    for i in xrange(max_iter):
#        mean_cur = np.nanmean(dilation_i)
#        print "iteration %d %f %f"%(i,mean_cur,mask_mean)
        dilation_i1 = geodesic_dilation_v2(dilation_i,mask)
        if i > 0 and np.sum(np.equal(dilation_i.ravel(),dilation_i1.ravel())) == dilation_i.size:        
            break     
        else:
            dilation_i = dilation_i1.copy()
    del dilation_i1
    print "Done. Total iterations: %d"%i
    return dilation_i



def calc_LRV(data,size):
    min_area = ndimage.minimum_filter(data,size)
    max_area = ndimage.maximum_filter(data,size)
    return max_area-min_area

def std_convoluted(image, N):
    im = np.array(image, dtype=float)
    im2 = im**2
    ones = np.ones(im.shape)

    kernel = np.ones((2*N+1, 2*N+1))
    s = scipy.signal.convolve2d(im, kernel, mode="same")
    s2 = scipy.signal.convolve2d(im2, kernel, mode="same")
    ns = scipy.signal.convolve2d(ones, kernel, mode="same")

    return np.sqrt((s2 - s**2 / ns) / ns)

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

def mean_convoluted(image, m, n):
    kernel=np.full((m,n),1.0/(m*n))
    return scipy.signal.convolve2d(image, kernel, mode="same", boundary="symm")



def recon_by_median(data,flt,ml=(4,4),mh=(40,40)):   
   lo = -0.5
   hi = 0.5
   i = 1
   out_dtm = data[:]
   for tr in flt:
       print "filtration threshold %.2f interation %d from %d"%(tr,i,len(flt))
       out_dtm = dtm_kraus_median(out_dtm,tr,lo,hi,ml,mh)
       if i > 1 and np.sum(np.equal(out_dtm.ravel(),prev.ravel())) == out_dtm.size:        
           break     
       else:
           i+=1
           prev = np.copy(out_dtm)
   return out_dtm

def fill_by_median(data,big,small):
    filled = denoise(data,-1000,1000,big)
    return denoise(filled,-0.5,0.5,small)


def extract_labels(data,min_size=10,ext=0):
    label_im, nb_labels = ndimage.label(data)
    sizes = ndimage.sum(data,label_im,range(nb_labels+1))
    if(ext!=0):
        mask_size = sizes > min_size
    else:
        mask_size = sizes < min_size
    remove_pixel = mask_size[label_im]
    label_im[remove_pixel] = 0
    labels = np.unique(label_im)
    label_im = np.searchsorted(labels, label_im)
    labels = np.unique(label_im)
    return label_im

def extract_contour(mask, iteration=1):
    erode = ndimage.morphology.binary_erosion(mask,iterations=iteration)
    out = np.copy(mask)
    out[erode==1]=0
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
    lab = extract_labels(nDSM0 > np.std(nDSM0)*tsd)
    print "Total regions: %d"%len(lab)
    reg = reg_median_cont1(lrv,lab)
    print "Regions mean: %f"%np.mean(reg)
    mask[reg>t]=nd
    return mask, imrec#(imrec, nDSM0, lab, reg, mask)

    
def flt_minmax(data,size,it):
    fdata = np.copy(data)
    data = None
    for i in range(0,it):
        print "dtm rank filter iteration %d"%(i+1)
        out = dtm_rank2(fdata,size,0.5)
        fdata = out
    return out


def recon_by_rank(data,size_hi,size_lo,tr=2,it=10):
    ldata = np.copy(data)
    hdata = np.copy(data)
    out = np.copy(data)
    data = None
    for i in range(0,it):
#        print "dtm filter iteration %d"%(i+1)
        rank_lo = dtm_rank2(ldata,size_lo,0.5)
        ldata = rank_lo
        rank_hi = dtm_rank2(hdata,size_hi,0.5)
        hdata = rank_hi
    mask = (out[:]-rank_lo[:])>tr
    out[mask]=rank_hi[mask]
    return out

def flt_rank_recon(data,size_hi,size_lo,tr,it,int_it=10):
    out = np.copy(data)
    data = None
    for i in range(0,it):
        print "dtm filter iteration %d mean %f"%(i+1,np.mean(out[out>-9999]))
        out = recon_by_rank(out,size_hi,size_lo,tr,int_it)
        if i > 0 and np.sum(np.equal(out.ravel(),prev.ravel())) == out.size:        
           break     
        else:
           i+=1
           prev = np.copy(out)
    return out

def set_range(data, out, nd=-9999):
    out[out<np.min(data[data!=nd])]=nd
    return out

def recon_by_wtophat(data,size,th=10,it=10):
    out = np.copy(data)
    data = None
    for i in range(0,it):
        print "dtm wh filter iteration %d mean %f"%(i+1,np.mean(out[out>-9999]))
        wth = ndimage.morphology.white_tophat(out,size)
        out[wth>th]-=wth[wth>th]        
        if i > 0 and np.sum(np.equal(out.ravel(),prev.ravel())) == out.size:        
           break     
        else:
           i+=1
           prev = np.copy(out)
    return out

def tosha_dtm(data):
    flt_hi = ([1,21],[1,17],[1,15],[1,11],[1,7])
    flt_lo = ([1,11],[1,9], [1,7], [1,5], [1,3])
    flt_tr = (10,8,4,1,0.5)
    out = np.copy(data)
    for i in range(0,len(flt_tr)):
        print "tosha iteration %d"%(i+1)
        out = flt_rank_recon(out,flt_hi[i],flt_lo[i],flt_tr[i],2000,int_it=7)

    return set_range(data,out) 

def tosha_dtm_0(data):
    flt_hi = (1,40)
    flt_lo = (1,9)
    flt_tr = 1
    return set_range(data,flt_rank_recon(data,flt_hi,flt_lo,flt_tr,20,int_it=3))
    
def recon_by_gauss(data,sigma,th=2,it=10000):
    out = np.copy(data)
    data = None
    for i in range(0,it):
        print "dtm gauss filter iteration %d mean %f"%(i+1,np.mean(out[out>-1000]))
        gauss = filters.gaussian_filter(out,sigma)
        diff = out[:]-gauss[:]
        out[diff>th]=gauss[diff>th]        
        if i > 0 and np.sum(np.equal(out.ravel(),prev.ravel())) == out.size:        
           break     
        else:
           i+=1
           prev = np.copy(out)
    return out

def fspecial_gauss(size, sigma):

    """Function to mimic the 'fspecial' gaussian MATLAB function
    """
    x, y = np.mgrid[-size//2 + 1:size//2 + 1, -size//2 + 1:size//2 + 1]
    g = np.exp(-((x**2 + y**2)/(2.0*sigma**2)))
    return g/g.sum()

def recon_by_gauss1(data,ps,th=1,it=10000):
    out = np.copy(data)
    data = None
    size = int(100/ps+0.5)
    sigma = 25.0/ps
    kernel = fspecial_gauss(size,sigma)
    for i in range(0,it):
        print "dtm gauss filter iteration %d mean %f"%(i+1,np.mean(out[out>-1000]))
        gauss = scipy.signal.convolve2d(out,kernel,mode="same", boundary="symm")
        diff = out[:]-gauss[:]
        nmask = diff>th
        out = fill(out,nmask)
        if i > 0 and np.sum(np.equal(out.ravel(),prev.ravel())) == out.size:        
           break     
        else:
           i+=1
           prev = np.copy(out)
    return out

def calc_col_perc(data,perc,low):
    out = np.zeros((1,data.shape[1]))
    for i in range(0,data.shape[1]):
        tbuf = data[:,i]
        try:
            out[0,i] = np.percentile(tbuf[tbuf>low],perc,interpolation='linear')
        except IndexError:
            out[0,i] = -9999.0

    return out[0,:]

def calc_col_mean(data,low):
    out = np.zeros((1,data.shape[1]))
    for i in range(0,data.shape[1]):
        tbuf = data[:,i]
        try:
            out[0,i] = np.mean(tbuf[tbuf>low])
        except IndexError:
            out[0,i] = -9999.0
    return out[0,:]


def window_stdev(arr, radius):
    c1 = ndimage.filters.uniform_filter(arr, radius*2, mode='constant', origin=-radius)
    c2 = ndimage.filters.uniform_filter(arr*arr, radius*2, mode='constant', origin=-radius)
#    return ((c2 - c1*c1)**.5)[:-radius*2+1,:-radius*2+1]
    return ((c2 - c1*c1)**.5)



def windowed_sum(a, win):
    table = np.cumsum(np.cumsum(a, axis=0), axis=1)
    win_sum = np.empty(tuple(np.subtract(a.shape, win-1)))
    win_sum[0,0] = table[win-1, win-1]
    win_sum[0, 1:] = table[win-1, win:] - table[win-1, :-win]
    win_sum[1:, 0] = table[win:, win-1] - table[:-win, win-1]
    win_sum[1:, 1:] = (table[win:, win:] + table[:-win, :-win] -
                       table[win:, :-win] - table[:-win, win:])
    return win_sum

def windowed_var(a, win):
    win_a = windowed_sum(a, win)
    win_a2 = windowed_sum(a*a, win)
    return (win_a2 - win_a * win_a / win/ win) / win / win


def mkgrid(data,method='cubic'):
    x = np.arange(0,data.shape[1])
    y = np.arange(0,data.shape[0])
    data = np.ma.masked_invalid(data)
    xx,yy = np.meshgrid(x,y)
    x1 = xx[~data.mask]
    y1 = yy[~data.mask]
    new = data[~data.mask]
    return scipy.interpolate.griddata((x1,y1),new.ravel(),(xx,yy),method=method)


def nan_helper(y):
    """Helper to handle indices and logical indices of NaNs.

    Input:
        - y, 1d numpy array with possible NaNs
    Output:
        - nans, logical indices of NaNs
        - index, a function, with signature indices= index(logical_indices),
          to convert logical indices of NaNs to 'equivalent' indices
    Example:
        >>> # linear interpolation of NaNs
        >>> nans, x= nan_helper(y)
        >>> y[nans]= np.interp(x(nans), x(~nans), y[~nans])
    """

    return np.isnan(y), lambda z: z.nonzero()[0]

def remove_peaks(data,hi,low,fill=np.nan):
    out = np.copy(data)
    out[data>np.nanpercentile(data,hi)]=fill
    out[data<np.nanpercentile(data,low)]=fill
    return out


def remove_low(data,min_size):
    out = np.copy(data)
    j=1
    for i in range(1,50,5):
        threshold = np.percentile(out[out!=9999],i)
        print "Iteration %d threshold=%f"%(j,threshold)
        mask = extract_labels(out<threshold,min_size,ext=1)
        out[mask>0]=9999
        j+=1
    return out

def remove_hi(data,min_size):
    out = np.copy(data)
    j=1
    for i in range(100,75,-5):
        threshold = np.percentile(out[out!=-9999],i)
        print "Iteration %d threshold=%f"%(j,threshold)
        mask = extract_labels(out>threshold,min_size,ext=1)
        out[mask>0]=-9999
        j+=1
    return out

#meanshift
#cv2.cvtColor(data.astype(np.uint8),cv2.COLOR_GRAY2BGR)

#save no nan
#>>> xyz[xyz==-9999]=np.nan
#>>> xyz1 = xyz[~np.isnan(xyz).any(axis=1)]
#flt_hi = ([1,21],[1,17],[1,15],[1,11],[1,7])
#flt_lo = ([1,11],[1,9], [1,7], [1,5], [1,3])
#flt_tr = (10,8,4,1,0.5)


#step1 - recon by rank (1,21) (1,5)
#step2 - recon by white tophat, start from 21,17,15,9,5 - 10,8,6,4,2
#step3 = x3

#fill holes
#scipy.ndimage.morphology.binary_fill_holes

#data = interp(data)
#filled = inpaint.replace_nans(data,5,0.5,3,'localmean')
print "Done"

#flt
#dtm_med = recon_by_median(data,([15,10,5,5,2,2,1,1,0.5,0.5]))
#recim_hi = flt_rank_recon(data,(1,17),(1,5),1,30)


__END__

data_i1 = data[:]
data_i1[regmed50>2]=-9999
marker40 = data_i1[:]-40
marker40[regmed50>2]=-9999
imrec40=recon_by_dilation(marker40,data_i1)
dif40 = data_i1[:]-imrec40[:]
nDSM1 = extract_labels(dif40 > np.std(dif40)*3)
regmed40 = reg_median_cont1(lrv,nDSM1)


flt_tr = [0.25,0.25,0.25,0.25,0.25,0.25,0.25,0.25,0.25,0.25]#[5,5,2,2,1,1,0.5,0.5,0.5,0.5,0.5,0.5,0.2,0.2,0.2,0.2]#,0.8,0.7,0.6,0.5,0.4,0.3,0.2]
lo = -0.5
hi = 0.5
i = 1
denoised = denoise(data,lo,hi,(3,3))
out_dtm = np.copy(denoised)
for tr in flt_tr:
   print "filtration threshold %.2f interation %d from %d"%(tr,i,len(flt_tr))
   oname = "dtm_%.2f_%d.tif"%(tr,i)
   out_dtm = dtm_kraus_median(out_dtm,tr,lo,hi)
#   gdal_write(oname,out_dtm)
   i+=1
   lo = -2
   hi = 2

#todo:
#1. generate nDTM0 - smoothed DSM, using iterative median filtering
#2. generate difference map, with threshold dif > std(dif)*t (t=0.9)
#3. generate local height variation - max(loc)-min(loc)
#4. generate contour of the difference map - by erosion with 2 iterations and subtraction
#5. generate separate polygons from diference map
#6. get median height variation and insert it in diference map polygons
   
