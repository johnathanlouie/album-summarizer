from json import dump
from typing import List

from numpy import (amax, apply_along_axis, asarray, histogram, ndarray,
                   set_printoptions, zeros)
from sklearn.cluster import AffinityPropagation
from sklearn.preprocessing import normalize

import cv2 as cv
from jl import (JSON_SIMILARITYMATRIX, NPY_DESC, TEXT_CLUSTER_COMBINED2,
                TEXT_CLUSTER_HISTOGRAM, TEXT_CLUSTER_SIFT, Image,
                ImageDirectory, ListFile, Url, intize, npload, npsave,
                readimg2)


set_printoptions(threshold=10000000000)


def match(a, b):
    """
    """
    matcher = cv.BFMatcher_create()
    matches = matcher.knnMatch(a, b, 2)
    return matches


def match2(a, b):
    """
    """
    matcher = cv.BFMatcher_create()
    matches = matcher.match(a, b)
    return matches


def ratio_test(matches):
    """
    """
    good = []
    for m, n in matches:
        if m.distance < .75 * n.distance:
            good.append(m)
    return good


def ratio_test2(matches):
    """
    """
    good = []
    for m in matches:
        if m.distance <= .6:
            good.append(m)
    return good


def ratio_test3(matches):
    """
    """
    sim = 0
    for m in matches:
        if m.distance <= .75:
            sim = sim + 1 - m.distance
    return sim


def get_descriptors(imgs: List[Image], features: int = 300) -> List[ndarray]:
    """
    Returns SIFT descriptors from images.
    More features helps distinguishing images but adds more bad descriptors.
    """
    sift = cv.xfeatures2d.SIFT_create(nfeatures=features)
    a = list()
    for i, img in enumerate(imgs):
        p = 'Descriptors %3d / %3d' % (i + 1, len(imgs))
        print(p)
        _, descriptors = sift.detectAndCompute(image=img, mask=None)
        a.append(descriptors)
    a2 = asarray(a)
    return a2


def norm(descs):
    """
    """
    return list(map(normalize, descs))


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


def similarity(a, b):
    """
    """
    # x = ratio_test(match(a, b))
    x2 = ratio_test2(match2(a, b))
    # x2 = ratio_test3(match2(a, b))
    return len(x2)
    # return x2


def empty_matrix(size: int) -> ndarray:
    """
    Returns a square matrix filled with zeros.
    """
    return zeros((size, size))


def sim_matrix(listofdesc):
    """
    """
    a = empty_matrix(len(listofdesc))
    for i, x in enumerate(listofdesc):
        for j, y in enumerate(listofdesc):
            sim = similarity(x, y)
            a[i, j] = sim
    return a


def normalize_row(row):
    """
    """
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


def cluster(desc):
    """
    """
    d = norm(desc)
    e = sim_matrix(d)
    q = apply_along_axis(normalize_row, 1, e)
    f = AffinityPropagation().fit(q)
    return f.labels_


def create_desc_file(url: Url) -> None:
    """
    Creates and saves the descriptors of an array of images.
    """
    image_urls = ImageDirectory(url).jpeg()
    images = readimg2(image_urls)
    descriptors = get_descriptors(images)
    npsave(NPY_DESC, descriptors)
    print("Saved descriptors.")
    return


def save_sim_mat() -> None:
    """
    """
    desc = npload(NPY_DESC)
    d = norm(desc)
    e = sim_matrix(d)
    with open(JSON_SIMILARITYMATRIX, 'w') as file1:
        dump(e.tolist(), file1)
    return


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


def create_cluster() -> None:
    """
    Clusters images from SIFT descriptors.
    Saves them in a list file.
    """
    print('Loading descriptors....')
    descriptors = npload(NPY_DESC)
    print('Loaded descriptors.')
    clusters = cluster(descriptors)
    ListFile(TEXT_CLUSTER_SIFT).write(clusters)
    print('Saved clusters.')
    return


url = 'data/cc/calvin/Calvin Lee-[01_15] Guilin pt1_files'
create_desc_file(url)
create_cluster()
# main2()
# save_sim_mat()
