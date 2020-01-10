from os import getcwd
from os.path import join, normpath
from typing import List, Optional, Union

from numpy import asarray, ndarray

from dataset import DataSet
from jl import Csv, Url


class CcDataFile(object):
    """
    Represents the data file for the CC dataset.
    Knows the URL and internals of the data file.
    Does not know the paths of the images.
    """

    URL = 'data/cc/data.csv'

    categories = {
        'environment': 0,
        'people': 1,
        'object': 2,
        'hybrid': 3,
        'animal': 4,
        'food': 5
    }

    def __init__(self, url: Optional[Url] = None) -> None:
        if url == None:
            url = self.URL
        self._csv = Csv(url)
        return

    def _to_category_int(self, e: str) -> int:
        """
        Converts categories from string to integer representation.
        """
        return self.categories[e]

    def to_category_int(self, a: List[str]) -> List[int]:
        """
        Converts categories from string to integer representation.
        """
        return [self._to_category_int(i) for i in a]

    def _to_category_str(self, e: int) -> str:
        """
        Converts categories from integer to string representation.
        """
        for k, v in self.categories.items():
            if e == v:
                return k
        raise Exception()

    def to_category_str(self, a: List[int]) -> List[str]:
        """
        Converts categories from integer to string representation.
        """
        return [self._to_category_str(i) for i in a]

    def url(self) -> List[Url]:
        """
        Gets the urls of the input images.
        """
        return self._csv.get_col(0)

    def rating(self) -> List[int]:
        """
        Gets the user ratings of the images.
        """
        return self._csv.get_col_int(1)

    def category(self) -> List[str]:
        """
        Gets the categories of the images as strings.
        """
        return self._csv.get_col(2)

    def category_as_int(self) -> List[int]:
        """
        Gets the categories of the images as integers.
        """
        return self.to_category_int(self.category())


class Cc(DataSet):
    """
    An abstract base class for the CC dataset.
    """

    NAME = 'cc'
    SPLITS = 5

    def _relative_url(self, url: Url) -> str:
        """
        Returns the relative url of the image from the filename.
        """
        a = join(getcwd(), 'data', 'cc', url)
        return normpath(a)

    def _x(self) -> ndarray:
        """
        Returns an array of URLs to the images.
        """
        data_file = CcDataFile()
        x = data_file.url()
        x = [self._relative_url(i) for i in x]
        return asarray(x)

    def _y(self) -> ndarray:
        """
        Returns the Y. To be implemented by subclass.
        """
        raise NotImplementedError

    def prepare(self) -> None:
        """
        Reads the data file and produces some splits.
        """
        x = self._x()
        y = self._y()
        print('Generating data splits')
        for i in range(self.SPLITS):
            self.create_split(x, y, i)
        print('Prep complete')
        return


class Ccc(Cc):
    """
    The image classification subset of the CC dataset.
    """

    NAME = 'ccc'

    def _y(self) -> ndarray:
        """
        Returns the Y. To be implemented by subclass.
        """
        data_file = CcDataFile()
        y = asarray(data_file.category_as_int())
        y = self.one_hot(y, 6)
        return y


class Ccr(Cc):
    """
    The aesthetic rating subset of the CC dataset.
    """

    NAME = 'ccr'

    def _y(self) -> ndarray:
        """
        Returns the Y. To be implemented by subclass.
        """
        data_file = CcDataFile()
        y = asarray(data_file.rating())
        return y


class CcrCategorical(Cc):
    """
    The aesthetic rating subset of the CC dataset using categories instead of a number.
    """

    NAME = 'ccrc'

    def _y(self) -> ndarray:
        """
        Returns the Y. To be implemented by subclass.
        """
        data_file = CcDataFile()
        y = data_file.rating()
        y = [i - 1 for i in y]
        y = asarray(y)
        y = self.one_hot(y, 3)
        return y

    def class_names(self, results: List[int]) -> List[Union[str, int]]:
        """
        Returns correct rating.
        """
        return [i + 1 for i in results]
