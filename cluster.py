import jl
import numpy as np
import sift
import histogram


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
    a = jl.readtxt(jl.TEXT_CLUSTER_SIFT)
    b = jl.readtxt(jl.TEXT_CLUSTER_HISTOGRAM)
    a = jl.intize(a)
    b = jl.intize(b)
    c = combine(a, b)
    jl.writetxt(jl.TEXT_CLUSTER_COMBINED, c)
    return


# sift.createdescfile()
# sift.main()
# histogram.main()
# main()
