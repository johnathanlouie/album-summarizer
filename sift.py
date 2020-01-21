from json import dump

from numpy import (amax, apply_along_axis, histogram, nan, set_printoptions,
                   zeros)
from sklearn.cluster import AffinityPropagation
from sklearn.preprocessing import normalize

import cv2 as cv
from jl import (JSON_SIMILARITYMATRIX, NPY_DESC, TEXT_CLUSTER_COMBINED2,
                TEXT_CLUSTER_HISTOGRAM, TEXT_CLUSTER_SIFT, TEXT_URL_ALBUM,
                ListFile, intize, npload, npsave, readimg2)


set_printoptions(threshold=nan)


def match(a, b):
    matcher = cv.BFMatcher_create()
    matches = matcher.knnMatch(a, b, 2)
    return matches


def match2(a, b):
    matcher = cv.BFMatcher_create()
    matches = matcher.match(a, b)
    return matches


def ratioTest(matches):
    good = []
    for m, n in matches:
        if m.distance < .75 * n.distance:
            good.append(m)
    return good


def ratioTest2(matches):
    good = []
    for m in matches:
        if m.distance <= .6:
            good.append(m)
    return good


def ratioTest3(matches):
    sim = 0
    for m in matches:
        if m.distance <= .75:
            sim = sim + 1 - m.distance
    return sim


def getdescriptors(imgs):
    sift = cv.xfeatures2d.SIFT_create(300)
    a = list()
    for i, v in enumerate(imgs):
        p = 'desc %d of %d' % (i+1, len(imgs))
        print(p)
        _, des = sift.detectAndCompute(v, None)
        a.append(des)
    return a


def norm(descs):
    return list(map(normalize, descs))


def histogram2(labels):
    num = amax(labels) + 1
    hist, _ = histogram(labels, num)
    return hist


def predict(model, descs):
    a = list()
    for i, v in enumerate(descs):
        p = 'pred %d of %d' % (i + 1, len(descs))
        print(p)
        b = model.predict(v)
        c = histogram2(b)
        a.append(c)
    return a


def similarity(a, b):
    # x = ratioTest(match(a, b))
    x2 = ratioTest2(match2(a, b))
    # x2 = ratioTest3(match2(a, b))
    return len(x2)
    # return x2


def simmatrix(listofdesc):
    a = zeros((len(listofdesc), len(listofdesc)))
    for i, x in enumerate(listofdesc):
        for j, y in enumerate(listofdesc):
            sim = similarity(x, y)
            a[i, j] = sim
    return a


def normalizerow(row):
    # row2 = np.square(row)
    maxi = amax(row)
    # sec = np.partition(row, -2)[-2]
    # if sec <= 120:
    # row = row / sec * 300
    # row[row >= 300] = 0
    # asd = row / maxi
    # print(asd)
    # return row / sec
    # return np.sqrt(row)
    return row / maxi


def invertlabels(labels):
    l = list()
    num = max(labels) + 1
    for _ in range(num):
        l.append(list())
    for i, v in enumerate(labels):
        l[v].append(i)
    return l


def cluster(desc):
    d = norm(desc)
    e = simmatrix(d)
    q = apply_along_axis(normalizerow, 1, e)
    f = AffinityPropagation().fit(q)
    return f.labels_


def createdescfile():
    a = ListFile(TEXT_URL_ALBUM).read()
    b = readimg2(a)
    c = getdescriptors(b)
    npsave(NPY_DESC, c)
    return


def savesimmat():
    desc = npload(NPY_DESC)
    d = norm(desc)
    e = simmatrix(d)
    with open(JSON_SIMILARITYMATRIX, 'w') as file1:
        dump(e.tolist(), file1)
    return


def main2():
    # urls = jl.readtxt('url3.txt')
    # images = jl.readimg2(urls)
    # descs = getdescriptors(images)
    descs = npload(NPY_DESC)
    labels = ListFile(TEXT_CLUSTER_HISTOGRAM).read_as_int()
    invertedlabels = invertlabels(labels)
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


def main():
    # a = jl.readtxt('url3.txt')
    # b = jl.readimg2(a)
    # c = getdescriptors(b)
    c = npload(NPY_DESC)
    f = cluster(c)
    ListFile(TEXT_CLUSTER_SIFT).write(f)
    return


# createdescfile()
# main()
# main2()
# savesimmat()

# url = 'C:\\Users\\Johnathan Louie\\Downloads\\summarizer\\calvin\\Calvin Lee-[01_15] Guilin pt1_files\\1979657_10204632820873838_1998872105038206053_n.jpg'
# url2 = 'C:\\Users\\Johnathan Louie\\Downloads\\summarizer\\calvin\\Calvin Lee-[01_15] Guilin pt1_files\\10494820_10204632795473203_4096435618123510312_n.jpg'
