from jl import (TEXT_CLUSTER_COMBINED, TEXT_CLUSTER_HISTOGRAM,
                TEXT_CLUSTER_SIFT, ListFile)


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
