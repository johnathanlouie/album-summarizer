import os
from enum import Enum
from typing import Any, Dict, List, Tuple

import keras
import numpy as np

import jl


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

    def save(self, data: np.ndarray) -> None:
        """
        Saves a NumPy array as a file.
        """
        jl.npsave(self, data)
        return

    def load(self) -> np.ndarray:
        """
        Loads a NumPy array from a file.
        """
        return jl.npload(self)


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
        pass


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

    def __init__(self, url: str) -> None:
        self._csv = jl.Csv(url)
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

    def url(self) -> List[str]:
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


class Ccc:
    name = 'ccc'

    @classmethod
    def prep(cls) -> None:
        print("Reading data file")
        x = jl.getcol(0)
        y = jl.getcol(2)
        y = jl.class_str_int(y)
        print('Generating data splits')
        tx, ty, vx, vy, ex, ey = jl.train_valid_test_split(x, y, test_size=0.1, valid_size=0.1)
        print('Converting to one hot')
        ty = keras.utils.to_categorical(ty, num_classes=6, dtype='int32')
        vy = keras.utils.to_categorical(vy, num_classes=6, dtype='int32')
        ey = keras.utils.to_categorical(ey, num_classes=6, dtype='int32')
        print('Saving')
        ds = DataSetSplitFactory(cls.name, 1)
        ds.xtrain().save(tx)
        ds.xtrain().save(vx)
        ds.xtrain().save(ex)
        ds.ytrain().save(ty)
        ds.ytrain().save(vy)
        ds.ytrain().save(ey)
        print('Prep complete')
        return


class Ccr:
    name = 'ccr'

    @classmethod
    def prep(cls) -> None:
        print("Reading data file")
        x = jl.getcol(0)
        y = jl.getcol(1)
        y = jl.intize(y)
        print('Generating data splits')
        tx, ty, vx, vy, ex, ey = jl.train_valid_test_split(x, y, test_size=0.1, valid_size=0.1)
        print('Saving')
        ds = DataSetSplitFactory(cls.name, 1)
        ds.xtrain().save(tx)
        ds.xtrain().save(vx)
        ds.xtrain().save(ex)
        ds.ytrain().save(ty)
        ds.ytrain().save(vy)
        ds.ytrain().save(ey)
        print('Prep complete')
        return


class LamemDataFile(object):
    """
    Represents one of the data files found in the splits directory of the LaMem project.
    """

    def __init__(self, url: str) -> None:
        self._url = url

    def read(self) -> List[List[str]]:
        """
        Gets the data as a 2D list of strings.
        """
        return [line.split(' ') for line in jl.readtxt(self._url)]

    def list_x(self) -> List[str]:
        """
        Gets the x column for deep learning.
        """
        b = np.asarray(self.read())
        return b[:, 0].tolist()

    def list_y(self) -> List[float]:
        """
        Gets the y column for deep learning.
        """
        b = np.asarray(self.read())
        return [float(x) for x in b[:, 1]]


class Lamem(DataSet):
    """
    Dataset used for large scale image memorability.
    """

    name = 'lamem'
    _splits = range(1, 6)
    _phases = ['train', 'test', 'val']

    def split(self, num: int) -> DataSetSplit:
        """
        Gets the training, testing, and validation split for Keras.
        """
        return DataSetSplit(self.name, num)

    def _data_file_url(self, split: int, phase: str) -> str:
        """
        Returns the url of a data file.
        """
        return 'lamem/splits/%s_%d.txt' % (phase, split)

    def _relative_url(self, url: str) -> str:
        """
        Returns the relative url of the image from the filename.
        """
        a = os.path.join(os.getcwd(), 'lamem/images', url)
        return os.path.normpath(a)

    def _prep_data_file(self, split: int, phase: str) -> None:
        """
        Produce 1 input and 1 output NumPy file from the data file.
        """
        url = self._data_file_url(split, phase)
        datafile = LamemDataFile(url)
        x = np.asarray(datafile.list_x())
        y = np.asarray(datafile.list_x())
        ds = self.split(split - 1)
        if phase == self._phases[0]:
            dp = ds.train()
        elif phase == self._phases[1]:
            dp = ds.test()
        elif phase == self._phases[2]:
            dp = ds.validatation()
        else:
            raise Exception()
        dp.x().save(x)
        dp.y().save(y)
        return

    def prepare(self) -> None:
        """
        Produce NumPy files from the dataset data files.
        """
        for i in self._splits:
            for j in self._phases:
                self._prep_data_file(i, j)
        return
