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

    def __init__(self, image: Url, hue: int = 180, saturation: int = 256, value: int = 256) -> None:
        self._url = image
        self._image = hsv(read_image(image), hue, saturation, value)

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

    def hue(self, bins: int = 180) -> Histogram:
        """
        Returns the histogram from the hue channel.
        """
        return self._histogram(0, bins)

    def saturation(self, bins: int = 256) -> Histogram:
        """
        Returns the histogram from the saturation channel.
        """
        return self._histogram(1, bins)

    def value(self, bins: int = 256) -> Histogram:
        """
        Returns the histogram from the value channel.
        """
        return self._histogram(2, bins)

    def hsv(self, hue: int = 180, saturation: int = 256, value: int = 256) -> Histogram:
        """
        Returns the combined histogram from all HSV channels.
        """
        h1 = self.hue(hue)
        h2 = self.saturation(saturation)
        h3 = self.value(value)
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

    def run(
        self,
        images: List[Url],
        hue_bins: int = 180,
        saturation_bins: int = 256,
        value_bins: int = 256,
    ) -> ClusterResults:
        """
        Clusters images.
        """
        c = list()
        for i, img in enumerate(images):
            print("HISTOGRAM ( %i / %i )" % (i, len(images)))
            hh = HsvHistogram(img, hue_bins, saturation_bins, value_bins)
            histogram = HsvHistogram.scale(hh.hsv(), hh.size())
            c.append(histogram)
        d = vstack(c)
        print('CLUSTER: Mean Shift')
        cluster = MeanShift().fit_predict(d).tolist()
        return ClusterResults(images, cluster)


ClusterRegistry.add('histogram', HistogramCluster())
