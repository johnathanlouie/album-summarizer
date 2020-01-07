from typing import List

from numpy import asarray

from dataset import DataSet
from jl import CSV_CCDATA, Csv, Url


class CcDataFile(object):
    """
    Represents the data file for the CC dataset.
    Knows the internals of the data file.
    Does not know anything outside of the file itself, such as the paths of the data file and images.
    """

    categories = {
        'environment': 0,
        'people': 1,
        'object': 2,
        'hybrid': 3,
        'animal': 4,
        'food': 5
    }

    def __init__(self, url: Url) -> None:
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


class Ccc(DataSet):
    """
    The image classification subset of the CC dataset.
    """

    name = 'ccc'

    def prepare(self) -> None:
        """
        Reads the data file and produces some splits.
        """
        print("Reading data file")
        data_file = CcDataFile(CSV_CCDATA)
        x = asarray(data_file.url())
        y = asarray(data_file.category_as_int())
        print('Converting to one hot')
        y = self.one_hot(y, 6)
        print('Generating data splits')
        for i in range(5):
            self.create_split(x, y, i)
        print('Prep complete')
        return


class Ccr(DataSet):
    """
    The aesthetic rating subset of the CC dataset.
    """

    name = 'ccr'

    def prepare(self) -> None:
        """
        Create NumPy files for the randomly generated splits.
        """
        print("Reading data file")
        data_file = CcDataFile(CSV_CCDATA)
        x = asarray(data_file.url())
        y = asarray(data_file.rating())
        print('Generating data splits')
        for i in range(5):
            self.create_split(x, y, i)
        print('Prep complete')
        return


class CcrCategorical(DataSet):
    """
    The aesthetic rating subset of the CC dataset using categories instead of a number.
    """

    name = 'ccr-categ'

    def prepare(self) -> None:
        """
        Create NumPy files for the randomly generated splits.
        """
        print("Reading data file")
        data_file = CcDataFile(CSV_CCDATA)
        x = asarray(data_file.url())
        y = data_file.rating()
        y = [i-1 for i in y]
        y = asarray(y)
        y = self.one_hot(y, 3)
        print('Generating data splits')
        for i in range(5):
            self.create_split(x, y, i)
        print('Prep complete')
        return
