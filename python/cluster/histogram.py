from typing import Dict, List

import cv2
from core.cluster import ClusterRegistry, ClusterResults, ClusterStrategy
from core.jl import hsv, read_image
from core.typing2 import Url
from numpy import concatenate, ndarray, reshape, vstack
from sklearn.cluster import MeanShift


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
        histogram = cv2.calcHist(
            images=[self._image],
            channels=[channel],
            mask=None,
            histSize=[range],
            ranges=[0, range],
        )
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


class HistogramCluster(ClusterStrategy):
    """
    """

    def run(self, images: List[Url]) -> ClusterResults:
        """
        Clusters images.
        """
        print('Reading image directory....')
        cluster = self.cluster(images)
        return ClusterResults(images, cluster)

    @staticmethod
    def cluster(images: List[Url], bandwidth: float = .09) -> List[int]:
        """
        """
        c = list()
        print('Creating histograms....')
        for i in images:
            hh = HsvHistogram(i)
            histogram = HsvHistogram.scale(hh.hsv(), hh.size())
            c.append(histogram)
        d = vstack(c)
        print('Clustering by mean shift....')
        results = MeanShift(bandwidth=bandwidth).fit_predict(d).tolist()
        return results


ClusterRegistry.add('histogram', HistogramCluster())
