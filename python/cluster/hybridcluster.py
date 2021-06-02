from typing import Dict, List

from rasek.cluster import ClusterRegistry, ClusterResults, ClusterStrategy
from rasek.typing2 import Url

from cluster.histogram import HistogramCluster
from cluster.sift import (SiftCluster, SiftCluster2, Similarity, Similarity1, Similarity2,
                          Similarity3)


class HybridCluster(ClusterStrategy):
    """
    """

    def __init__(self, similarity: Similarity):
        self._sift = SiftCluster(similarity)
        self._hist = HistogramCluster()

    def run(self, images: List[Url]) -> ClusterResults:
        """
        Clusters images.
        """
        results1 = self._sift.run(images)
        results2 = self._hist.run(images)
        labels1 = results1.labels()
        labels2 = results2.labels()
        k1 = results1.k()
        cluster = [self.combine(c1, c2, k1)
                   for c1, c2 in zip(labels1, labels2)]
        self.remove_empty_clusters(cluster)
        return ClusterResults(images, cluster)

    @staticmethod
    def combine(label1: int, label2: int, k1: int) -> int:
        """
        Returns a new cluster label by combining two cluster labels.
        """
        return label1 * k1 + label2

    @staticmethod
    def _next_lowest(min_: int, clusters: List[int]) -> int:
        """
        Returns the lowest integer from the list of integers no lower than the given minimum.
        Returns none if there is no integer greater or equal to the minimum.
        """
        lowest = None
        for i in clusters:
            if lowest == None:
                if min_ <= i:
                    lowest = i
            elif min_ <= i <= lowest:
                lowest = i
        return lowest

    @staticmethod
    def _replace_all(l: List[int], old: int, new: int) -> None:
        """
        """
        for i, e in enumerate(l):
            if e == old:
                l[i] = new
        return

    def remove_empty_clusters(self, clusters: List[int]) -> None:
        """
        """
        k = max(clusters) + 1
        for i in range(k):
            j = self._next_lowest(i, clusters)
            if j == None:
                return
            elif i < j:
                self._replace_all(clusters, j, i)
        return


class HybridCluster2(HybridCluster):
    """
    """

    def run(self, images: List[Url]) -> ClusterResults:
        """
        Clusters images.
        """
        results1 = self._hist.run(images)
        cluster = [-1] * len(images)
        for label1, urls1 in enumerate(results1.urls()):
            results2 = self._sift.run(urls1)
            for label2, urls2 in enumerate(results2.urls()):
                label3 = self.combine(label1, label2, results1.k())
                for url2 in urls2:
                    i = images.index(url2)
                    cluster[i] = label3
        self.remove_empty_clusters(cluster)
        return ClusterResults(images, cluster)


class HybridCluster3(HybridCluster):
    def __init__(self):
        pass

    def run(self, images: List[Url]) -> ClusterResults:
        results1 = SiftCluster2().run(images)
        results2 = HistogramCluster().run(images)
        labels1 = results1.labels()
        labels2 = results2.labels()
        k1 = results1.k()
        cluster = [self.combine(c1, c2, k1)
                   for c1, c2 in zip(labels1, labels2)]
        self.remove_empty_clusters(cluster)
        return ClusterResults(images, cluster)


ClusterRegistry.add('hybrid1a', HybridCluster(Similarity1()))
ClusterRegistry.add('hybrid1b', HybridCluster(Similarity2()))
ClusterRegistry.add('hybrid1c', HybridCluster(Similarity3()))
ClusterRegistry.add('hybrid2a', HybridCluster2(Similarity1()))
ClusterRegistry.add('hybrid2b', HybridCluster2(Similarity2()))
ClusterRegistry.add('hybrid2c', HybridCluster2(Similarity3()))
ClusterRegistry.add('hybrid3', HybridCluster3())
