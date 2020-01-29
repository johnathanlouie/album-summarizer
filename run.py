from argparse import ArgumentParser, Namespace
from typing import List

import aaa
import cv2
from deeplearning import DeepLearningFactory
from jl import ImageDirectory, ListFile, ProgressBar, Url, copy_file
from sift import SiftCluster


def proc_args() -> Namespace:
    """
    Parses program arguments.
    """
    parser = ArgumentParser(description='A program that chooses the most representative photos from a photo album.')
    parser.add_argument('directory', help='')
    args = parser.parse_args()
    return args


def cluster_number(a: List[int]) -> int:
    """
    Returns the number of clusters in the clusters text file.
    """
    return max(a) + 1


class ImageRating(object):
    """
    Struct for holding the URL and rating of an image.
    Used by the ClusterRank class.
    """

    def __init__(self, image: Url = '', rating: int = -1) -> None:
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


class ClusterRank(object):
    """
    A ranking system that picks the best out of each cluster.
    """

    def __init__(self, clusters: List[int], rates: List[float], images: List[Url]) -> None:
        self._best = [ImageRating() for _ in range(cluster_number(clusters))]
        for c, r, i in zip(clusters, rates, images):
            self._best[c].update_if_better(i, r)
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


def main():
    args = proc_args()
    url = args.directory
    clusters = SiftCluster().run2(url).labels()
    s = DeepLearningFactory.create_split('smi1', 'ccrc', 0, 14, 0, 0)
    s.predict2(url)
    print('Loading rates....')
    prediction_file = s.name().predictions()
    rates = ListFile(prediction_file).read_as_floats()
    print('Loading images....')
    images = ImageDirectory(url).jpeg()
    print('Ranking results....')
    cr = ClusterRank(clusters, rates, images)
    print('Making summarized album at out/summarized....')
    cr.copy_images()
    return


main()
