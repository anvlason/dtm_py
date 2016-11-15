import numpy as np
import re

class RPC:
    def __init__(self):
        self.LINE_OFF = 0
        self.SAMP_OFF = 0
        self.LAT_OFF = 0
        self.LONG_OFF = 0
        self.HEIGHT_OFF = 0
        self.LINE_SCALE = 0
        self.SAMP_SCALE = 0
        self.LAT_SCALE = 0
        self.LONG_SCALE = 0
        self.HEIGHT_SCALE = 0
        self.LINE_NUM_COEFF = np.zeros(21,dtype=np.float)
        self.LINE_DEN_COEFF = np.zeros(21,dtype=np.float)
        self.SAMP_NUM_COEFF = np.zeros(21,dtype=np.float)
        self.SAMP_DEN_COEFF = np.zeros(21,dtype=np.float)

def read_orthokit(fname):
    f = open(fname,"rt");
    lines = f.readlines()
    f.close()
    rpc = RPC()
    rpc.LINE_OFF = float(re.findall(r"[-+]?\d*\.\d+",lines[0])[0])
    rpc.SAMP_OFF = float(re.findall(r"[-+]?\d*\.\d+",lines[1])[0])
    rpc.LAT_OFF = float(re.findall(r"[-+]?\d*\.\d+",lines[2])[0])
    rpc.LONG_OFF = float(re.findall(r"[-+]?\d*\.\d+",lines[3])[0])
    rpc.HEIGHT_OFF = float(re.findall(r"[-+]?\d*\.\d+",lines[4])[0])
    rpc.LINE_SCALE = float(re.findall(r"[-+]?\d*\.\d+",lines[5])[0])
    rpc.SAMP_SCALE = float(re.findall(r"[-+]?\d*\.\d+",lines[6])[0])
    rpc.LAT_SCALE = float(re.findall(r"[-+]?\d*\.\d+",lines[7])[0])
    rpc.LONG_SCALE = float(re.findall(r"[-+]?\d*\.\d+",lines[8])[0])
    rpc.HEIGHT_SCALE = float(re.findall(r"[-+]?\d*\.\d+",lines[9])[0])
    j = 10
    jj = 30
    jjj = 50
    jjjj = 70
    for i in range(1,21):
        rpc.LINE_NUM_COEFF[i]=float(re.findall(r"[-+]?\d*\.\d+[eE][-+]?\d*",lines[j])[0])
        rpc.LINE_DEN_COEFF[i]=float(re.findall(r"[-+]?\d*\.\d+[eE][-+]?\d*",lines[jj])[0])
        rpc.SAMP_NUM_COEFF[i]=float(re.findall(r"[-+]?\d*\.\d+[eE][-+]?\d*",lines[jjj])[0])
        rpc.SAMP_DEN_COEFF[i]=float(re.findall(r"[-+]?\d*\.\d+[eE][-+]?\d*",lines[jjjj])[0])        
        j+=1
        jj+=1
        jjj+=1
        jjjj+=1
    return rpc

def calc_rfm_i(r,s,l,h):
    V = (s - r.SAMP_OFF - 0.5)/r.SAMP_SCALE
    U = (l - r.LINE_OFF - 0.5)/r.LINE_SCALE
    W = (h - r.HEIGHT_OFF)/r.HEIGHT_SCALE
    VU = V*U
    VW = V*W
    UW = U*W
    VV = V*V
    UU = U*U
    WW = W*W
    VVV = V*V*V
    UUU = U*U*U
    WWW = W*W*W
    UVW = U*V*W
    VUU = V*U*U
    VWW = V*W*W
    VVU = V*V*U
    VVW = V*V*W
    UWW = U*W*W
    UUW = U*U*W
    buf = np.zeros(21,dtype=np.float_)
    buf[0 ] = r.LINE_NUM_COEFF[1 ]*  1
    buf[1 ] = r.LINE_NUM_COEFF[2 ]*  V
    buf[2 ] = r.LINE_NUM_COEFF[3 ]*  U
    buf[3 ] = r.LINE_NUM_COEFF[4 ]*  W
    buf[4 ] = r.LINE_NUM_COEFF[5 ]* VU
    buf[5 ] = r.LINE_NUM_COEFF[6 ]* VW
    buf[6 ] = r.LINE_NUM_COEFF[7 ]* UW
    buf[7 ] = r.LINE_NUM_COEFF[8 ]* VV
    buf[8 ] = r.LINE_NUM_COEFF[9 ]* UU
    buf[9 ] = r.LINE_NUM_COEFF[10]* WW
    buf[10] = r.LINE_NUM_COEFF[11]*UVW
    buf[11] = r.LINE_NUM_COEFF[12]*VVV
    buf[12] = r.LINE_NUM_COEFF[13]*VUU
    buf[13] = r.LINE_NUM_COEFF[14]*VWW
    buf[14] = r.LINE_NUM_COEFF[15]*VVU
    buf[15] = r.LINE_NUM_COEFF[16]*UUU
    buf[16] = r.LINE_NUM_COEFF[17]*UWW
    buf[17] = r.LINE_NUM_COEFF[18]*VVW
    buf[18] = r.LINE_NUM_COEFF[19]*UUW
    buf[19] = r.LINE_NUM_COEFF[20]*WWW
    Nl = np.sum(buf[0:20])

    buf[0 ] = r.LINE_DEN_COEFF[1 ]  *1
    buf[1 ] = r.LINE_DEN_COEFF[2 ]  *V
    buf[2 ] = r.LINE_DEN_COEFF[3 ]  *U
    buf[3 ] = r.LINE_DEN_COEFF[4 ]  *W
    buf[4 ] = r.LINE_DEN_COEFF[5 ] *VU
    buf[5 ] = r.LINE_DEN_COEFF[6 ] *VW
    buf[6 ] = r.LINE_DEN_COEFF[7 ] *UW
    buf[7 ] = r.LINE_DEN_COEFF[8 ] *VV
    buf[8 ] = r.LINE_DEN_COEFF[9 ] *UU
    buf[9 ] = r.LINE_DEN_COEFF[10] *WW
    buf[10] = r.LINE_DEN_COEFF[11]*UVW
    buf[11] = r.LINE_DEN_COEFF[12]*VVV
    buf[12] = r.LINE_DEN_COEFF[13]*VUU
    buf[13] = r.LINE_DEN_COEFF[14]*VWW
    buf[14] = r.LINE_DEN_COEFF[15]*VVU
    buf[15] = r.LINE_DEN_COEFF[16]*UUU
    buf[16] = r.LINE_DEN_COEFF[17]*UWW
    buf[17] = r.LINE_DEN_COEFF[18]*VVW
    buf[18] = r.LINE_DEN_COEFF[19]*UUW
    buf[19] = r.LINE_DEN_COEFF[20]*WWW
    Dl = np.sum(buf[0:20])

    buf[0 ] = r.SAMP_NUM_COEFF[1 ]  *1
    buf[1 ] = r.SAMP_NUM_COEFF[2 ]  *V
    buf[2 ] = r.SAMP_NUM_COEFF[3 ]  *U
    buf[3 ] = r.SAMP_NUM_COEFF[4 ]  *W
    buf[4 ] = r.SAMP_NUM_COEFF[5 ] *VU
    buf[5 ] = r.SAMP_NUM_COEFF[6 ] *VW
    buf[6 ] = r.SAMP_NUM_COEFF[7 ] *UW
    buf[7 ] = r.SAMP_NUM_COEFF[8 ] *VV
    buf[8 ] = r.SAMP_NUM_COEFF[9 ] *UU
    buf[9 ] = r.SAMP_NUM_COEFF[10] *WW
    buf[10] = r.SAMP_NUM_COEFF[11]*UVW
    buf[11] = r.SAMP_NUM_COEFF[12]*VVV
    buf[12] = r.SAMP_NUM_COEFF[13]*VUU
    buf[13] = r.SAMP_NUM_COEFF[14]*VWW
    buf[14] = r.SAMP_NUM_COEFF[15]*VVU
    buf[15] = r.SAMP_NUM_COEFF[16]*UUU
    buf[16] = r.SAMP_NUM_COEFF[17]*UWW
    buf[17] = r.SAMP_NUM_COEFF[18]*VVW
    buf[18] = r.SAMP_NUM_COEFF[19]*UUW
    buf[19] = r.SAMP_NUM_COEFF[20]*WWW
    Ns = np.sum(buf[0:20])

    buf[0 ] = r.SAMP_DEN_COEFF[1 ]  *1;
    buf[1 ] = r.SAMP_DEN_COEFF[2 ]  *V;
    buf[2 ] = r.SAMP_DEN_COEFF[3 ]  *U;
    buf[3 ] = r.SAMP_DEN_COEFF[4 ]  *W;
    buf[4 ] = r.SAMP_DEN_COEFF[5 ] *VU;
    buf[5 ] = r.SAMP_DEN_COEFF[6 ] *VW;
    buf[6 ] = r.SAMP_DEN_COEFF[7 ] *UW;
    buf[7 ] = r.SAMP_DEN_COEFF[8 ] *VV;
    buf[8 ] = r.SAMP_DEN_COEFF[9 ] *UU;
    buf[9 ] = r.SAMP_DEN_COEFF[10] *WW;
    buf[10] = r.SAMP_DEN_COEFF[11]*UVW;
    buf[11] = r.SAMP_DEN_COEFF[12]*VVV;
    buf[12] = r.SAMP_DEN_COEFF[13]*VUU;
    buf[13] = r.SAMP_DEN_COEFF[14]*VWW;
    buf[14] = r.SAMP_DEN_COEFF[15]*VVU;
    buf[15] = r.SAMP_DEN_COEFF[16]*UUU;
    buf[16] = r.SAMP_DEN_COEFF[17]*UWW;
    buf[17] = r.SAMP_DEN_COEFF[18]*VVW;
    buf[18] = r.SAMP_DEN_COEFF[19]*UUW;
    buf[19] = r.SAMP_DEN_COEFF[20]*WWW;
    Ds = np.sum(buf[0:20])

    X=Ns/Ds
    Y=Nl/Dl
    lon  = X * r.LONG_SCALE  +  r.LONG_OFF
    lat  = Y * r.LAT_SCALE  +  r.LAT_OFF

    return lon,lat

def calc_rfm_d(r,lon,lat,h):
    V = (lon - r.LONG_OFF)/r.LONG_SCALE
    U = (lat - r.LAT_OFF)/r.LAT_SCALE
    W = (h - r.HEIGHT_OFF)/r.HEIGHT_SCALE
    VU = V*U
    VW = V*W
    UW = U*W
    VV = V*V
    UU = U*U
    WW = W*W
    VVV = V*V*V
    UUU = U*U*U
    WWW = W*W*W
    UVW = U*V*W
    VUU = V*U*U
    VWW = V*W*W
    VVU = V*V*U
    VVW = V*V*W
    UWW = U*W*W
    UUW = U*U*W
    buf = np.zeros(21,dtype=np.float_)
    buf[0 ] = r.LINE_NUM_COEFF[1 ]*  1
    buf[1 ] = r.LINE_NUM_COEFF[2 ]*  V
    buf[2 ] = r.LINE_NUM_COEFF[3 ]*  U
    buf[3 ] = r.LINE_NUM_COEFF[4 ]*  W
    buf[4 ] = r.LINE_NUM_COEFF[5 ]* VU
    buf[5 ] = r.LINE_NUM_COEFF[6 ]* VW
    buf[6 ] = r.LINE_NUM_COEFF[7 ]* UW
    buf[7 ] = r.LINE_NUM_COEFF[8 ]* VV
    buf[8 ] = r.LINE_NUM_COEFF[9 ]* UU
    buf[9 ] = r.LINE_NUM_COEFF[10]* WW
    buf[10] = r.LINE_NUM_COEFF[11]*UVW
    buf[11] = r.LINE_NUM_COEFF[12]*VVV
    buf[12] = r.LINE_NUM_COEFF[13]*VUU
    buf[13] = r.LINE_NUM_COEFF[14]*VWW
    buf[14] = r.LINE_NUM_COEFF[15]*VVU
    buf[15] = r.LINE_NUM_COEFF[16]*UUU
    buf[16] = r.LINE_NUM_COEFF[17]*UWW
    buf[17] = r.LINE_NUM_COEFF[18]*VVW
    buf[18] = r.LINE_NUM_COEFF[19]*UUW
    buf[19] = r.LINE_NUM_COEFF[20]*WWW
    Nl = np.sum(buf[0:20])

    buf[0 ] = r.LINE_DEN_COEFF[1 ]  *1
    buf[1 ] = r.LINE_DEN_COEFF[2 ]  *V
    buf[2 ] = r.LINE_DEN_COEFF[3 ]  *U
    buf[3 ] = r.LINE_DEN_COEFF[4 ]  *W
    buf[4 ] = r.LINE_DEN_COEFF[5 ] *VU
    buf[5 ] = r.LINE_DEN_COEFF[6 ] *VW
    buf[6 ] = r.LINE_DEN_COEFF[7 ] *UW
    buf[7 ] = r.LINE_DEN_COEFF[8 ] *VV
    buf[8 ] = r.LINE_DEN_COEFF[9 ] *UU
    buf[9 ] = r.LINE_DEN_COEFF[10] *WW
    buf[10] = r.LINE_DEN_COEFF[11]*UVW
    buf[11] = r.LINE_DEN_COEFF[12]*VVV
    buf[12] = r.LINE_DEN_COEFF[13]*VUU
    buf[13] = r.LINE_DEN_COEFF[14]*VWW
    buf[14] = r.LINE_DEN_COEFF[15]*VVU
    buf[15] = r.LINE_DEN_COEFF[16]*UUU
    buf[16] = r.LINE_DEN_COEFF[17]*UWW
    buf[17] = r.LINE_DEN_COEFF[18]*VVW
    buf[18] = r.LINE_DEN_COEFF[19]*UUW
    buf[19] = r.LINE_DEN_COEFF[20]*WWW
    Dl = np.sum(buf[0:20])

    buf[0 ] = r.SAMP_NUM_COEFF[1 ]  *1
    buf[1 ] = r.SAMP_NUM_COEFF[2 ]  *V
    buf[2 ] = r.SAMP_NUM_COEFF[3 ]  *U
    buf[3 ] = r.SAMP_NUM_COEFF[4 ]  *W
    buf[4 ] = r.SAMP_NUM_COEFF[5 ] *VU
    buf[5 ] = r.SAMP_NUM_COEFF[6 ] *VW
    buf[6 ] = r.SAMP_NUM_COEFF[7 ] *UW
    buf[7 ] = r.SAMP_NUM_COEFF[8 ] *VV
    buf[8 ] = r.SAMP_NUM_COEFF[9 ] *UU
    buf[9 ] = r.SAMP_NUM_COEFF[10] *WW
    buf[10] = r.SAMP_NUM_COEFF[11]*UVW
    buf[11] = r.SAMP_NUM_COEFF[12]*VVV
    buf[12] = r.SAMP_NUM_COEFF[13]*VUU
    buf[13] = r.SAMP_NUM_COEFF[14]*VWW
    buf[14] = r.SAMP_NUM_COEFF[15]*VVU
    buf[15] = r.SAMP_NUM_COEFF[16]*UUU
    buf[16] = r.SAMP_NUM_COEFF[17]*UWW
    buf[17] = r.SAMP_NUM_COEFF[18]*VVW
    buf[18] = r.SAMP_NUM_COEFF[19]*UUW
    buf[19] = r.SAMP_NUM_COEFF[20]*WWW
    Ns = np.sum(buf[0:20])

    buf[0 ] = r.SAMP_DEN_COEFF[1 ]  *1;
    buf[1 ] = r.SAMP_DEN_COEFF[2 ]  *V;
    buf[2 ] = r.SAMP_DEN_COEFF[3 ]  *U;
    buf[3 ] = r.SAMP_DEN_COEFF[4 ]  *W;
    buf[4 ] = r.SAMP_DEN_COEFF[5 ] *VU;
    buf[5 ] = r.SAMP_DEN_COEFF[6 ] *VW;
    buf[6 ] = r.SAMP_DEN_COEFF[7 ] *UW;
    buf[7 ] = r.SAMP_DEN_COEFF[8 ] *VV;
    buf[8 ] = r.SAMP_DEN_COEFF[9 ] *UU;
    buf[9 ] = r.SAMP_DEN_COEFF[10] *WW;
    buf[10] = r.SAMP_DEN_COEFF[11]*UVW;
    buf[11] = r.SAMP_DEN_COEFF[12]*VVV;
    buf[12] = r.SAMP_DEN_COEFF[13]*VUU;
    buf[13] = r.SAMP_DEN_COEFF[14]*VWW;
    buf[14] = r.SAMP_DEN_COEFF[15]*VVU;
    buf[15] = r.SAMP_DEN_COEFF[16]*UUU;
    buf[16] = r.SAMP_DEN_COEFF[17]*UWW;
    buf[17] = r.SAMP_DEN_COEFF[18]*VVW;
    buf[18] = r.SAMP_DEN_COEFF[19]*UUW;
    buf[19] = r.SAMP_DEN_COEFF[20]*WWW;
    Ds = np.sum(buf[0:20])

    X=Ns/Ds
    Y=Nl/Dl
    s  = X * r.SAMP_SCALE  +  r.SAMP_OFF + 0.5
    l  = Y * r.LINE_SCALE  +  r.LINE_OFF + 0.5

    return s,l
