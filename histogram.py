from numpy import concatenate, reshape, vstack
from sklearn.cluster import MeanShift

import cv2 as cv
from jl import (TEXT_CLUSTER_HISTOGRAM, TEXT_URL_ALBUM, ListFile, Stopwatch,
                hsvlist, readimg2)


def calchist(img, channel, val):
    a = cv.calcHist([img], [channel], None, [val], [0, val])
    b = reshape(a, (a.size))
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
        c4 = concatenate((c1, c2, c3))
        c.append(c4)
        # c.append(c1)
    d = vstack(c)
    f = MeanShift(bandwidth).fit(d)
    return f.labels_


def main():
    sw = Stopwatch()
    print('reading urls')
    a = ListFile(TEXT_URL_ALBUM).read()
    print('reading images')
    b = readimg2(a)
    b = hsvlist(b)
    g = cluster(b, .09)
    ListFile(TEXT_CLUSTER_HISTOGRAM).write(g)
    sw.print()
    return


# main()
