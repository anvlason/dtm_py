import rpc_staff as rpc
import gdal_staff as gdal
import pyproj
import liblas as las
import os
import numpy as np

os.chdir("e:/sz_remap")
data = gdal.gdal_read("remaped.tif",2)
ZONE=36
step=2
r = rpc.read_orthokit("14MAY29095545-P2AS-055633805020_01_P001_F.icrpci")
pj_str = "+proj=utm +zone=%d  +ellps=WGS84 +datum=WGS84 +units=m +no_defs"%(ZONE)
utm = pyproj.Proj(pj_str)
lonlat = pyproj.Proj('+proj=longlat +datum=WGS84 +no_defs')
o_srs = las.srs.SRS(pj_str)

hh = las.header.Header()
hh.set_scale([0.01,0.01,0.01])
hh.set_offset([0.0,0.0,0.0])
hh.set_srs(o_srs)
of = las.file.File("test_2x_UTM.las",header=hh,mode="w")
for s in range(0,data.shape[1],step):
	print "%d"%s
	for l in range(0,data.shape[0],step):
		h = data[l][s]
		if(h!=-9999):
			p = las.point.Point()
			p.set_header(hh)
#			p.z = h
			lon,lat = rpc.calc_rfm_i(r,s,l,h)
			p.x, p.y = (pyproj.transform(lonlat,utm,lon,lat,radians=False))
			p.z = float(h)
			of.write(p)
			

of.close()

"""
__END__
out = open("test.csv","wt")
out.write("Lon,Lat,H\n")
for s in range(0,data.shape[1]):
    print "%d\n"%s
    for l in range(0,data.shape[0]):
        h = data[l][s]
        if(h!=-9999):
            lon,lat = rpc.calc_rfm_i(r,s,l,h)
            out.write("%.15f,%.15f,%.3f\n"%(lon,lat,h))
			
h = las.header.Header()
of = las.file.File("test_4x.laz",mode="w",header=h)
for s in range(0,data.shape[1],4):
    print "%d"%s
    for l in range(0,data.shape[0],4):
        h = data[l][s]
        if(h!=-9999):
            p = las.point.Point()
            p.x,p.y = rpc.calc_rfm_i(r,s,l,h)
            p.z = h
			
#    pj_str = "+proj=geocent +a=%f +b=%f +units=m +no_defs" % (EARTH_A,EARTH_B)
    pj_str = "+proj=utm +zone=%d  +ellps=WGS84 +datum=WGS84 +units=m +no_defs"%(ZONE)
    utm = pyproj.Proj(pj_str)
    lonlat = pyproj.Proj('+proj=longlat +datum=WGS84 +no_defs')
#    lonlat = pyproj.Proj('+proj=utm +zone=44  +ellps=WGS84 +datum=WGS84 +units=m +no_defs')
    x, y, z = np.float_(pyproj.transform(lonlat,utm,lon,lat,h,radians=False))

"""

