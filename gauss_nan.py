import scipy as sp
import scipy.ndimage

U=sp.randn(10,10)          # random array...
U[U<2]=np.nan              # ...with NaNs for testing

V=U.copy()
V[U!=U]=0
VV=sp.ndimage.gaussian_filter(V,sigma=2.0)

W=0*U.copy()+1
W[U!=U]=0
WW=sp.ndimage.gaussian_filter(W,sigma=2.0)

Z=VV/WW
