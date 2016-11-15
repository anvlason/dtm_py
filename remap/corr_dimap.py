import sys
import os
import numpy as np
from xml.dom import minidom
import datetime
#import matplotlib.pyplot as plt
import re
import subprocess
import time

#Calc julian date
def toJD(year,mon,day,hour,mnt,sec):
    mjd_epoch=2400000.5
    j2000_mjd=51544.5
    a = int((14-mon)/12)
    y = year + 4800 - a
    m = mon + 12*a -3
    JDN = day + int((153*m+2)/5.)+365*y + int(y/4.)-int(y/100.)+int(y/400.)-32045
    JD = np.float_(JDN + (hour-12)/24. + mnt/1440. + sec/86400.)

    MJD = np.float_(JD - mjd_epoch)
    MJD_day = int(MJD)
    return np.float_([JDN, JD, MJD, MJD_day, JDN-JD])

def JD2Greg(jd):
    p = int(jd+0.5)+68569
    q = int(4*p/146097)
    r = int(p - (146097*q+3)/4)
    s = int(4000*(r+1)/1461001)
    t = int(r - 1461*s/4 +31)
    u = int(80*t/2447)
    v = int(u/11)

    Y = int(100*(q-49)+s+v)
    M = int(u + 2 -12*v)
    D = int(t -2447*u/80)
    hh = np.float_((jd-int(jd-0.5))*24-12)
    mm = np.float_((hh-int(hh))*60)
    ss = np.float_((mm-int(mm))*60)
    ms = np.float_((ss-int(ss))*1000000)
    dt = datetime.datetime(Y,M,D,int(hh),int(mm),int(ss),int(ms))
    return str("%sZ"%dt.isoformat())

def datetime2str(date,td):
    hh = td*24
    mm = (hh-int(hh))*60
    ss = (mm-int(mm))*60
    ms = (ss - int(ss))*1e6
    t=datetime.time(int(hh),int(mm),int(ss),int(ms))
    return str("%sT%s"%(date,t.strftime("%H:%M:%S.%fZ")))

#print toJD(2016,6,1,15,44,7.0)
def strtojd(string):
    date = np.array(string.split("T")[0].split("-"),dtype=int)
    ttt = string.split("T")[1].split(":")
    time = np.array((ttt[0],ttt[1],float(ttt[2].split("Z")[0])),dtype=float)
    return np.float_(toJD(date[0],date[1],date[2],time[0],time[1],time[2]))

#print toJD(2016,6,1,15,44,7.0)
def getdatetime(string):
    date = np.array(string.split("T")[0].split("-"),dtype=int)
    ttt = string.split("T")[1].split(":")
    time = np.array((ttt[0],ttt[1],float(ttt[2].split("Z")[0])),dtype=float)
    td = np.float_(time[0]/24. + time[1]/1440. + time[2]/86400.)
    return ((string.split("T")[0]),(td))

#print toJD(2016,6,1,15,44,7.0)
def strtojd1(string):
    date = np.array(string.split("T")[0].split("-"),dtype=int)
    ttt = string.split("T")[1].split(":")
    time = np.array((ttt[0],ttt[1],float(ttt[2].split("Z")[0])),dtype=float)
    return np.float_(toJD(date[0],date[1],date[2],time[0],time[1],time[2])[1])

#read quaternions from IAP
def readIAPquat(name):
    xmldoc = minidom.parse(name)
    qlist = xmldoc.getElementsByTagName("UTC_Quaternion")
    qcount = len(qlist)
    q=np.zeros((qcount,5),dtype=np.float_)
    for i in range(0,qcount):
            qt=qlist[i].getElementsByTagName("QuaternionValues")[0]
            q[i,0:4]=map(np.float_,qt.firstChild.nodeValue.split(" "))
#            q[i,4]=strtojd(qlist[i].getElementsByTagName("UTC_TIME")[0].firstChild.nodeValue)[1]
            q[i,4]=getdatetime(qlist[i].getElementsByTagName("UTC_TIME")[0].firstChild.nodeValue)[1]
    xmldoc=None
    return q

#read sat Position coords from IAP
def readIAPpos(name):
    xmldoc = minidom.parse(name)
    poslist = xmldoc.getElementsByTagName("Point")
    pcount = len(poslist)
    pos=np.zeros((pcount,7),dtype=np.float_)
    for i in range(0,pcount):
            pt=poslist[i].getElementsByTagName("LOCATION_VALUES")[0]
            pos[i,0:3]=map(np.float_,pt.firstChild.nodeValue.split(" "))
            vl=poslist[i].getElementsByTagName("VELOCITY_VALUES")[0]
            pos[i,3:6]=map(np.float_,vl.firstChild.nodeValue.split(" "))
            pos[i,6]=getdatetime(poslist[i].getElementsByTagName("UTC_TIME")[0].firstChild.nodeValue)[1]
    xmldoc=None
    return pos

#read quaternions from DIMAP
def readDIMquat(name):
    xmldoc = minidom.parse(name)
    qlist = xmldoc.getElementsByTagName("Quaternion")
    qcount = len(qlist)
    q=np.zeros((qcount,5),dtype=np.float_)
    for i in range(0,qcount):
            q[i,0]=np.float_(qlist[i].childNodes[3].firstChild.nodeValue)
            q[i,1]=np.float_(qlist[i].childNodes[5].firstChild.nodeValue)
            q[i,2]=np.float_(qlist[i].childNodes[7].firstChild.nodeValue)
            q[i,3]=np.float_(qlist[i].childNodes[9].firstChild.nodeValue)
#            q[i,4]=strtojd(qlist[i].getElementsByTagName("TIME")[0].firstChild.nodeValue)[1]
            q[i,4]=getdatetime(qlist[i].getElementsByTagName("TIME")[0].firstChild.nodeValue)[1]
    xmldoc=None
    return q

#read sat Position coords from DIM
def readDIMpos(name):
    xmldoc = minidom.parse(name)
    poslist = xmldoc.getElementsByTagName("Point")
    pcount = len(poslist)
    pos=np.zeros((pcount,7),dtype=np.float_)
    for i in range(0,pcount):
            pt=poslist[i].getElementsByTagName("LOCATION_XYZ")[0]
            pos[i,0:3]=map(np.float_,pt.firstChild.nodeValue.split(" "))
            vl=poslist[i].getElementsByTagName("VELOCITY_XYZ")[0]
            pos[i,3:6]=map(np.float_,vl.firstChild.nodeValue.split(" "))
            pos[i,6]=getdatetime(poslist[i].getElementsByTagName("TIME")[0].firstChild.nodeValue)[1]
    xmldoc=None
    return pos

#calculate linear trend
def GetTrendQuat(q):
    fit_w = np.poly1d(np.polyfit(q[:,4],q[:,0],1))
    fit_x = np.poly1d(np.polyfit(q[:,4],q[:,1],1))
    fit_y = np.poly1d(np.polyfit(q[:,4],q[:,2],1))
    fit_z = np.poly1d(np.polyfit(q[:,4],q[:,3],1))
    return (fit_w,fit_x,fit_y,fit_z)

#calculate linear trend for ephemerides
def GetTrendPos(pos):
    fit_x = np.poly1d(np.polyfit(pos[:,6],pos[:,0],1))
    fit_y = np.poly1d(np.polyfit(pos[:,6],pos[:,1],1))
    fit_z = np.poly1d(np.polyfit(pos[:,6],pos[:,2],1))
    fit_vx = np.poly1d(np.polyfit(pos[:,6],pos[:,3],1))
    fit_vy = np.poly1d(np.polyfit(pos[:,6],pos[:,4],1))
    fit_vz = np.poly1d(np.polyfit(pos[:,6],pos[:,5],1))
    return (fit_x,fit_y,fit_z,fit_vx,fit_vy,fit_vz)

#detrend source quaternions
def DeTrendQuat(q,trend):
    detrended = np.zeros((len(q),5),dtype=np.float_)
    detrended[:,0] = q[:,0]-trend[0](q[:,4])
    detrended[:,1] = q[:,1]-trend[1](q[:,4])
    detrended[:,2] = q[:,2]-trend[2](q[:,4])
    detrended[:,3] = q[:,3]-trend[3](q[:,4])
    detrended[:,4] = q[:,4]
    return detrended

#detrend ephemerides
def DeTrendPos(pos,trend):
    detrended = np.zeros((len(pos),7),dtype=np.float_)
    detrended[:,0] = pos[:,0]-trend[0](pos[:,6])
    detrended[:,1] = pos[:,1]-trend[1](pos[:,6])
    detrended[:,2] = pos[:,2]-trend[2](pos[:,6])
    detrended[:,3] = pos[:,3]-trend[3](pos[:,6])
    detrended[:,4] = pos[:,4]-trend[4](pos[:,6])
    detrended[:,5] = pos[:,5]-trend[5](pos[:,6])
    detrended[:,6] = pos[:,6]
    return detrended

#detrend angles
def DeTrendAngles(a,trend):
    detrended = np.zeros((len(a),4),dtype=np.float_)
    detrended[:,0] = a[:,0]-trend[0](a[:,3])
    detrended[:,1] = a[:,1]-trend[1](a[:,3])
    detrended[:,2] = a[:,2]-trend[2](a[:,3])
    detrended[:,3] = a[:,3]
    return detrended

#fit detrend quaternions with poly^3
def fitPoly3(q):
    fit_w = np.poly1d(np.polyfit(q[0::62,4],q[0::62,0],3))
    fit_x = np.poly1d(np.polyfit(q[0::62,4],q[0::62,1],3))
    fit_y = np.poly1d(np.polyfit(q[0::62,4],q[0::62,2],3))
    fit_z = np.poly1d(np.polyfit(q[0::62,4],q[0::62,3],3))
    return (fit_w,fit_x,fit_y,fit_z)

#fit detrend angles with poly^3
def fitPoly3Ang(a):
    fit_x = np.poly1d(np.polyfit(a[:,3],a[:,0],3))
    fit_y = np.poly1d(np.polyfit(a[:,3],a[:,1],3))
    fit_z = np.poly1d(np.polyfit(a[:,3],a[:,2],3))
    return (fit_x,fit_y,fit_z)

#fit detrend ephemerides with poly^3
def fitPoly3Pos(pos):
    fit_x = np.poly1d(np.polyfit(pos[:,6],pos[:,0],3))
    fit_y = np.poly1d(np.polyfit(pos[:,6],pos[:,1],3))
    fit_z = np.poly1d(np.polyfit(pos[:,6],pos[:,2],3))
    fit_vx = np.poly1d(np.polyfit(pos[:,6],pos[:,3],3))
    fit_vy = np.poly1d(np.polyfit(pos[:,6],pos[:,4],3))
    fit_vz = np.poly1d(np.polyfit(pos[:,6],pos[:,5],3))
    return (fit_x,fit_y,fit_z,fit_vx,fit_vy,fit_vz)

#normalization 
def norm(data):
    n = np.zeros((len(data),1),dtype=np.float_)
    for j in range(0,len(data)):
        s=np.float_(0.0)
        for i in range(0,len(data[0])):
                s+=data[j,i]*data[j,i]
        n[j,0] = np.float_(1/np.sqrt(s))
#    return (np.array(data,dtype=np.float_)*n)
    return (n)

#write to xml
def writeXML(date,nquat,npos,name,oname):
    xmldoc = minidom.parse(name)
    qlist = xmldoc.getElementsByTagName("Quaternion")
    i = 0
    for node in qlist:
        node.getElementsByTagName('Q0')[0].firstChild.replaceWholeText(str("%.18f"%nquat[i,0]))
        node.getElementsByTagName('Q1')[0].firstChild.replaceWholeText(str("%.18f"%nquat[i,1]))
        node.getElementsByTagName('Q2')[0].firstChild.replaceWholeText(str("%.18f"%nquat[i,2]))
        node.getElementsByTagName('Q3')[0].firstChild.replaceWholeText(str("%.18f"%nquat[i,3]))
        node.getElementsByTagName('TIME')[0].firstChild.replaceWholeText(datetime2str(date,nquat[i,4]))
        i+=1
    plist = xmldoc.getElementsByTagName("Point")
    i = 0
    for node in plist:
        node.getElementsByTagName('LOCATION_XYZ')[0].firstChild.replaceWholeText(str("%.18f %.18f %.18f"%(npos[i,0],npos[i,1],npos[i,2])))
        node.getElementsByTagName('VELOCITY_XYZ')[0].firstChild.replaceWholeText(str("%.18f %.18f %.18f"%(npos[i,3],npos[i,4],npos[i,5])))
        node.getElementsByTagName('TIME')[0].firstChild.replaceWholeText(datetime2str(date,npos[i,6]))
        i+=1
    of=open(oname,'w')
    xmldoc.writexml(of)
    of.close
    xmldoc = None


#extract angles from quaternion
def quat2rpy2(Q):
    w = Q[0]
    x = Q[1]
    y = Q[2]
    z = Q[3]    
    r = np.float_(np.arctan2(2*y*w - 2*x*z, 1 -2*y*y - 2*z*z))
    p = np.float_(np.arctan2(2*x*w - 2*y*z, 1 -2*x*x - 2*z*z))
    y = np.float_(np.arcsin(2*x*y + 2*z*w))
    return np.float_([r,p,y])

def rpy2quat(r,p,y): #xyz - bha (bank,heading, attitude) rotation z->y->x rpy2quat(z,y,x)
    c1 = np.cos(p/2.0)
    c2 = np.cos(y/2.0)
    c3 = np.cos(r/2.0)
    s1 = np.sin(p/2.0)
    s2 = np.sin(y/2.0)
    s3 = np.sin(r/2.0)
    c1c2 = c1*c2
    s1s2 = s1*s2
    w = c1c2*c3 - s1s2*s3
    x = c1c2*s3 + s1s2*c3
    y = s1*c2*c3 + c1*s2*s3
    z = c1*s2*c3 - s1*c2*s3
    return (norm([w,x,y,z]))

def GetTrendAng(a):
    fit_x = np.poly1d(np.polyfit(a[:,3],a[:,0],1))
    fit_y = np.poly1d(np.polyfit(a[:,3],a[:,1],1))
    fit_z = np.poly1d(np.polyfit(a[:,3],a[:,2],1))    
    return (fit_x,fit_y,fit_z)


def GetTimeRange(name):
    xmldoc = minidom.parse(name)
    tr = xmldoc.getElementsByTagName("Time_Range")
    date, time_s = getdatetime(tr[0].getElementsByTagName("START")[0].firstChild.nodeValue)
    time_e = getdatetime(tr[0].getElementsByTagName("END")[0].firstChild.nodeValue)[1]
    xmldoc=None
    return (date,time_s,time_e)

def GetDIMtiles(name):
    xmldoc = minidom.parse(name)
    tn = xmldoc.getElementsByTagName("DATA_FILE_PATH")[0].getAttributeNode('href').nodeValue
    nrows = int(xmldoc.getElementsByTagName("NTILES_SIZE")[0].getAttributeNode('nrows').nodeValue)
    ncols = int(xmldoc.getElementsByTagName("NTILES_SIZE")[0].getAttributeNode('ncols').nodeValue)
    xmldoc=None
    return (os.path.dirname(name)+"\\"+re.sub('R1C1.TIF','.TIFF',tn),[nrows,ncols])

def GetRPCheight(name):
    xmldoc = minidom.parse(name)
    off = float(xmldoc.getElementsByTagName('HEIGHT_OFF')[0].firstChild.nodeValue)
    scale = float(xmldoc.getElementsByTagName('HEIGHT_SCALE')[0].firstChild.nodeValue)
    xmldoc=None
    min = off-scale
    mean = scale
    max = off+scale
    return ([min,min+(mean-min)/2.0,mean,mean+(max-mean)/2.0,max])

def worker(proc, name, h, step):
    command = "%s %s %f %f"%(proc,name,step,h)
    if(os.system(command)!=0):
        print "Error...\nGrid generation failed"
        exit(1)

def run_multi(pool,proc,name,heights,step):
    for h in heights:
        pool.apply_async(worker, args=(proc,name, h, step))



start_time = time.time()

if len(sys.argv)<2:
    name = "niitp\\DIM_SPOT7_P_20150401051933870_SEN_RS-DS-00_000000.XML"
    iname = "niitp\\IAP_SPOT7_201504010519338_RU1_RU1_RU2_RU2_00000319_123_00000_03331_E082N57.xml"
else:
    if os.path.exists(sys.argv[1]):
        name = sys.argv[1]
    else:
        print "ERROR...\nInput DIM file does not exists\n"
        exit(1)
    if os.path.exists(sys.argv[2]):
        iname = sys.argv[2]
    else:
        print "ERROR...\nInput IAP file does not exists\n"
        exit(1)    
msmode = 0
res = re.findall("_MS_",name,flags=re.IGNORECASE)
if len(res) > 0:
    msmode = 1
    print "ms mode\n"
oname = re.sub(".XML","_COR.XML",name,flags=re.IGNORECASE)
bname = re.sub(".XML",".batch",name,flags=re.IGNORECASE)
rpcname = re.sub("DIM_SPOT","RPC_SPOT",name,flags=re.IGNORECASE)
relname = os.path.dirname(name)+"\\"+"srtm.tif"
flname = os.path.dirname(name)+"\\"+"flist"
ip_path = "c:\\app\\BIN_IC_REMAP\\IC.exe"
rpc_path = "c:\\app\\BIN_IC_REMAP\\BIN_BLAS\\QR_BLAS.exe"
rsmod = "rs_model.py"
rpcconv = "OrthoKit2DIM.pl"
relief_path = "C:\\SRTM_LAST"
use_angles = 0
use_norm = 1
mk_batch = 1
use_rel = 1
remap = 1
rename = 1
calc_rpc = 1
cleanup = 1
gridstep = 32
if msmode == 1:
    gridstep = 8
height = GetRPCheight(rpcname)
print height
#exit(0)
squat = readDIMquat(name)
nsamp = len(squat)
siquat = readIAPquat(iname)
spos = readDIMpos(name)
nsamppos = len(spos)
sipos = readIAPpos(iname)

#get time range
date,tstart,tend = GetTimeRange(name)
tstep = (tend-tstart)/nsamp
trange=np.linspace(tstart,tend,nsamp).astype(np.float_)
trangepos = np.linspace(tstart,tend,nsamppos).astype(np.float_)

#process
if use_angles == 1:
    print "Transform to angles"
    angles=np.zeros((len(siquat),4),dtype=np.float_)
    for i in range(0,len(siquat)):
        angles[i,0:3]=quat2rpy2(siquat[i,0:4])
        angles[i,3]=siquat[i,4]
    trend = GetTrendAng(angles)
    dangles = DeTrendAng(angles,trend)
    fit = fitPoly3Ang(dangles)

    nangles = np.zeros((nsamp,4),dtype=np.float_)
    nangles[:,0] = np.float_(fit[0](trange)+trend[0](trange))
    nangles[:,1] = np.float_(fit[1](trange)+trend[1](trange))
    nangles[:,2] = np.float_(fit[2](trange)+trend[2](trange))
    nangles[:,3] = np.float_(trange)

    nquat = np.zeros((len(squat),5),dtype=np.float_)
    for i in range(0,len(squat)):
        nquat[i,0:4]=rpy2quat(nangles[i,1],nangles[i,2],nangles[i,0])
        #nquat = norm(nquat)
        nquat[:,4] = nangles[:,3]
else:
    print "Interpolate quaternions, and create DIM file"
    trend = GetTrendQuat(siquat)
    dquat = DeTrendQuat(siquat,trend)
    fit = fitPoly3(dquat)
    nquat = np.zeros((len(squat),5),dtype=np.float_)
    nquat[:,0] = np.float_(fit[0](trange)+trend[0](trange))
    nquat[:,1] = np.float_(fit[1](trange)+trend[1](trange))
    nquat[:,2] = np.float_(fit[2](trange)+trend[2](trange))
    nquat[:,3] = np.float_(fit[3](trange)+trend[3](trange))
    nquat[:,4] = np.float_(trange)
    if use_norm == 1:
        norm = 1/np.sqrt(nquat[:,0]*nquat[:,0]+nquat[:,1]*nquat[:,1]+nquat[:,2]*nquat[:,2]+nquat[:,3]*nquat[:,3]).astype(np.float_)
        nquat[:,0] = nquat[:,0]*norm[:]
        nquat[:,1] = nquat[:,1]*norm[:]
        nquat[:,2] = nquat[:,2]*norm[:]
        nquat[:,3] = nquat[:,3]*norm[:]

trendpos = GetTrendPos(sipos)
dpos = DeTrendPos(sipos,trendpos)
fitpos = fitPoly3Pos(dpos)
npos = np.zeros((len(spos),7),dtype=np.float_)
npos[:,0]=np.float_(fitpos[0](trangepos)+trendpos[0](trangepos))
npos[:,1]=np.float_(fitpos[1](trangepos)+trendpos[1](trangepos))
npos[:,2]=np.float_(fitpos[2](trangepos)+trendpos[2](trangepos))
npos[:,3]=np.float_(fitpos[3](trangepos)+trendpos[3](trangepos))
npos[:,4]=np.float_(fitpos[4](trangepos)+trendpos[4](trangepos))
npos[:,5]=np.float_(fitpos[5](trangepos)+trendpos[5](trangepos))
npos[:,6]=np.float_(trangepos)

writeXML(date,nquat,npos,name,oname)

if mk_batch == 1:
    print "Create IP batch"    
    batch=open(bname,'w')
    imname,tsize = GetDIMtiles(name)
    batch.write("-exit=1\n")
    batch.write("-readWorldFile=0\n")
    batch.write("-ReadTabFile=0\n")
    batch.write("-ReadGeoGrid=0\n")
    batch.write("-ReadMetFile=0\n")
    batch.write("-SaveTabFile=0\n")
    batch.write("-SaveMetFile=1\n")
    batch.write("-SaveGeoGrid=0\n")
    batch.write("-CompRadiance=0\n")
    batch.write("-SkipPyramids=1\n")
    batch.write("-OutputFormat=\"GeoTIFF\"\n")
    batch.write("-OutputOptions=\"INTERLEAVE=BAND,TILED=YES\"\n")
    batch.write("-PixelType=Uint16\n")
    batch.write("-Filter=hermit\n")
    batch.write("-saveraw=1\n")
    batch.write("-setExtent=0\n")
    batch.write("-Histogram=0\n\n")
    batch.write("\"auto\"\n")
    batch.write("\"auto\"\n")
    batch.write("infile gridstep %d \"%s\" %d\n"%(gridstep,oname,0))
    if msmode == 0:
        batch.write("infile gridstep %d \"%s\" %d\n"%(gridstep,name,0))
    else:
        batch.write("infile gridstep %d \"%s\" %d %d %d %d\n"%(gridstep,name,0,1,2,3))
    batch.write("ortho %f %d\n"%(height[2],gridstep))
    if msmode == 0:
        batch.write("mapping flt=%d dst=%d %d\n"%(2,0,1))
    else:
        batch.write("mapping flt=%d dst=%d %d\n"%(2,0,1))
        batch.write("mapping flt=%d dst=%d %d\n"%(2,0,2))
        batch.write("mapping flt=%d dst=%d %d\n"%(2,0,3))
        batch.write("mapping flt=%d dst=%d %d\n"%(2,0,4))
    batch.write("tilesBySize sizeNX=%d sizeNY=%d remain2Last=2 pOverNX=0 pOverNY=0\n"%(tsize[1],tsize[0]))
    if msmode == 0:
        batch.write("outfile \"%s\" %d\n"%(imname,2))
    else:
        batch.write("outfile \"%s\" %d %d %d %d\n"%(imname,5,6,7,8))
    batch.write("layout \"%d\"\n\n"%(1111))
    batch.write("\"auto\"\n")
    batch.write("\"auto\"\n")
    batch.write("infile gridstep %d \"%s\" %d\n"%(gridstep,oname,0))
    batch.write("relief srtm egmtowgs margin %f \"%s\"\n"%(0,relief_path))
    batch.write("outfile \"%s\" %d\n"%(relname,1))
    batch.write("layout \"%d\"\n"%(1111))
    batch.close()

if remap == 1:
    print "Remaping imagery"
    if (subprocess.call("%s %s"%(ip_path,bname))!=0):
        print "Error...\nRemaping failed"
        exit(1)
#try to read srtm met
#    relname = re.sub(".tif","R1C1.tif",relname)
    os.remove(relname)
    relmet = re.sub(".tif",".met",relname)
    met = open(relmet,'r')
    for ln in met:
        if re.match("\s+MIN\s+([0-9.]+)",ln):
            height[0] = float(re.findall("\s+MIN\s+([0-9.]+)",ln)[0])
        if re.match("\s+MAX\s+([0-9.]+)",ln):
            height[4] = float(re.findall("\s+MAX\s+([0-9.]+)",ln)[0])
        if re.match("\s+MEAN\s+([0-9.]+)",ln):
            height[2] = float(re.findall("\s+MEAN\s+([0-9.]+)",ln)[0])
            break
    met.close()
    height[1]=height[0]+(height[2]-height[0])/2.0
    height[3]=height[2]+(height[4]-height[2])/2.0
    print height
#rename TIFF to TIF
if rename == 1:
    print "Rename imagery"
    for root, dirs, files in os.walk(os.path.dirname(name)):
        for file in files:
            if file.lower().endswith(".tif"):
                tname = os.path.join(root,re.sub(".TIF",".TIFF",file,flags=re.IGNORECASE))
                if os.path.isfile(tname):
                    os.rename(os.path.join(root, file),os.path.join(root, file)+".bak")
                    os.rename(tname,os.path.join(root, file))
            if file.lower().endswith("_cor.xml"):
                xname = os.path.join(root,re.sub("_COR.XML",".XML",file,flags=re.IGNORECASE))
                if os.path.isfile(xname):
                    os.rename(os.path.join(root, xname),os.path.join(root, xname)+".bak")
                    os.rename(os.path.join(root, file),xname)
#calc RPC
if calc_rpc == 1:
    print "Generation of grids for RPC"
    for h in height:
        if (os.system("%s %s %d %f"%(rsmod,name,64,h))!=0):
            print "Error...\nGrid generation failed"
            exit(1)
#    NUM_CPUS = 5
#    import multiprocessing as mp
#    pool = mp.Pool(NUM_CPUS)
#    run_multi(pool,rsmod,name,height,64)
#    pool.close()
#    pool.join()    
    flist = open(flname,'w')
    flist.write("H File\n")
    for h in height:
        flist.write("%f %s\\%f%s\n"%(h,os.path.dirname(name),h,".gg0.ascii"))
    flist.close()
    irpc_name = re.sub(".XML","_INV_RPC.TXT",name,flags=re.IGNORECASE)
    drpc_name = re.sub(".XML","_RPC.TXT",name,flags=re.IGNORECASE)
    print "RPC calculation"
    p = subprocess.Popen([rpc_path,flname,drpc_name,irpc_name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate(b"input data that is passed to subprocess' stdin")
    rc = p.returncode
    if(rc !=1):
#    if (os.system("%s %s %s %s"%(rpc_path,flname,drpc_name,irpc_name))!=1):
        print "Error...\nRPC calculation failed"
        exit(1)
    if (os.system("%s %s"%(rpcconv,drpc_name))!=0):
        print "Error...\nRPC convertion failed"
        exit(1)
#temporary files cleaning
if cleanup == 1:
    print "Temporary files cleaning"
    for root, dirs, files in os.walk(os.path.dirname(name)):
        for file in files:
            if file.lower().endswith(".gg0.ascii"):
                os.remove(os.path.join(root, file))
            elif file.lower().endswith(".imd"):
                os.remove(os.path.join(root, file))
            elif file.lower().endswith(".met"):
                os.remove(os.path.join(root, file))
            elif file.lower().endswith("_rpc.txt"):
                os.remove(os.path.join(root, file))
            elif file.lower().endswith("flist"):
                os.remove(os.path.join(root, file))
            elif file.lower().endswith(".bak"):
                os.remove(os.path.join(root, file))
            elif file.lower().endswith(".batch"):
                os.remove(os.path.join(root, file))
            elif file.lower().endswith(".batch.log"):
                os.remove(os.path.join(root, file))
print "Done"
end_time = time.time()
print "Elapsed time %f sec"%(end_time-start_time)










