import os
from enum import Enum
from typing import Any, Dict, List, Tuple, Union

import keras
import sklearn.model_selection as sklms
from numpy import asarray, ndarray

from jl import CSV_CCDATA, ArrayLike, Csv, ListFile, Url, npload, npsave


class XY(Enum):
    """
    Used in the dataset classes.
    """
    X = 'x'
    Y = 'y'


class Phase(Enum):
    """
    Used in the dataset classes.
    """
    TRAIN = 'train'
    VALIDATION = 'val'
    TEST = 'test'


class DataSetXY(object):
    """
    Stores or loads an input x or an output y array for deep learning.
    """

    def __init__(self, name: str, split: int, phase: Phase, xy: XY) -> None:
        self.name = name
        self.split = split
        self.phase = phase
        self.xy = xy
        return

    def __str__(self) -> str:
        return '%s.%d.%s.%s' % (self.name, self.split, self.phase, self.xy)

    def __add__(self, other) -> str:
        return str(self) + other

    def __radd__(self, other) -> str:
        return other + str(self)

    def save(self, data: ndarray) -> None:
        """
        Saves a NumPy array as a file.
        """
        npsave(self, data)
        return

    def load(self) -> ndarray:
        """
        Loads a NumPy array from a file.
        """
        return npload(self)


class DataSetPhase(object):
    """
    Represents a training, test, or validation phase for deep learning.
    """

    def __init__(self, name: str, split: int, phase: Phase) -> None:
        self.name = name
        self.split = split
        self.phase = phase
        return

    def _get_xy(self, xy: XY) -> DataSetXY:
        """
        Gets an input x or an output y from this phase.
        """
        return DataSetXY(self.name, self.split, self.phase, xy)

    def x(self) -> DataSetXY:
        """
        Gets the input x from this phase.
        """
        return self._get_xy(XY.X)

    def y(self) -> DataSetXY:
        """
        Gets the input y from this phase.
        """
        return self._get_xy(XY.Y)


class DataSetSplit(object):
    """
    Represents a split of a dataset for cross-validation.
    """

    def __init__(self, name: str, split: int) -> None:
        self.name = name
        self.split = split
        return

    def _get_phase(self, phase: Phase) -> DataSetPhase:
        """
        Gets a phase from this split.
        """
        return DataSetPhase(self.name, self.split, phase)

    def train(self) -> DataSetPhase:
        """
        Gets the training phase from this split.
        """
        return self._get_phase(Phase.TRAIN)

    def test(self) -> DataSetPhase:
        """
        Gets the testing phase from this split.
        """
        return self._get_phase(Phase.TEST)

    def validatation(self) -> DataSetPhase:
        """
        Gets the validation phase from this split.
        """
        return self._get_phase(Phase.VALIDATION)


class DataSet(object):
    """
    Interface for datasets. Mainly used for hints.
    """

    name = ''

    def prepare(self) -> None:
        """
        Reads and convert the dataset data files into NumPy arrays for Keras.
        """
        pass

    def split(self, num: int) -> DataSetSplit:
        """
        Gets the training, testing, and validation split for Keras.
        """
        return DataSetSplit(self.name, num)

    def train_valid_test_split(
        self,
        x: ArrayLike,
        y: ArrayLike,
        test_size: Union[float, int, None] = 0.1,
        valid_size: Union[float, int, None] = 0.1,
        train_size: Union[float, int, None] = None,
        random_state: Union[int, None] = None,
        shuffle: bool = True,
        stratify: Union[ArrayLike, None] = None
    ) -> Tuple[ndarray, ndarray, ndarray, ndarray, ndarray, ndarray]:
        """
        Divides up the dataset into phases.
        """
        if test_size != None:
            dx, ex, dy, ey = sklms.train_test_split(x, y, test_size=test_size, train_size=None, random_state=random_state, shuffle=shuffle, stratify=None)
            tx, vx, ty, vy = sklms.train_test_split(dx, dy, test_size=valid_size, train_size=train_size, random_state=random_state, shuffle=shuffle, stratify=None)
        else:
            dx, vx, vy, vy = sklms.train_test_split(x, y, test_size=valid_size, train_size=None, random_state=random_state, shuffle=shuffle, stratify=None)
            tx, ex, ty, ey = sklms.train_test_split(dx, dy, test_size=test_size, train_size=train_size, random_state=random_state, shuffle=shuffle, stratify=None)
        return tx, ty, vx, vy, ex, ey

    def create_split(self, x: ndarray, y: ndarray, index: int) -> None:
        """
        Randomly generates a split.
        """
        tx, ty, vx, vy, ex, ey = self.train_valid_test_split(x, y)
        print('Saving')
        ds = self.split(index)
        dtrain = ds.train()
        dtest = ds.test()
        dval = ds.validatation()
        dtrain.x().save(tx)
        dtrain.y().save(ty)
        dtest.x().save(ex)
        dtest.y().save(ey)
        dval.x().save(vx)
        dval.y().save(vy)
        return

    def one_hot(self, y: ndarray, num_classes: int) -> ndarray:
        """
        Returns the one hot representation from an array of integers.
        """
        return keras.utils.to_categorical(y, num_classes=num_classes, dtype='int32')


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
