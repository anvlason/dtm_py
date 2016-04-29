import numpy as np
import sys
from osgeo import gdal
from osgeo.gdalconst import *
import numpy as np
import numpy.ma as ma
import os.path
gdal.AllRegister()
gdal.UseExceptions()

fname = "I:\MTS\Luga_22102014_1m_int16.tif"#sys.argv[1]
oname = os.path.splitext(fname)[0] + '.bin'
hname = os.path.splitext(fname)[0] + '.index'
ds = gdal.Open(fname,gdal.GA_ReadOnly)
data=ds.GetRasterBand(1).ReadAsArray().astype(np.int16)
trn=ds.GetGeoTransform()
minX=int(trn[0]+0.5)
maxY=int(trn[3]+0.5)
maxX = int(data.shape[1]*trn[1]+minX)
minY = int(maxY-data.shape[0]*trn[1])
data = data.byteswap()

f = open(oname,'wb')
f.write(data)
f.close()

fh = open(hname,"w")
fh.write("%s\t%d %d %d %d %d\n" %(os.path.basename(oname),minX,maxX,minY,maxY,int(trn[1])))
fh.close()

"""
f = open('ints','wb')
x = f.read()
numpy.fromstring(x, dtype=np.uint16, count=3)
array([1, 2, 3], dtype=uint16)
"""
