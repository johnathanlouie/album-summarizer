from json import dump
from typing import List

from numpy import (amax, apply_along_axis, asarray, ndarray, set_printoptions,
                   zeros)
from sklearn.cluster import AffinityPropagation
from sklearn.preprocessing import normalize

import cv2
from jl import (JSON_SIMILARITYMATRIX, NPY_DESC, TEXT_CLUSTER_SIFT, Image,
                ImageDirectory, ListFile, Number, ProgressBar, Url, npload,
                npsave, read_image, readimg2)


set_printoptions(threshold=10000000000)
Descriptors = ndarray
Matrix = ndarray


def normalize_row(row: ndarray) -> ndarray:
    """
    Old version of SimilarityMatrix.scale_row.
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


def cluster(descriptors: List[Descriptors]) -> List[int]:
    """
    Groups images together by how similar their descriptors are.
    Returns a cluster ID for each set of descriptors.
    """
    print('Similarity matrix....')
    sm = SimilarityMatrix(descriptors, Similarity2())
    print('Scaling each row of the similarity matrix....')
    sm.scale()
    print('Clustering by affinity propagation....')
    results = AffinityPropagation().fit_predict(sm.matrix).tolist()
    return results


def create_descriptors(directory: Url) -> None:
    """
    Creates and saves the descriptors of an array of images.
    """
    images = ImageDirectory(directory).jpeg()
    print("Creating descriptors from images....")
    sds = SiftDescriptorSet(images)
    print('Normalizing descriptors to unit vectors....')
    sds.unit_normalize()
    sds.save()
    print("Saved descriptors.")
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


class Similarity(object):
    """
    Abstract class for computing similarity between images.
    """

    def compute(self, a: Descriptors, b: Descriptors) -> Number:
        """
        Returns a measure of how similar two images (sets of descriptors) are.
        To be implemented by subclasses.
        """
        raise NotImplementedError


class Similarity1(Similarity):
    """
    Uses K nearest neighbor to match key points between images.
    Filters out false matches by Lowe's ratio test.
    The number of true matches are returned.
    """

    @staticmethod
    def match(a: Descriptors, b: Descriptors) -> List[List[cv2.DMatch]]:
        """
        For each descriptor in the first set, this matcher finds the closest descriptor in the second set by trying each one.
        Finds the k best matches for each descriptor from a query set.
        """
        matcher = cv2.BFMatcher_create()
        matches = matcher.knnMatch(queryDescriptors=a, trainDescriptors=b, k=2)
        return matches

    @staticmethod
    def ratio_test(matches: List[List[cv2.DMatch]]) -> List[cv2.DMatch]:
        """
        Filters out false matches by David Lowe's ratio test.
        """
        good = []
        for m, n in matches:
            if m.distance < .75 * n.distance:
                good.append(m)
        return good

    def compute(self, a: Descriptors, b: Descriptors) -> Number:
        """
        Returns a measure of how similar two images (sets of descriptors) are.
        """
        m = self.match(a, b)
        x = self.ratio_test(m)
        return len(x)


class Similarity2(Similarity):
    """
    Uses brute force matching to match key points between images.
    Filters out false matches by a ratio test.
    The number of true matches are returned.
    """

    @staticmethod
    def match(a: Descriptors, b: Descriptors) -> List[cv2.DMatch]:
        """
        For each descriptor in the first set, this matcher finds the closest descriptor in the second set by trying each one.
        Finds the best match for each descriptor from a query set.
        """
        matcher = cv2.BFMatcher_create()
        matches = matcher.match(queryDescriptors=a, trainDescriptors=b)
        return matches

    @staticmethod
    def ratio_test(matches: List[cv2.DMatch]) -> List[cv2.DMatch]:
        """
        Filters out false matches by my variation of David Lowe's ratio test.
        """
        good = []
        for m in matches:
            if m.distance <= .6:
                good.append(m)
        return good

    def compute(self, a: Descriptors, b: Descriptors) -> Number:
        """
        Returns a measure of how similar two images (sets of descriptors) are.
        """
        m = self.match(a, b)
        x = self.ratio_test(m)
        return len(x)


class Similarity3(Similarity2):
    """
    Uses brute force matching to match key points between images.
    Returns the sum of the closeness between true matches.
    """

    def compute(self, a: Descriptors, b: Descriptors) -> Number:
        """
        Returns a measure of how similar two images (sets of descriptors) are.
        """
        matches = self.match(a, b)
        sim = 0
        for m in matches:
            if m.distance <= .75:
                closeness = 1 - m.distance
                sim = sim + closeness
        return sim


class SimilarityMatrix(object):
    """
    A square array.
    Each XY entry is a numerical value of how similar X is to Y.
    """

    def __init__(self, descriptors: List[Descriptors], algorithm: Similarity) -> None:
        num = len(descriptors)
        matrix = self.empty_matrix(num)
        pb = ProgressBar(num * num)
        for x, d1 in enumerate(descriptors):
            for y, d2 in enumerate(descriptors):
                matrix[x, y] = algorithm.compute(d1, d2)
                pb.update()
        self.matrix = matrix
        return

    @staticmethod
    def empty_matrix(size: int) -> Matrix:
        """
        Returns a square matrix filled with zeros.
        """
        dim = (size, size)
        return zeros(dim)

    def save_as_json(self, url: Url = JSON_SIMILARITYMATRIX) -> None:
        """
        Saves the similarity matrix as a JSON file.
        """
        with open(url, 'w') as f:
            dump(self.matrix.tolist(), f)
        return

    @staticmethod
    def scale_row(row: ndarray) -> ndarray:
        """
        Scales a 1D array between 0 and 1.
        """
        max_ = amax(row)
        row2 = row / max_
        return row2

    def scale(self):
        """
        Scales the similarity matrix row by row.
        """
        self.matrix = apply_along_axis(self.scale_row, 1, self.matrix)


class SiftDescriptorSet(object):
    """
    Returns SIFT descriptors from images.
    More features helps distinguishing images but adds more bad descriptors.
    """

    def __init__(self, images: List[Url], features: int = 300) -> None:
        sift = cv2.xfeatures2d.SIFT_create(nfeatures=features)
        a = list()
        pb = ProgressBar(len(images))
        for url in images:
            image = read_image(url)
            _, descriptors = sift.detectAndCompute(image=image, mask=None)
            a.append(descriptors)
            pb.update()
        self.descriptors = a

    def unit_normalize(self) -> None:
        """
        Scales input vectors individually to unit norm (vector length).
        """
        self.descriptors = list(map(normalize, self.descriptors))
        return

    def save(self, url: Url = NPY_DESC) -> None:
        """
        Saves descriptors to a NumPy file.
        """
        npsave(url, self.descriptors)
        return
