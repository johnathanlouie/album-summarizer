from typing import List

from numpy import concatenate, ndarray, reshape, vstack
from sklearn.cluster import MeanShift

import cv2
from jl import (TEXT_CLUSTER_HISTOGRAM, Image, ImageDirectory, ListFile,
                Stopwatch, Url, hsvlist, readimg2)


def calchist(img: Image, channel: int, range: int) -> ndarray:
    """
    """
    histogram = cv2.calcHist(images=[img], channels=[channel], mask=None, histSize=[range], ranges=[0, range])
    histogram2 = reshape(histogram, (histogram.size))
    return histogram2


def scale_histogram(histogram: ndarray, height: int, width: int) -> ndarray:
    """
    """
    pixels = height * width
    return histogram / pixels


def cluster(images: List[Image], bandwidth: float) -> List[int]:
    """
    """
    c = list()
    for i in images:
        h, w, _ = i.shape
        x1 = calchist(i, 0, 180)
        x2 = calchist(i, 1, 256)
        x3 = calchist(i, 2, 256)
        c1 = scale_histogram(x1, h, w)
        c2 = scale_histogram(x2, h, w)
        c3 = scale_histogram(x3, h, w)
        c4 = concatenate((c1, c2, c3))
        c.append(c4)
        # c.append(c1)
    d = vstack(c)
    ms = MeanShift(bandwidth)
    ms.fit(d)
    results = ms.labels_.tolist()
    return results


def main(directory: Url) -> None:
    """
    """
    print('Reading image directory....')
    image_urls = ImageDirectory(directory).jpeg()
    print('Loading images....')
    images = readimg2(image_urls)
    print('Converting images to hue-saturation-value representation....')
    images2 = hsvlist(images)
    print('Clustering....')
    c = cluster(images2, .09)
    print('Saving....')
    ListFile(TEXT_CLUSTER_HISTOGRAM).write(c)
    return


# main()
