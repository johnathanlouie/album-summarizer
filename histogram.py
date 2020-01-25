from typing import List

from numpy import concatenate, ndarray, reshape, vstack
from sklearn.cluster import MeanShift

import cv2
from jl import (TEXT_CLUSTER_HISTOGRAM, Image, ImageDirectory, ListFile,
                Stopwatch, Url, hsv, hsvlist, read_image, readimg2)


Histogram = ndarray


class HsvHistogram(object):
    """
    hue-saturation-value
    """

    def __init__(self, image: Url) -> None:
        self._url = image
        self._image = hsv(read_image(image))
        return

    def _histogram(self, channel: int, range: int) -> Histogram:
        """
        Returns the histogram from one of the HSV channels.
        """
        histogram = cv2.calcHist(images=[self._image], channels=[channel], mask=None, histSize=[range], ranges=[0, range])
        histogram2 = reshape(histogram, (histogram.size))
        return histogram2

    def hue(self) -> Histogram:
        """
        Returns the histogram from the hue channel.
        """
        return self._histogram(0, 180)

    def saturation(self) -> Histogram:
        """
        Returns the histogram from the saturation channel.
        """
        return self._histogram(1, 256)

    def value(self) -> Histogram:
        """
        Returns the histogram from the value channel.
        """
        return self._histogram(2, 256)

    def hsv(self) -> Histogram:
        """
        Returns the combined histogram from all HSV channels.
        """
        h1 = self.hue()
        h2 = self.saturation()
        h3 = self.value()
        h = concatenate((h1, h2, h3))
        return h

    def size(self) -> int:
        """
        Returns the size of the image in numbers of pixels.
        """
        height, width, _ = self._image.shape
        return height * width

    @staticmethod
    def scale(histogram: Histogram, pixels: int) -> Histogram:
        """
        """
        return histogram / pixels


def scaled_hsv_histogram(image: Url) -> Histogram:
    """
    Returns a scaled histogram of the HSV space of an image.
    """
    hh = HsvHistogram(image)
    return HsvHistogram.scale(hh.hsv(), hh.size())


def cluster(images: List[Url], bandwidth: float) -> List[int]:
    """
    """
    c = [scaled_hsv_histogram(i) for i in images]
    d = vstack(c)
    ms = MeanShift(bandwidth)
    ms.fit(d)
    results = ms.labels_.tolist()
    return results


def main(directory: Url) -> None:
    """
    """
    print('Reading image directory....')
    images = ImageDirectory(directory).jpeg()
    print('Clustering....')
    c = cluster(images, .09)
    print('Saving....')
    ListFile(TEXT_CLUSTER_HISTOGRAM).write(c)
    return


# main()
