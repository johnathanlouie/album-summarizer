from numpy import amax, histogram

from jl import (NPY_DESC, TEXT_CLUSTER_COMBINED, TEXT_CLUSTER_COMBINED2,
                TEXT_CLUSTER_HISTOGRAM, TEXT_CLUSTER_SIFT, ListFile, npload)
from sift import cluster


def numberz(big, lil, radix):
    return big * radix + lil


def numberz2(a, b, c):
    return a * 1000 + b


def numberz3(a, b):
    return "%d,%d" % (a, b)


def combine(a, b):
    c = list()
    for i, j in zip(a, b):
        c.append(numberz3(i, j))
    return c


def main():
    a = ListFile(TEXT_CLUSTER_SIFT).read_as_int()
    b = ListFile(TEXT_CLUSTER_HISTOGRAM).read_as_int()
    c = combine(a, b)
    ListFile(TEXT_CLUSTER_COMBINED).write(c)
    return


# sift.createdescfile()
# sift.main()
# histogram.main()
# main()


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
