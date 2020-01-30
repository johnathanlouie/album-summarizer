from argparse import ArgumentParser, Namespace
from typing import List

import aaa
import cv2
from cluster.histogram import HistogramCluster
from cluster.hybridcluster import HybridCluster, HybridCluster2
from cluster.sift import SiftCluster
from core.archidata import ArchitectureSplit
from core.cluster import ClusterResults, ImageCluster
from dlfactory import DeepLearningFactory
from jl import ImageDirectory, ListFile, ProgressBar, Url, copy_file


def proc_args() -> Namespace:
    """
    Parses program arguments.
    """
    parser = ArgumentParser(description='A program that chooses the most representative photos from a photo album.')
    parser.add_argument('directory', help='')
    args = parser.parse_args()
    return args


class ImageRating(object):
    """
    Struct for holding the URL and rating of an image.
    Used by the ClusterRank class.
    """

    def __init__(self, image: Url = None, rating: int = -1000000000000000000000000000) -> None:
        self.image = image
        self.rating = rating
        return

    def update_if_better(self, image: Url, rating: int) -> bool:
        """
        Updates the data if the new image is better.
        """
        if self.rating < rating:
            self.image = image
            self.rating = rating
            return True
        return False

    def valid(self) -> bool:
        """
        Returns true if the object has been updated at least once.
        """
        return self.image != None


class ClusterRank(object):
    """
    A ranking system that picks the best out of each cluster.
    """

    def __init__(self, clusters: ClusterResults, rates: List[float]) -> None:
        self._best = [ImageRating() for _ in range(clusters.k())]
        for c, r, i in zip(clusters.labels(), rates, clusters.get_all_urls()):
            self._best[c].update_if_better(i, r)
        for i in self._best:
            if not i.valid():
                raise Exception('Some clusters are empty.')
        return

    @staticmethod
    def copy_img(image: Url) -> None:
        """
        Makes a copy of an image to another location.
        """
        copy_file(image, 'out/summarized', 1)
        return

    def copy_images(self) -> None:
        """
        Makes a copy of each image in this summarized collection to a new location.
        """
        pb = ProgressBar(len(self._best))
        for image_rating in self._best:
            self.copy_img(image_rating.image)
            pb.update()
        return


def main2(url: Url, algorithm: ImageCluster, algorithm2: ArchitectureSplit) -> None:
    """
    Does all the work.
    """
    clusters = algorithm.run2(url)
    algorithm2.predict2(url)
    print('Loading rates....')
    prediction_file = algorithm2.name().predictions()
    rates = ListFile(prediction_file).read_as_floats()
    print('Ranking results....')
    cr = ClusterRank(clusters, rates)
    print('Making summarized album at out/summarized....')
    cr.copy_images()
    return


def main():
    """
    Command line shell interface.
    """
    args = proc_args()
    url = args.directory
    cluster = SiftCluster()
    rater = DeepLearningFactory.create_split('smi1', 'ccrc', 0, 14, 0, 0)
    main2(url, cluster, rater)
    return


main()
