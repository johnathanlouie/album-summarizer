import hashlib
import json
import os.path
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Union

import dill

from core.jl import ImageDirectory, hash_images, mkdirname
from core.typing2 import Url


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


class ClusterStrategy(ABC):
    """
    A clustering algorithm for images.
    """

    @abstractmethod
    def run(self,  images: List[Url], **kwargs) -> ClusterResults:
        """
        Clusters a list of images.
        """
        pass

    def _cache_path(self, images: List[Url], **kwargs) -> Url:
        md5 = hashlib.md5()
        md5.update(type(self).__name__.encode())
        md5.update(json.dumps(kwargs).encode('utf-8'))
        return "cache/%s/cluster/%s.dill" % (hash_images(images), md5.hexdigest())

    def run_cached(self, images: List[Url], **kwargs) -> ClusterResults:
        filepath = self._cache_path(images, **kwargs)
        mkdirname(filepath)
        if os.path.exists(filepath):
            print('LOADING: %s' % filepath)
            with open(filepath, 'rb') as f:
                return dill.load(f)
        results = self.run(images, **kwargs)
        print('SAVING: %s' % filepath)
        with open(filepath, 'wb') as f:
            dill.dump(results, f)
        return results


class ClusterRegistryInsertionError(LookupError):
    pass


class ClusterRegistryNameError(LookupError):
    pass


class ClusterRegistry(object):
    """
    """

    _REGISTRY: Dict[str, ClusterStrategy] = dict()

    @ classmethod
    def add(cls, name: str, strategy: ClusterStrategy) -> None:
        if name in cls._REGISTRY:
            raise ClusterRegistryInsertionError(name)
        else:
            cls._REGISTRY[name] = strategy

    @ classmethod
    def get(cls, name: str) -> ClusterStrategy:
        if name not in cls._REGISTRY:
            raise ClusterRegistryNameError(name)
        return cls._REGISTRY[name]

    @ classmethod
    def keys(cls) -> List[str]:
        return list(cls._REGISTRY.keys())

    @classmethod
    def items(cls) -> List[Tuple[str, ClusterStrategy]]:
        return [i for i in cls._REGISTRY.items()]
