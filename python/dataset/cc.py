from os import getcwd
from os.path import join, normpath
from typing import Any, List, Optional, Union

from core import modelbuilder
from core.dataset import DataSet, Predictions, PredictionsFactory
from jl import Csv, Url
from numpy import asarray, ndarray


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

    def __init__(self):
        raise NotImplementedError

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
        print('Generating data splits....')
        for i in range(self.splits()):
            self.create_split(x, y, i)
        print('Prep complete')
        return

    def splits(self) -> int:
        """
        Returns the number of splits.
        """
        return 5


class CccPredictions(Predictions):
    """
    """

    def human_readable(self) -> List[Any]:
        """
        """
        return CcDataFile().to_category_str(self._y)


class CccPredictionsFactory(PredictionsFactory):
    """
    """

    def __init__(self):
        pass

    def predictions(self, x: ndarray, y: ndarray) -> Predictions:
        """
        """
        return CccPredictions(x, y)


class Ccc(Cc):
    """
    The image classification subset of the CC dataset.
    """

    NAME = 'ccc'
    OUTPUT_NUM: int = 6

    def __init__(self):
        pass

    def _y(self) -> ndarray:
        """
        Returns the Y as one hot arrays.
        """
        data_file = CcDataFile()
        y = asarray(data_file.category_as_int())
        y = self.one_hot(y, 6)
        return y

    def _predictions_factory(self) -> PredictionsFactory:
        """
        """
        return CccPredictionsFactory()


class CcrPredictions(Predictions):
    """
    """

    def human_readable(self) -> List[Any]:
        """
        """
        return self._y.flatten().tolist()


class CcrPredictionsFactory(PredictionsFactory):
    """
    """

    def __init__(self):
        pass

    def predictions(self, x: ndarray, y: ndarray) -> Predictions:
        """
        Returns an instance of CcrPredictions.
        """
        return CcrPredictions(x, y)


class Ccr(Cc):
    """
    The aesthetic rating subset of the CC dataset.
    """

    NAME = 'ccr'
    OUTPUT_NUM: int = 1

    def __init__(self):
        pass

    def _y(self) -> ndarray:
        """
        Returns the Y as integers.
        """
        data_file = CcDataFile()
        y = asarray(data_file.rating())
        return y

    def _predictions_factory(self) -> PredictionsFactory:
        """
        Returns an instance of PredictionsFactory.
        """
        return CcrPredictionsFactory()


class CcrcPredictions(Predictions):
    """
    """

    @staticmethod
    def _rate(one: float, two: float, three: float) -> float:
        """
        Calculates the predicted rating from percentages.
        """
        total = one + two + three
        x1 = 1 * one
        x2 = 2 * two
        x3 = 3 * three
        rate = (x1 + x2 + x3) / total
        return rate

    def human_readable(self) -> List[Any]:
        """
        """
        return [self._rate(i, j, k) for i, j, k in self._y]


class CcrcPredictionsFactory(PredictionsFactory):
    """
    """

    def __init__(self):
        pass

    def predictions(self, x: ndarray, y: ndarray) -> Predictions:
        """
        """
        return CcrcPredictions(x, y)


class CcrCategorical(Cc):
    """
    The aesthetic rating subset of the CC dataset using categories instead of a number.
    """

    NAME = 'ccrc'
    OUTPUT_NUM: int = 3

    def __init__(self):
        pass

    def _y(self) -> ndarray:
        """
        Returns the Y as one hot arrays.
        """
        data_file = CcDataFile()
        y = data_file.rating()
        y = [i - 1 for i in y]
        y = asarray(y)
        y = self.one_hot(y, 3)
        return y

    def _predictions_factory(self) -> PredictionsFactory:
        """
        Returns an instance of PredictionsFactory.
        """
        return CcrcPredictionsFactory()


modelbuilder.ModelBuilder.dataset(Ccc())
modelbuilder.ModelBuilder.dataset(Ccr())
modelbuilder.ModelBuilder.dataset(CcrCategorical())
