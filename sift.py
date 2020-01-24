from json import dump
from typing import List

from numpy import (amax, apply_along_axis, asarray, histogram, ndarray,
                   set_printoptions, zeros)
from sklearn.cluster import AffinityPropagation
from sklearn.preprocessing import normalize

import cv2
from jl import (JSON_SIMILARITYMATRIX, NPY_DESC, TEXT_CLUSTER_COMBINED2,
                TEXT_CLUSTER_HISTOGRAM, TEXT_CLUSTER_SIFT, Image,
                ImageDirectory, ListFile, Number, Url, npload, npsave,
                readimg2)


set_printoptions(threshold=10000000000)
Descriptors = ndarray
Matrix = ndarray


def match(a: Descriptors, b: Descriptors) -> List[List[cv2.DMatch]]:
    """
    For each descriptor in the first set, this matcher finds the closest descriptor in the second set by trying each one.
    Finds the k best matches for each descriptor from a query set.
    """
    matcher = cv2.BFMatcher_create()
    matches = matcher.knnMatch(queryDescriptors=a, trainDescriptors=b, k=2)
    return matches


def match2(a: Descriptors, b: Descriptors) -> List[cv2.DMatch]:
    """
    For each descriptor in the first set, this matcher finds the closest descriptor in the second set by trying each one.
    Finds the best match for each descriptor from a query set.
    """
    matcher = cv2.BFMatcher_create()
    matches = matcher.match(queryDescriptors=a, trainDescriptors=b)
    return matches


def ratio_test(matches: List[List[cv2.DMatch]]) -> List[cv2.DMatch]:
    """
    Filters out false matches by David Lowe's ratio test.
    """
    good = []
    for m, n in matches:
        if m.distance < .75 * n.distance:
            good.append(m)
    return good


def ratio_test2(matches: List[cv2.DMatch]) -> List[cv2.DMatch]:
    """
    Filters out false matches by my variation of David Lowe's ratio test.
    """
    good = []
    for m in matches:
        if m.distance <= .6:
            good.append(m)
    return good


def get_descriptors(imgs: List[Image], features: int = 300) -> List[Descriptors]:
    """
    Returns SIFT descriptors from images.
    More features helps distinguishing images but adds more bad descriptors.
    """
    sift = cv2.xfeatures2d.SIFT_create(nfeatures=features)
    a = list()
    for i, img in enumerate(imgs):
        p = 'Descriptors %3d / %3d' % (i + 1, len(imgs))
        print(p)
        _, descriptors = sift.detectAndCompute(image=img, mask=None)
        a.append(descriptors)
    a2 = asarray(a)
    return a2


def norm(descriptors: List[Descriptors]) -> List[Descriptors]:
    """
    Scales input vectors individually to unit norm (vector length).
    """
    return list(map(normalize, descriptors))


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


def similarity(a: Descriptors, b: Descriptors) -> Number:
    """
    Returns a measure of how similar two images (sets of descriptors) are.
    Uses K nearest neighbor to match key points between images.
    Filters out false matches by Lowe's ratio test.
    The number of true matches are returned.
    """
    m = match(a, b)
    x = ratio_test(m)
    return len(x)


def similarity2(a: Descriptors, b: Descriptors) -> Number:
    """
    Returns a measure of how similar two images (sets of descriptors) are.
    Uses brute force matching to match key points between images.
    Filters out false matches by a ratio test.
    The number of true matches are returned.
    """
    m = match2(a, b)
    x = ratio_test2(m)
    return len(x)


def similarity3(a: Descriptors, b: Descriptors) -> Number:
    """
    Returns a measure of how similar two images (sets of descriptors) are.
    Uses brute force matching to match key points between images.
    Returns the sum of the closeness between true matches.
    """
    matches = match2(a, b)
    sim = 0
    for m in matches:
        if m.distance <= .75:
            closeness = 1 - m.distance
            sim = sim + closeness
    return sim


def empty_matrix(size: int) -> Matrix:
    """
    Returns a square matrix filled with zeros.
    """
    dim = (size, size)
    return zeros(dim)


def sim_matrix(descriptors: List[Descriptors]) -> Matrix:
    """
    Prepares a similarity matrix.
    Each XY entry is a numerical value of how similar X is to Y.
    """
    matrix = empty_matrix(len(descriptors))
    for x, d1 in enumerate(descriptors):
        for y, d2 in enumerate(descriptors):
            matrix[x, y] = similarity2(d1, d2)
    return matrix


def scale_row(row: ndarray) -> ndarray:
    """
    Scales a 1D array between 0 and 1.
    """
    max_ = amax(row)
    row2 = row / max_
    return row2


def normalize_row(row: ndarray) -> ndarray:
    """
    Old version of scale_row.
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


def cluster(descriptors: List[Descriptors]) -> List[int]:
    """
    Groups images together by how similar their descriptors are.
    Returns a cluster ID for each set of descriptors.
    """
    print('Normalizing descriptors to unit vectors....')
    d = norm(descriptors)
    print('Similarity matrix....')
    sm = sim_matrix(d)
    print('Scaling each row of the similarity matrix....')
    sm2 = apply_along_axis(scale_row, 1, sm)
    print('Clustering by affinity propagation....')
    ap = AffinityPropagation().fit(sm2)
    return ap.labels_.tolist()


def create_descriptors(directory: Url) -> None:
    """
    Creates and saves the descriptors of an array of images.
    """
    image_urls = ImageDirectory(directory).jpeg()
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
