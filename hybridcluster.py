from typing import List

from cluster import ClusterResults, ImageCluster
from histogram import HistogramCluster
from jl import Url
from sift import SiftCluster


class HybridCluster(ImageCluster):
    """
    """

    def run(self, images: List[Url]) -> ClusterResults:
        """
        Clusters images.
        """
        results1 = SiftCluster().run(images)
        results2 = HistogramCluster().run(images)
        labels1 = results1.labels()
        labels2 = results2.labels()
        radix = results1.k()
        cluster = [self.combine(s, h, radix) for s, h in zip(labels1, labels2)]
        return ClusterResults(images, cluster)

    @staticmethod
    def combine(label1: int, label2: int, k1: int) -> int:
        """
        Returns a new cluster label by combining two cluster labels.
        """
        return label1 * k1 + label2


class HybridCluster2(HybridCluster):
    """
    """

    def run(self, images: List[Url]) -> ClusterResults:
        """
        Clusters images.
        """
        results1 = HistogramCluster().run(images)
        cluster = [-1] * len(images)
        for label1, urls1 in enumerate(results1.urls()):
            results2 = SiftCluster().run(urls1)
            for label2, urls2 in enumerate(results2.urls()):
                label3 = self.combine(label1, label2, results1.k())
                for url2 in urls2:
                    i = images.index(url2)
                    cluster[i] = label3
        return ClusterResults(images, cluster)
