from abc import abstractmethod
from os import getcwd
from os.path import join, normpath
from typing import Any, List, Optional

from rasek import modelbuilder
from rasek.dataset import DataSet, LabelTranslator
from rasek.jl import Csv
from rasek.modeltype import OutputType
from rasek.typing2 import Url
from numpy import asarray, ndarray


class CcDataFile(object):
    """
    Represents the data file for the CC dataset.
    Knows the URL and internals of the data file.
    Does not know the paths of the images.
    """

    URL = 'data/cc/data.csv'

    CLASSES = [
        'environment',
        'people',
        'object',
        'hybrid',
        'animal',
        'food',
    ]

    categories = {
        'environment': 0,
        'people': 1,
        'object': 2,
        'hybrid': 3,
        'animal': 4,
        'food': 5,
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
        if type(e) is not int:
            raise ValueError("Type Error: Got type %s instead of int" % type(e))
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

    def _relative_url(self, url: Url) -> str:
        """
        Returns the relative url of the image from the filename.
        """
        return normpath(join(getcwd(), 'data', 'cc', url))

    def _x(self) -> ndarray:
        """
        Returns an array of URLs to the images.
        """
        return asarray([self._relative_url(i) for i in CcDataFile().url()])

    @abstractmethod
    def _y(self) -> ndarray:
        """
        Returns the Y. To be implemented by subclass.
        """
        pass

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


class CccLabelTranslator(LabelTranslator):
    """
    """

    def translate(self, y: List[Any]) -> List[Any]:
        """
        """
        return CcDataFile().to_category_str(y)


class Ccc(Cc):
    """
    The image classification subset of the CC dataset.
    """

    NAME = 'ccc'
    OUTPUT_TYPE: OutputType = OutputType.ONE_HOT
    CLASSES: int = 6

    def _y(self) -> ndarray:
        """
        Returns the Y as one hot arrays.
        """
        data_file = CcDataFile()
        y = asarray(data_file.category_as_int())
        y = self.one_hot(y, 6)
        return y

    def _label_translator(self) -> LabelTranslator:
        """
        """
        return CccLabelTranslator()

    @staticmethod
    def classes() -> List[str]:
        return CcDataFile.CLASSES.copy()


class CcrLabelTranslator(LabelTranslator):
    """
    """

    def translate(self, y: List[Any]) -> List[Any]:
        """
        Translates the predicted output.
        """
        return y


class Ccr(Cc):
    """
    The aesthetic rating subset of the CC dataset.
    """

    NAME = 'ccr'
    OUTPUT_TYPE: OutputType = OutputType.SCALAR
    CLASSES = None

    def _y(self) -> ndarray:
        """
        Returns the Y as integers.
        """
        data_file = CcDataFile()
        y = asarray(data_file.rating())
        return y

    def _label_translator(self) -> LabelTranslator:
        """
        Returns an instance of PredictionsFactory.
        """
        return CcrLabelTranslator()


class CcrcLabelTranslator(LabelTranslator):
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

    def translate(self, y: List[Any]) -> List[Any]:
        """
        """
        return [self._rate(i, j, k) for i, j, k in y]


class CcrCategorical(Cc):
    """
    The aesthetic rating subset of the CC dataset using categories instead of a number.
    """

    NAME = 'ccrc'
    OUTPUT_TYPE: OutputType = OutputType.ONE_HOT
    CLASSES = 3

    def _y(self) -> ndarray:
        """
        Returns the Y as one hot arrays.
        """
        y = [i - 1 for i in CcDataFile().rating()]
        y = asarray(y)
        y = self.one_hot(y, 3)
        return y

    def _label_translator(self) -> LabelTranslator:
        """
        Returns an instance of PredictionsFactory.
        """
        return CcrcLabelTranslator()

    @staticmethod
    def classes() -> List[str]:
        return ['bad', 'average', 'good']


modelbuilder.ModelBuilder.dataset(Ccc())
modelbuilder.ModelBuilder.dataset(Ccr())
modelbuilder.ModelBuilder.dataset(CcrCategorical())
