import jl
import time
import cv2 as cv
import numpy as np
from sklearn.cluster import MeanShift


def calchist(img, channel, val):
    a = cv.calcHist([img], [channel], None, [val], [0, val])
    b = np.reshape(a, (a.size))
    return b


def norm(histogram, resolution):
    return histogram / resolution


def cluster(images, bandwidth):
    c = list()
    for i in images:
        h, w, _ = i.shape
        res = h * w
        c1 = norm(calchist(i, 0, 180), res)
        c2 = norm(calchist(i, 1, 256), res)
        c3 = norm(calchist(i, 2, 256), res)
        c4 = np.concatenate((c1, c2, c3))
        c.append(c4)
        # c.append(c1)
    d = np.vstack(c)
    f = MeanShift(bandwidth).fit(d)
    return f.labels_


def main():
    sw = jl.Stopwatch()
    print('reading urls')
    a = jl.readtxt(jl.TEXT_URL_ALBUM)
    print('reading images')
    b = jl.readimg2(a)
    b = jl.hsvlist(b)
    g = cluster(b, .09)
    jl.writetxt(jl.TEXT_CLUSTER_HISTOGRAM, g)
    sw.print()
    return


main()
