from argparse import ArgumentParser, Namespace
from json import dump
from typing import Dict, List, Union
from urllib.parse import quote

import cv2

import aaa
from cluster.histogram import HistogramCluster
from cluster.hybridcluster import HybridCluster, HybridCluster2
from cluster.sift import SiftCluster
from core.archidata import ArchiSplitAdapter
from core.cluster import ClusterResults, ImageCluster
from dlfactory import DeepLearningFactory
from jl import ImageDirectory, ListFile, Url, copy_file


def proc_args() -> Namespace:
    """
    Parses program arguments.
    """
    parser = ArgumentParser(
        description='A program that chooses the most representative photos from a photo album.')
    parser.add_argument('directory', help='')
    args = parser.parse_args()
    return args


class ClusterRank(object):
    """
    A ranking system that picks the best out of each cluster.
    """

    def __init__(self, clusters: ClusterResults, rates: List[float]) -> None:
        self._results = [[] for _ in range(clusters.k())]
        for clusterId, rate, url in zip(clusters.labels(), rates, clusters.get_all_urls()):
            self._results[clusterId].append({
                'image': url,
                'rating': rate,
                'cluster': clusterId
            })
        for cluster in self._results:
            cluster.sort(key=lambda x: x['rating'], reverse=True)
        return

    def save_results(self, dst: Url) -> None:
        """
        Saves the results to a JSON file at 'electron/public/data/***.json'.
        """
        dst = 'electron/public/data/%s.json' % quote(dst)
        with open(dst, 'w', encoding='utf8') as f:
            dump(self._results, f, indent=4)
        return


def main2(directory: Url, algorithm: ImageCluster, algorithm2: ArchiSplitAdapter) -> None:
    """
    Does all the work.
    """
    images = ImageDirectory(directory).jpeg()
    clusters = algorithm.run(images)
    rates = algorithm2.predict(images).human_readable()
    print('Ranking results....')
    cr = ClusterRank(clusters, rates)
    print('Saving results....')
    cr.save_results(directory)
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


if __name__ == '__main__':
    main()
