from scipy import ndimage
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(1)
n = 10
l = 256
im = np.zeros((l, l))
points = l*np.random.random((2, n**2))
im[(points[0]).astype(np.int), (points[1]).astype(np.int)] = 1
im = ndimage.gaussian_filter(im, sigma=l/(4.*n))

mask = im > im.mean()

label_im, nb_labels = ndimage.label(mask)

plt.figure(figsize=(9,3))

plt.subplot(131)
plt.imshow(im)
plt.axis('off')
plt.subplot(132)
plt.imshow(mask, cmap=plt.cm.gray)
plt.axis('off')
plt.subplot(133)
plt.imshow(label_im, cmap=plt.cm.spectral)
plt.axis('off')

plt.subplots_adjust(wspace=0.02, hspace=0.02, top=1, bottom=0, left=0, right=1)
plt.show()
#Compute size, mean_value, etc. of each region:
sizes = ndimage.sum(mask, label_im, range(nb_labels + 1))
mean_vals = ndimage.sum(im, label_im, range(1, nb_labels + 1))
#Clean up small connect components
mask_size = sizes < 1000
remove_pixel = mask_size[label_im]
remove_pixel.shape
label_im[remove_pixel] = 0
plt.imshow(label_im)
#Now reassign labels with np.searchsorted:
labels = np.unique(label_im)
label_im = np.searchsorted(labels, label_im)

