import cv2 as cv
import numpy as np
from sklearn.cluster import AffinityPropagation
from sklearn.preprocessing import normalize
import jl
import time
import json


np.set_printoptions(threshold=np.nan)


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


def histogram(labels):
    num = np.amax(labels) + 1
    hist, _ = np.histogram(labels, num)
    return hist


def predict(model, descs):
    a = list()
    for i, v in enumerate(descs):
        p = 'pred %d of %d' % (i + 1, len(descs))
        print(p)
        b = model.predict(v)
        c = histogram(b)
        a.append(c)
    return a


def similarity(a, b):
    # x = ratioTest(match(a, b))
    x2 = ratioTest2(match2(a, b))
    # x2 = ratioTest3(match2(a, b))
    return len(x2)
    # return x2


def simmatrix(listofdesc):
    a = np.zeros((len(listofdesc), len(listofdesc)))
    for i, x in enumerate(listofdesc):
        for j, y in enumerate(listofdesc):
            sim = similarity(x, y)
            a[i, j] = sim
    return a


def normalizerow(row):
    # row2 = np.square(row)
    maxi = np.amax(row)
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
    start_time = time.time()
    d = norm(desc)
    e = simmatrix(d)
    q = np.apply_along_axis(normalizerow, 1, e)
    f = AffinityPropagation().fit(q)
    elapsed_time = time.time() - start_time
    minutes, sec = divmod(elapsed_time, 60)
    print('time: %d:%02d' % (minutes, sec))
    return f.labels_


def createdescfile():
    a = jl.readtxt(jl.TEXT_URL_ALBUM)
    b = jl.readimg2(a)
    c = getdescriptors(b)
    jl.npsave(jl.NPY_DESC, c)
    return


def savesimmat():
    desc = jl.npload(jl.NPY_DESC)
    d = norm(desc)
    e = simmatrix(d)
    with open(jl.JSON_SIMILARITYMATRIX, 'w') as file1:
        json.dump(e.tolist(), file1)
    return


def main2():
    # urls = jl.readtxt('url3.txt')
    # images = jl.readimg2(urls)
    # descs = getdescriptors(images)
    descs = jl.npload(jl.NPY_DESC)
    labels = jl.readtxt(jl.TEXT_CLUSTER_HISTOGRAM)
    labels = jl.intize(labels)
    invertedlabels = invertlabels(labels)
    lastid = 0
    newcluster = [-1] * len(labels)
    for indices in invertedlabels:
        subdescs = [descs[i] for i in indices]
        sublabels = cluster(subdescs)
        lastid = np.amax(sublabels) + 100 + lastid
        sublabels = sublabels + lastid
        for x, y in zip(indices, sublabels):
            newcluster[x] = y
    jl.writetxt(jl.TEXT_CLUSTER_COMBINED2, newcluster)
    return


def main():
    # a = jl.readtxt('url3.txt')
    # b = jl.readimg2(a)
    # c = getdescriptors(b)
    c = jl.npload(jl.NPY_DESC)
    f = cluster(c)
    jl.writetxt(jl.TEXT_CLUSTER_SIFT, f)
    return


# createdescfile()
# main()
# main2()
# savesimmat()

# url = 'C:\\Users\\Johnathan Louie\\Downloads\\summarizer\\calvin\\Calvin Lee-[01_15] Guilin pt1_files\\1979657_10204632820873838_1998872105038206053_n.jpg'
# url2 = 'C:\\Users\\Johnathan Louie\\Downloads\\summarizer\\calvin\\Calvin Lee-[01_15] Guilin pt1_files\\10494820_10204632795473203_4096435618123510312_n.jpg'
