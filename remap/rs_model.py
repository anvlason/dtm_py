import numpy as np
import pyproj
from xml.dom import minidom
#import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D
from scipy import stats
from scipy import interpolate
import re
import sys
import os

#C1A_dx = 6992-6977 #15
#C1A_dy = 414
pr_width = 6992

c1_tanpsixA = np.array([-7.3034718975430004e-16,3.5572177896699068e-12,3.1478173429705174e-06,-0.00029921962179080074],dtype=np.float_)
c1_tanpsiyA = np.array([-3.3769522298186612e-17,4.0166990826268786e-12,1.6183243381077438e-08,-0.0019222411677056485],dtype=np.float_)
c1_tanpsixB = np.array([-6.8418152985104859e-16,1.7511052090106396e-11,3.0144720107619574e-06,-0.021469360379009563],dtype=np.float_)
c1_tanpsiyB = np.array([4.1426605251299866e-17,2.2556215956045086e-12,-6.0137496578202653e-08,0.0019989167057853511],dtype=np.float_)

c2_tanpsixA = np.array([-7.0983688885429144e-16,3.9027800355408196e-13,3.162504015449916e-06,-0.00027391308094523595],dtype=np.float_)
c2_tanpsiyA = np.array([-3.9640461405024627e-17,4.1167631886158308e-12,1.6730356605220181e-08,-0.0019270559359486877],dtype=np.float_)
c2_tanpsixB = np.array([-7.2337896358514762e-16,1.5408224529989014e-11,3.06241992946334e-06,-0.021648544658619019],dtype=np.float_)
c2_tanpsiyB = np.array([2.9342068454518549e-17,2.5483098087787894e-12,-6.3071868587214056e-08,0.0020080456587679811],dtype=np.float_)

CSF1_TO_ISF = np.array([0.99994377236285159,-0.010583635965803584,4.8100329467639325e-05,-0.00066064275623463082],dtype=np.float_)
#CSF1_TO_ISF = np.array([-0.99994377236285159,0.010583635965803584,-4.8100329467639325e-05,0.00066064275623463082],dtype=np.float_)
CSF2_TO_ISF = np.array([0.99994377178761795,0.010583690313834142,-3.410629429344461e-05,0.00066151285233566348],dtype=np.float_)
#CSF2_TO_ISF = np.array([-0.99994377178761795,-0.010583690313834142,3.410629429344461e-05,-0.00066151285233566348],dtype=np.float_)

ISF_TO_RATT = [1, 0, 0, 0]

c_tanpsixRS = np.array([-0.0427997144900000, 0.0000022171403835],dtype=np.float_)
c_tanpsiyRS = [0.0, 0.0]



#pos = [733526.0321830204, 3729980.604078132, 5960846.761069546]
#att = [0.01570974166639381, 0.7747520630988693, 0.5966291707165694, -0.2086769689996465]

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
    pos=np.zeros((pcount,4),dtype=np.float_)
    for i in range(0,pcount):
            pt=poslist[i].getElementsByTagName("LOCATION_VALUES")[0]
            pos[i,0:3]=map(np.float_,pt.firstChild.nodeValue.split(" "))
            pos[i,3]=getdatetime(poslist[i].getElementsByTagName("UTC_TIME")[0].firstChild.nodeValue)[1]
    xmldoc=None
    return pos


def readIAPretina(name,cam,retina):
    xmldoc = minidom.parse(name)
    rlist=xmldoc.getElementsByTagName(cam)[0].getElementsByTagName(retina)[0].getElementsByTagName('Barrette')
    retpar = np.zeros((len(rlist),5),dtype=np.float_)
    for i in range (0, len(rlist)): #Pan, B0,B1, B2, B3
        retpar[i,0]=getdatetime(rlist[0].getElementsByTagName('UTC_ReferenceTime')[0].firstChild.nodeValue)[1] #reference line JD
        retpar[i,1]=np.float_(rlist[0].getElementsByTagName('ReferenceLinePeriod')[0].firstChild.nodeValue)*1e-3 #reference line period in sec
        retpar[i,2]=np.float_(rlist[0].getElementsByTagName('IndexOfReferenceLine')[0].firstChild.nodeValue) #reference line num
        retpar[i,3]=np.float_(rlist[0].getElementsByTagName('StartValidLine')[0].firstChild.nodeValue) #first valid line
        retpar[i,4]=np.float_(rlist[0].getElementsByTagName('EndValidLine')[0].firstChild.nodeValue) #end valid line

    xmldoc=None
    return retpar
#read camera parameters from DIMAP
def readDIMcamera(name):
    xmldoc = minidom.parse(name)
    TimeRange = xmldoc.getElementsByTagName('Time_Range')
    stime = getdatetime(TimeRange[0].getElementsByTagName('START')[0].firstChild.nodeValue)[1]
    etime = getdatetime(TimeRange[0].getElementsByTagName('END')[0].firstChild.nodeValue)[1]
    linper = np.float_(xmldoc.getElementsByTagName('LINE_PERIOD')[0].firstChild.nodeValue)*1e-6
    firstcol = int(xmldoc.getElementsByTagName('FIRST_COL')[0].firstChild.nodeValue)
    lastcol = int(xmldoc.getElementsByTagName('LAST_COL')[0].firstChild.nodeValue)
    tanpsix = np.array([np.float_(xmldoc.getElementsByTagName('XLOS_0')[0].firstChild.nodeValue),np.float_(xmldoc.getElementsByTagName('XLOS_1')[0].firstChild.nodeValue)])
    tanpsiy = np.array([np.float_(xmldoc.getElementsByTagName('YLOS_0')[0].firstChild.nodeValue),np.float_(xmldoc.getElementsByTagName('YLOS_1')[0].firstChild.nodeValue)])
    RastDim = xmldoc.getElementsByTagName('Raster_Dimensions')
    imsize = np.array([int(RastDim[0].getElementsByTagName('NROWS')[0].firstChild.nodeValue),int(RastDim[0].getElementsByTagName('NCOLS')[0].firstChild.nodeValue)])

    xmldoc=None
    return (stime,etime,linper,firstcol,lastcol,tanpsix,tanpsiy,imsize)

#calc directions for all retina
def getdir_rn_all(width,colref,c_tanpsix,c_tanpsiy):
    visdir=np.zeros((3,width),dtype=np.float_)
    for i in range(1,width):
        tanpsix = np.float_(c_tanpsix[0]*(i-colref)**3+c_tanpsix[1]*(i-colref)**2+c_tanpsix[2]*(i-colref)+c_tanpsix[3])
        tanpsiy = np.float_(c_tanpsiy[0]*(i-colref)**3+c_tanpsiy[1]*(i-colref)**2+c_tanpsiy[2]*(i-colref)+c_tanpsiy[3])
        norm = 1/np.sqrt(1+tanpsix*tanpsix+tanpsiy*tanpsiy)
        visdir[0,i]=tanpsiy*norm
        visdir[1,i]=-tanpsix*norm
        visdir[2,i]=1*norm
#    print np.float_(norm)
#    return (tanpsiy*norm,-tanpsix*norm,1*norm)
    return visdir


#transformation matrix from quaternion
def quat2matrix(Q):
    w = np.float_(Q[0])
    x = np.float_(Q[1])
    y = np.float_(Q[2])
    z = np.float_(Q[3])
    ww = np.float_(w*w)
    xx = np.float_(x*x)
    yy = np.float_(y*y)
    zz = np.float_(z*z)
    mat = np.zeros((3,3),dtype=np.float_)
    mat[0,:]=[ww+xx-yy-zz , 2.*(x*y-w*z), 2.*(x*z+w*y)]
    mat[1,:]=[2.*(x*y+w*z), ww-xx+yy-zz , 2.*(y*z-w*x)]
    mat[2,:]=[2.*(x*z-w*y), 2.*(y*z+w*x), ww-xx-yy+zz]
    return mat

def quat2rpy(Q):
    r = np.float_(np.arctan2(2*(Q[0]*Q[1]+Q[2]*Q[3]),1-2*(Q[1]*Q[1]+Q[2]*Q[2])))
    p = np.float_(np.arcsin(2*(Q[0]*Q[2]-Q[3]*Q[1])))
    y = np.float_(np.arctan2(2*(Q[0]*Q[3]+Q[1]*Q[2]),1-2*(Q[2]*Q[2]+Q[3]*Q[3])))
    return np.float_([r,p,y])

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

    
def TransVis(vis,Q):
    w = Q[0]
    x = Q[1]
    y = Q[2]
    z = Q[3]
    ww = w*w
    xx = x*x
    yy = y*y
    zz = z*z
    mat = np.zeros((3,3))
    mat[0,:]=[ww+xx-yy-zz, 2.*(x*y-w*z), 2.*(x*z+w*y)]
    mat[1,:]=[2.*(x*y+w*y), ww-xx+yy-zz, 2.*(y*z-w*x)]
    mat[2,:]=[2.*(x*z-w*y), 2.*(y*z+w*x), ww-xx-yy-zz]
    visout = np.matrix(mat,dtype=np.float_)*np.matrix(vis,dtype=np.float_).T
    return(visout[0,0],visout[1,0],visout[2,0])

#trace to ground on constatne h
def pos2ll(pos,vis,h):
    EARTH_A = 6378137.0
    EARTH_B = 6356752.314245
#    EARTH_ES= np.float_(1.0-(EARTH_B/EARTH_A)*(EARTH_B/EARTH_A))
    ae2  = np.float_((EARTH_A+h) * (EARTH_A+h))
    be2  = np.float_((EARTH_B+h) * (EARTH_B+h))
    a = np.float_(vis[0] * vis[0] / ae2 + vis[1] * vis[1] / ae2 + vis[2] * vis[2] / be2)
    b = np.float_((pos[0] * vis[0] / ae2 + pos[1] * vis[1] / ae2 + pos[2] * vis[2] / be2)*2)
    c = np.float_(pos[0] * pos[0] / ae2 + pos[1] * pos[1] / ae2 + pos[2] * pos[2] / be2 - 1)
    D = np.float_(b*b - 4*c*a)
    if(D <= 0): return (-9999.0,-9999.0)
    t = np.float_((-b - np.sqrt(D)) / (2*a))
    tt = np.float_((-b + np.sqrt(D)) / (2*a))
    if(np.absolute(tt)<np.absolute(t)): t=tt
    x = pos[0] + t*vis[0]
    y = pos[1] + t*vis[1]
    z = pos[2] + t*vis[2]
#    print (x,y,z)
    pj_str = "+proj=geocent +a=%f +b=%f +units=m +no_defs" % (EARTH_A,EARTH_B)
    geocentric = pyproj.Proj(pj_str)
    lonlat = pyproj.Proj('+proj=longlat +datum=WGS84 +no_defs')
#    lonlat = pyproj.Proj('+proj=utm +zone=44  +ellps=WGS84 +datum=WGS84 +units=m +no_defs')
    lon, lat, h = np.float_(pyproj.transform(geocentric,lonlat,x,y,z,radians=False))
    return (lon,lat)

#calc direction for RS sensor
def getdir(col,colref,c_tanpsix,c_tanpsiy):
    tanpsix = np.float_(c_tanpsix[0]+c_tanpsix[1]*(col+colref))
    tanpsiy = np.float_(c_tanpsiy[0]+c_tanpsiy[0]*(col+colref))
#    return (tanpsiy,-tanpsix,1)
    return (-tanpsiy,tanpsix,-1)

#calc directions for all RS sensor
def getdir_rs_all(width,colref,c_tanpsix,c_tanpsiy):
    visdir=np.zeros((3,width),dtype=np.float_)
    for i in range(1,width):
        tanpsix = np.float_(c_tanpsix[1]*(i+colref)+c_tanpsix[0])
        tanpsiy = np.float_(c_tanpsiy[1]*(i+colref)+c_tanpsiy[0])
        norm = 1/np.sqrt(1+tanpsix*tanpsix+tanpsiy*tanpsiy)
        visdir[0,i]=tanpsiy*norm
        visdir[1,i]=-tanpsix*norm
        visdir[2,i]=1*norm
    return visdir

#normalization 
def norm(data):
    s=np.float_(0.0)
    for i in range(0,len(data)):
        s+=data[i]*data[i]
    n = np.float_(1/np.sqrt(s))
    return (np.array(data,dtype=np.float_)*n)

#rotation by matrix
def rotate(vdirn,mat):
    rvdirn=np.matrix(mat,dtype=np.float_)*np.matrix(vdirn,dtype=np.float_).T
    return(rvdirn[0,0],rvdirn[1,0],rvdirn[2,0])

#rotation by matrix.T
def rotateT(vdirn,mat):
    rvdirn=np.matrix(mat,dtype=np.float_).T*np.matrix(vdirn,dtype=np.float_).T
    return(rvdirn[0,0],rvdirn[1,0],rvdirn[2,0])


def rpy2quat(r,p,y): #xyz - bha (bank,heading, attitude)
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
    return (w,x,y,z)

def rotatev_aroundx(p,a): #
    x=p[0]
    y=p[1]
    z=p[2]
    cs=np.float_(np.cos(a))
    cn=np.float_(np.sin(a))
    return np.float_(np.array([x,cs*y-cn*z,cn*y+cs*z]))

def rotatev_aroundy(p,a): #
    x=p[0]
    y=p[1]
    z=p[2]    
    cs=np.float_(np.cos(a))
    cn=np.float_(np.sin(a))
    return np.float_(np.array([cs*x-cn*z,y,cn*x+cs*z]))

def rotatev_aroundz(p,a): #
    x=p[0]
    y=p[1]
    z=p[2]    
    cs=np.float_(np.cos(a))
    cn=np.float_(np.sin(a))
    return np.float_(np.array([cs*x-cn*y,cn*x+cs*y,z]))

    
def tracebeam(col,offset,psix,psiy,camq,pos,att,h):
    vdir = getdir_rn(col,offset,psix,psiy)
    vdir = rotate(vdir,camq)
    vdir = rotate(vdir,att)
    lon,lat=pos2ll(pos,vdir,h)
    return (lon,lat)
# get time for cur line
def getTbyline(line,tfl,lineper):
    t=line*lineper/86400.0+tfl
    return t

def fitQuat(q,model):
    fit_w = interpolate.interp1d(q[:,4],q[:,0],kind=model,bounds_error=False)
    fit_x = interpolate.interp1d(q[:,4],q[:,1],kind=model,bounds_error=False)
    fit_y = interpolate.interp1d(q[:,4],q[:,2],kind=model,bounds_error=False)
    fit_z = interpolate.interp1d(q[:,4],q[:,3],kind=model,bounds_error=False)
    return (fit_w,fit_x,fit_y,fit_z)
    #return (fit_w(jd)[0],fit_x(jd)[0],fit_y(jd)[0],fit_z(jd)[0])
    
def fitPos(pos,model):
    fit_x = interpolate.interp1d(pos[:,6],pos[:,0],kind=model,bounds_error=False)
    fit_y = interpolate.interp1d(pos[:,6],pos[:,1],kind=model,bounds_error=False)
    fit_z = interpolate.interp1d(pos[:,6],pos[:,2],kind=model,bounds_error=False)
    return (fit_x,fit_y,fit_z)
    #return (fit_x(jd)[0],fit_y(jd)[0],fit_z(jd)[0])

def fitQuatS(q,order):
    fit_w = interpolate.InterpolatedUnivariateSpline(q[:,4],q[:,0],k=order)
    fit_x = interpolate.InterpolatedUnivariateSpline(q[:,4],q[:,1],k=order)
    fit_y = interpolate.InterpolatedUnivariateSpline(q[:,4],q[:,2],k=order)
    fit_z = interpolate.InterpolatedUnivariateSpline(q[:,4],q[:,3],k=order)
    return (fit_w,fit_x,fit_y,fit_z)
    #return (fit_w(jd)[0],fit_x(jd)[0],fit_y(jd)[0],fit_z(jd)[0])
    
def fitPosS(pos,order):
    fit_x = interpolate.InterpolatedUnivariateSpline(pos[:,6],pos[:,0],k=order)
    fit_y = interpolate.InterpolatedUnivariateSpline(pos[:,6],pos[:,1],k=order)
    fit_z = interpolate.InterpolatedUnivariateSpline(pos[:,6],pos[:,2],k=order)
    return (fit_x,fit_y,fit_z)
    #return (fit_x(jd)[0],fit_y(jd)[0],fit_z(jd)[0])



def GetTrendQuat(q):
    fit_w = np.poly1d(np.polyfit(q[:,4],q[:,0],1))
    fit_x = np.poly1d(np.polyfit(q[:,4],q[:,1],1))
    fit_y = np.poly1d(np.polyfit(q[:,4],q[:,2],1))
    fit_z = np.poly1d(np.polyfit(q[:,4],q[:,3],1))
    return (fit_w,fit_x,fit_y,fit_z)

def DeTrendQuat(q,trend):
    detrended = np.zeros((len(q),5),dtype=np.float_)
    detrended[:,0] = q[:,0]-trend[0](q[:,4])
    detrended[:,1] = q[:,1]-trend[1](q[:,4])
    detrended[:,2] = q[:,2]-trend[2](q[:,4])
    detrended[:,3] = q[:,3]-trend[3](q[:,4])
    detrended[:,4] = q[:,4]
    return detrended

def fitPoly3(q):
    fit_w = np.poly1d(np.polyfit(q[:,4],q[:,0],3))
    fit_x = np.poly1d(np.polyfit(q[:,4],q[:,1],3))
    fit_y = np.poly1d(np.polyfit(q[:,4],q[:,2],3))
    fit_z = np.poly1d(np.polyfit(q[:,4],q[:,3],3))
    return (fit_w,fit_x,fit_y,fit_z)

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


#mata = quat2matrix(CSF1_TO_ISF)
#matb = quat2matrix(CSF2_TO_ISF)
if len(sys.argv)<3:
    name = "niitp\\DIM_SPOT7_P_20150401051933870_SEN_RS-DS-00_000000.XML"
    step = 128
    h = 0
else:
    if os.path.exists(sys.argv[1]):
        name = sys.argv[1]
    else:
        print "ERROR...\nInput DIM file does not exists\n"
        exit(1)
    step = int(sys.argv[2])
    h = float(sys.argv[3])
ticname = re.sub(".XML",".tic",name,flags=re.IGNORECASE)
#ggname = re.sub(".XML",".gg0.ascii",name,flags=re.IGNORECASE)
ggname = ("%s\\%f.gg0.ascii"%(os.path.dirname(name),h))
stime,etime,linper,firstcol,lastcol,tanpsix,tanpsiy,imsize = readDIMcamera(name)
tshift = 0#stime+10*linper
quat = readDIMquat(name)
pos = readDIMpos(name)
#step = 128
usetic = 0
usegg = 1
psi = getdir_rs_all(imsize[1]+step*2,0,tanpsix,tanpsiy)
interp = 'cubic'
order = 3
#fit_q = fitQuat(quat,interp)
#fit_p = fitPos(pos,interp)
fit_q = fitQuatS(quat,order)
fit_p = fitPosS(pos,order)
line_shift = 0
x_shift = 0
y_shift = 0


if usetic == 1:
    tic = open(ticname,'w')
#write header
    tic.write("proj=+proj=longlat +ellps=WGS84 +towgs84=0,0,0,-0,-0,-0,0 +no_defs\n")
    tic.write("prjf=rast\n")
    tic.write("prjt=proj\n")
#write points
    i = 0
    for y in (range(0,imsize[0]+step-1,step)):
        t = getTbyline(y+line_shift,stime+tshift,linper)
        q = np.zeros((1,4),dtype=np.float_)
        p = np.zeros((1,3),dtype=np.float_)
        q[0,0] = np.float_(fit_q[0](t))
        q[0,1] = np.float_(fit_q[1](t))
        q[0,2] = np.float_(fit_q[2](t))
        q[0,3] = np.float_(fit_q[3](t))
        p[0,0] = np.float_(fit_p[0](t))
        p[0,1] = np.float_(fit_p[1](t))
        p[0,2] = np.float_(fit_p[2](t))
        p=p[0]
        mat = quat2matrix(q[0])
        for x in range(0,lastcol+step-1,step):
            sdir = [psi[0,x+firstcol],psi[1,x+firstcol],psi[2,x+firstcol]]
            sdir = rotate(sdir,mat)
            lon,lat=pos2ll(p,sdir,h)
            if(np.isnan(lon)==False and np.isnan(lat)==False):
                tic.write("%f %f %.16f %.16f %f \"%s\"\n" %(x+x_shift,y+y_shift,lon,lat,t,str(y)))      
        i+=1
#        print i

    tic.close()

if usegg == 1:
#write header    
    gg = open(ggname,'w')
    gg.write("nSamples    %d\n"%((imsize[1]+step)/step+1))#(len(range(0,imsize[1]+step-1,step))))
    gg.write("nLines      %d\n"%((imsize[0]+step)/step+1))#(len(range(0,imsize[0]+step/2,step))))
    gg.write("start_pixel %f\n"%(0))
    gg.write("start_line  %f\n"%(0))
    gg.write("step_pixel  %f\n"%(step))
    gg.write("step_line   %f\n"%(step))
    gg.write("x0          %d\n"%(0))
    gg.write("y0          %d\n"%(0))
    gg.write("x1          %d\n"%(imsize[1]))
    gg.write("y1          %d\n"%(imsize[0]))
    gg.write("separate    %d\n"%(0))
    gg.write("delimiter   %d\n"%(32))
    gg.write("points\n")
#write points
    i = 0    
#    for y in (range(0,imsize[0]+step/2,step)):
    for y in (range(0,imsize[0]+step,step)):
        t = getTbyline(y+line_shift,stime,linper)
        q = np.zeros((1,4),dtype=np.float_)
        p = np.zeros((1,3),dtype=np.float_)
        q[0,0] = np.float_(fit_q[0](t))
        q[0,1] = np.float_(fit_q[1](t))
        q[0,2] = np.float_(fit_q[2](t))
        q[0,3] = np.float_(fit_q[3](t))
        p[0,0] = np.float_(fit_p[0](t))
        p[0,1] = np.float_(fit_p[1](t))
        p[0,2] = np.float_(fit_p[2](t))
        p=p[0]
        mat = quat2matrix(q[0])
        llstr = ''
        for x in range(0,lastcol+step,step):
#            print "%d\n"%x
            sdir = [psi[0,x+firstcol],psi[1,x+firstcol],psi[2,x+firstcol]]
            sdir = rotate(sdir,mat)
            lon,lat=pos2ll(p,sdir,h)
            llstr +=str("%.12f %.12f "%(lon,lat))
        llstr +=str("\n")
        gg.write(llstr)
        i+=1        
#        print i
    gg.close()
    
