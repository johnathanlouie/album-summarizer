import jl
import os
import numpy as np
import random


def absoluteFilePaths(directory):
    a = list()
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            a.append(os.path.abspath(os.path.join(dirpath, f)))
    return a


def filter1(i):
    return i.endswith('.jpg')


def jpgonly(a):
    return list(filter(filter1, a))


def append1(src, category, num=None):
    a1 = absoluteFilePaths(src)
    a1 = jpgonly(a1)
    if num != None and num <= len(a1):
        a1 = random.sample(a1, num)
    e = len(a1)
    jl.appendtxt(jl.TEXT_URL_RAW, a1)
    with open(jl.TEXT_CLASSES, 'a') as f:
        for _ in range(e):
            print(jl.classdict[category], file=f)
    return


def main():
    # a = 'C:\\Users\\Johnathan Louie\\Downloads\\summarizer\\calvin'
    # b = 'C:\\Users\\Johnathan Louie\\Downloads\\summarizer\\clara'
    c = 'C:\\Users\\Johnathan Louie\\Downloads\\summarizer\\animals'
    e = 'C:\\Users\\Johnathan Louie\\Downloads\\summarizer\\food-101\\images'
    append1(c, 'animal')
    append1(e, 'food', 1300)
    return


# main()
