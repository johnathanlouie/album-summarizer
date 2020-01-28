from typing import List

from numpy import amax, histogram

from cluster import ImageCluster
from histogram import HistogramCluster
from jl import (NPY_DESC, TEXT_CLUSTER_COMBINED, TEXT_CLUSTER_COMBINED2,
                TEXT_CLUSTER_HISTOGRAM, TEXT_CLUSTER_SIFT, ListFile, Url,
                npload)
from sift import SiftCluster


class HybridCluster(ImageCluster):
    """
    """

    def run(self, directory: Url) -> List[int]:
        """
        """
        sift = SiftCluster().run(directory)
        histogram = HistogramCluster().run(directory)
        radix = max(sift) + 1
        return [self.combine(s, h, radix) for s, h in zip(sift, histogram)]

    @staticmethod
    def combine(big, lil, radix):
        return big * radix + lil


def histogram2(labels):
    """
    """
    num = amax(labels) + 1
    hist, _ = histogram(labels, num)
    return hist


def predict(model, descs):
    """
    """
    a = list()
    for i, v in enumerate(descs):
        p = 'pred %d of %d' % (i + 1, len(descs))
        print(p)
        b = model.predict(v)
        c = histogram2(b)
        a.append(c)
    return a


def invert_labels(labels):
    """
    """
    l = list()
    num = max(labels) + 1
    for _ in range(num):
        l.append(list())
    for i, v in enumerate(labels):
        l[v].append(i)
    return l


def main2() -> None:
    """
    """
    descs = npload(NPY_DESC)
    labels = ListFile(TEXT_CLUSTER_HISTOGRAM).read_as_int()
    invertedlabels = invert_labels(labels)
    lastid = 0
    newcluster = [-1] * len(labels)
    for indices in invertedlabels:
        subdescs = [descs[i] for i in indices]
        sublabels = cluster(subdescs)
        lastid = amax(sublabels) + 100 + lastid
        sublabels = sublabels + lastid
        for x, y in zip(indices, sublabels):
            newcluster[x] = y
    ListFile(TEXT_CLUSTER_COMBINED2).write(newcluster)
    return
