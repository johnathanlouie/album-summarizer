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

    def __init__(self, url: str):
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


class Lamem:
    """Dataset used for large scale image memorability."""

    name = 'lamem'
    splits = range(1, 6)
    phases = [
        ('train', DataSetSplitFactory.TRAIN),
        ('val', DataSetSplitFactory.VALIDATION),
        ('test', DataSetSplitFactory.TEST)
    ]

    @staticmethod
    def read(phase, split):
        filename = 'lamem/splits/%s_%d.txt' % (phase, split)
        b = np.asarray([line.split(' ') for line in jl.readtxt(filename)])
        x = np.asarray(b[:, 0])
        y = np.asarray([float(x) for x in b[:, 1]])
        return x, y

    @staticmethod
    def rel_url(url):
        a = os.path.join(os.getcwd(), 'lamem/images', url)
        return os.path.normpath(a)

    @classmethod
    def prep_txt(cls, phase, split) -> None:
        x, y = cls.read(phase[0], split)
        x = np.asarray([cls.rel_url(url) for url in x])
        y = np.asarray(y)
        ds = DataSetSplitFactory(cls.name, split)
        ds.x(phase[1]).save(x)
        ds.y(phase[1]).save(y)
        return

    @classmethod
    def prep(cls) -> None:
        for j in cls.phases:
            for i in cls.splits:
                cls.prep_txt(j, i)
        return
