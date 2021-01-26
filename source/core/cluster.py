from typing import Dict, List, Union

from jl import ImageDirectory, Url


class ClusterResult(object):
    """
    A data object that is used by ClusterResults.
    """

    def __init__(self, image: Url, cluster: int) -> None:
        self.url = image
        self.cluster = cluster

    def toJson(self) -> Dict[str, Union[Url, int]]:
        """
        Returns a JSON serializable dict.
        """
        return {
            'url': self.url,
            'cluster': self.cluster
        }


class ClusterResults(object):
    """
    """

    def __init__(self, images: List[Url], clusters: List[int]) -> None:
        self._images = images
        self._clusters = clusters

    def k(self) -> int:
        """
        Returns the number of clusters.
        """
        return max(self._clusters) + 1

    def get_all_urls(self) -> List[Url]:
        """
        """
        return self._images

    def labels(self) -> List[int]:
        """
        """
        return self._clusters

    def indices(self) -> List[List[int]]:
        """
        Returns a list of clusters.
        Each cluster is a list of indices.
        """
        l = [list() for _ in range(self.k())]
        for image, cluster in enumerate(self._clusters):
            l[cluster].append(image)
        return l

    def urls(self) -> List[List[Url]]:
        """
        Returns a list of clusters.
        Each cluster is a list of URLs.
        """
        return [[self._images[i] for i in cluster] for cluster in self.indices()]


class ImageCluster(object):
    """
    """

    def run(self,  images: List[Url]) -> ClusterResults:
        """
        """
        raise NotImplementedError

    def run2(self, directory: Url) -> ClusterResults:
        """
        """
        images = ImageDirectory(directory).jpeg()
        return self.run(images)
