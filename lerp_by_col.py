lrp[mask] = np.interp(np.flatnonzero(mask),np.flatnonzero(~mask),lrp[~mask])
