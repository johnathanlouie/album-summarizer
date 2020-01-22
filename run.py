from sift import create_desc_file, create_cluster
from argparse import ArgumentParser, Namespace
from main import create_split
from jl import Url, mkdirs, ImageDirectory, ListFile, TEXT_CLUSTER_SIFT
import cv2
from rater import Smi13_1
from cc import CcrCategorical
from typing import List


def copy_img(image: Url, destination: Url) -> None:
    """
    Makes a copy of an image to another location.
    """
    x = cv2.imread(image, cv2.IMREAD_COLOR)
    new_url = "out/summarized/%s.jpg" % destination
    mkdirs(new_url)
    cv2.imwrite(new_url, x)
    return


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
    """
    max_ = -1
    for i in a:
        if i > max_:
            max_ = i
    return max_ + 1


class ImageRating(object):
    """
    """

    def __init__(self, image: Url = '', rating: int = -1) -> None:
        self.image = image
        self.rating = rating
        return


def main():
    args = proc_args()
    url = args.directory
    create_desc_file(url)
    create_cluster()
    clusters = ListFile(TEXT_CLUSTER_SIFT).read_as_int()
    best = [ImageRating()] * cluster_number(clusters)
    s = create_split(Smi13_1(), CcrCategorical(), 0, 14, 0, 0)
    s.predict2(url)
    print('Loading rates....')
    rates = ListFile(s.name().predictions()).read_as_floats()
    images = ImageDirectory(url).jpeg()
    print('Ranking results....')
    for c, r, i in zip(clusters, rates, images):
        if r > best[c].rating:
            best[c].image = i
            best[c].rating = r
    print('Making summarized album at out/summarized....')
    for cluster, image_rating in enumerate(best):
        print("Image %2d / %d" % (cluster + 1, len(best)))
        copy_img(image_rating.image, cluster)
    return


main()
