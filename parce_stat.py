import sys
import numpy as np

fname = sys.argv[0]
data = np.loadtxt("i:\RF\gronoaltaysk_epi\stat.txt", dtype=np.float_,skiprows=1,comments="#")
dx = data[:,2]-data[:,0]
max_disp = abs(np.min(dx))+abs(np.max(dx))
print "max_disp = %f"%(max_disp)
print "min par = %f"%(np.min(dx))
print "max par = %f"%(np.max(dx))
print "max height = %f"%(np.max(data[:,4]))
print "min height = %f"%(np.min(data[:,4]))

