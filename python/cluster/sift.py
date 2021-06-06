from abc import ABC, abstractmethod
from enum import Enum
from json import dump
from typing import Any, Dict, List, Union
import itertools
import cv2
from core.cluster import ClusterRegistry, ClusterResults, ClusterStrategy
from core.jl import npsave, read_image
from core.typing2 import Url, number
from numpy import amax, apply_along_axis, ndarray, set_printoptions, zeros
from sklearn.cluster import AffinityPropagation
from sklearn.preprocessing import normalize

set_printoptions(threshold=10000000000)
Descriptors = ndarray
Matrix = ndarray


class Similarity(ABC):
    """
    Abstract class for computing similarity between images.
    """

    @abstractmethod
    def compute(self, a: Descriptors, b: Descriptors) -> number:
        """
        Returns a measure of how similar two images (sets of descriptors) are.
        To be implemented by subclasses.
        """
        pass


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

    def compute(self, a: Descriptors, b: Descriptors) -> number:
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

    def compute(self, a: Descriptors, b: Descriptors) -> number:
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

    def compute(self, a: Descriptors, b: Descriptors) -> number:
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
        for x, d1 in enumerate(descriptors):
            for y, d2 in enumerate(descriptors):
                matrix[x, y] = algorithm.compute(d1, d2)
        self.matrix = matrix
        return

    @staticmethod
    def empty_matrix(size: int) -> Matrix:
        """
        Returns a square matrix filled with zeros.
        """
        dim = (size, size)
        return zeros(dim)

    def save_as_json(self, url: Url) -> None:
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

    def __init__(self, images: List[Url], features: int = 300):
        sift = cv2.xfeatures2d.SIFT_create(nfeatures=features)
        a = list()
        for url in images:
            image = read_image(url)
            _, descriptors = sift.detectAndCompute(image=image, mask=None)
            a.append(descriptors)
        self.descriptors = a

    def unit_normalize(self) -> None:
        """
        Scales input vectors individually to unit norm (vector length).
        """
        self.descriptors = list(map(normalize, self.descriptors))

    def save(self, url: Url) -> None:
        """
        Saves descriptors to a NumPy file.
        """
        npsave(url, self.descriptors)


class SiftCluster(ClusterStrategy):
    """
    Clusters images from SIFT descriptors.
    """

    def __init__(self, similarity: Similarity):
        self._similarity: Similarity = similarity

    def run(self, images: List[Url]) -> ClusterResults:
        """
        Creates descriptors of images.
        Groups images together by how similar their descriptors are.
        Returns a cluster ID for each set of descriptors.
        """
        print("Creating descriptors from images....")
        sds = SiftDescriptorSet(images)
        print('Normalizing descriptors to unit vectors....')
        sds.unit_normalize()
        print('Similarity matrix....')
        sm = SimilarityMatrix(sds.descriptors, self._similarity)
        print('Scaling each row of the similarity matrix....')
        sm.scale()
        print('Clustering by affinity propagation....')
        cluster = AffinityPropagation(random_state=0).fit_predict(sm.matrix).tolist()
        return ClusterResults(images, cluster)


class SimilarityMetric(Enum):
    INVERSE_DISTANCE = 'inverse_distance'
    COUNT = 'count'


class AffinityPropagationAffinity(Enum):
    EUCLIDEAN = 'euclidean'
    PRECOMPUTED = 'precomputed'


class DescriptorMatcher(Enum):
    FLANNBASED = 'flann_based'
    BRUTEFORCE = 'brute_force'


class SiftCluster2(ClusterStrategy):
    def run(
        self,
        images: List[Url],
        nfeatures: int = 0,
        nOctaveLayers: int = 3,
        contrastThreshold: float = 0.04,
        edgeThreshold: float = 10,
        sigma: float = 1.6,
        ratio: float = 0.8,
        similarity_metric: SimilarityMetric = SimilarityMetric.INVERSE_DISTANCE,
        damping: float = 0.5,
        max_iter: int = 200,
        convergence_iter: int = 15,
        affinity: AffinityPropagationAffinity = AffinityPropagationAffinity.EUCLIDEAN,
        descriptor_matcher: DescriptorMatcher = DescriptorMatcher.FLANNBASED,
    ) -> ClusterResults:
        if not isinstance(similarity_metric, SimilarityMetric):
            similarity_metric = SimilarityMetric(similarity_metric)
        if not isinstance(affinity, AffinityPropagationAffinity):
            affinity = AffinityPropagationAffinity(affinity)
        if not isinstance(descriptor_matcher, DescriptorMatcher):
            descriptor_matcher = DescriptorMatcher(descriptor_matcher)
        list_of_images = list()
        matrix = SimilarityMatrix.empty_matrix(len(images))
        for url in images:
            print("SIFT DESCRIPTORS: %s" % url)
            keypoint, descriptors = cv2.xfeatures2d.SIFT_create(
                nfeatures,
                nOctaveLayers,
                contrastThreshold,
                edgeThreshold,
                sigma,
            ).detectAndCompute(image=read_image(url), mask=None)
            list_of_images.append(descriptors)
        combo = list(itertools.combinations_with_replacement(range(len(list_of_images)), 2))
        if descriptor_matcher == DescriptorMatcher.FLANNBASED:
            matcher = cv2.FlannBasedMatcher_create()
        else:
            matcher = cv2.BFMatcher_create()
        for idx, (i, j) in enumerate(combo):
            print("SIFT SIMILARITY: ( %i / %i ) ( %i / %i )" % (i, j, idx, len(combo)))
            if i != j:
                matches = matcher.knnMatch(queryDescriptors=list_of_images[i], trainDescriptors=list_of_images[j], k=2)
                good = []
                for m, n in matches:
                    if m.distance < ratio * n.distance:
                        good.append(m)
                if similarity_metric == SimilarityMetric.INVERSE_DISTANCE:
                    inverse_distance = 0
                    for k in good:
                        inverse_distance += 1 - k.distance
                    if len(good) > 0:
                        matrix[i][j] = inverse_distance / len(good)
                        matrix[j][i] = inverse_distance / len(good)
                elif similarity_metric == SimilarityMetric.COUNT:
                    matrix[i][j] = len(good)
                    matrix[j][i] = len(good)
            else:
                if similarity_metric == SimilarityMetric.INVERSE_DISTANCE:
                    matrix[i][i] = 1
                elif similarity_metric == SimilarityMetric.COUNT:
                    matrix[i][i] = nfeatures
        print('CLUSTER: AffinityPropagation')
        cluster = AffinityPropagation(
            damping=damping,
            max_iter=max_iter,
            convergence_iter=convergence_iter,
            affinity=affinity.value,
            random_state=0,
        ).fit_predict(matrix).tolist()
        return ClusterResults(images, cluster)


ClusterRegistry.add('sift', SiftCluster(Similarity1()))
ClusterRegistry.add('sift2', SiftCluster(Similarity2()))
ClusterRegistry.add('sift3', SiftCluster(Similarity3()))
ClusterRegistry.add('sift4', SiftCluster2())
