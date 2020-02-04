from enum import Enum
from typing import Any, List, Optional, Tuple, Union

from keras.utils import to_categorical
from numpy import ndarray
from sklearn.model_selection import train_test_split

from jl import ArrayLike, ListFile, Number, Url, npexists, npload, npsave


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
        return '%s/%d/%s.%s' % (self.name, self.split, self.phase.value, self.xy.value)

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

    def exists(self) -> bool:
        """
        Returns true if the file exists.
        """
        return npexists(self)


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

    def exists(self) -> bool:
        """
        Returns true if all files exist.
        """
        if not self.x().exists():
            return False
        if not self.y().exists():
            return False
        return True


class DataSetSplit(object):
    """
    Represents a split of a dataset for cross-validation.
    """

    def __init__(self, dataset: str, split: int) -> None:
        self.dataset = dataset
        self.split = split
        return

    def _get_phase(self, phase: Phase) -> DataSetPhase:
        """
        Gets a phase from this split.
        """
        return DataSetPhase(self.dataset, self.split, phase)

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

    def validation(self) -> DataSetPhase:
        """
        Gets the validation phase from this split.
        """
        return self._get_phase(Phase.VALIDATION)

    def exists(self) -> bool:
        """
        Returns true if all files exist.
        """
        if not self.train().exists():
            return False
        if not self.test().exists():
            return False
        if not self.validation().exists():
            return False
        return True


class Predictions(object):
    """
    An interpreter for predictions.
    """

    def __init__(self, x: ndarray, y: ndarray, url: Url) -> None:
        self._x = x
        self._y = y
        self._url = url
        return

    def human_readable(self) -> List[Any]:
        """
        """
        raise NotImplementedError

    def save_as_list(self) -> None:
        """
        Saves the predictions a human readable format
        """
        ListFile(self._url).write(self.human_readable())
        return


class PredictionsFactory(object):
    """
    """

    def predictions(self, x: ndarray, y: ndarray, url: Url) -> Predictions:
        """
        Returns a concrete instance of Predictions.
        """
        raise NotImplementedError


class DataSet(object):
    """
    Interface for datasets. Mainly used for hints.
    """

    def prepare(self) -> None:
        """
        Reads and convert the dataset data files into NumPy arrays for Keras.
        """
        raise NotImplementedError

    def get_split(self, num: int) -> DataSetSplit:
        """
        Gets the training, testing, and validation split for Keras.
        """
        return DataSetSplit(self.name(), num)

    def train_val_test(
        self,
        xx: ArrayLike,
        yy: ArrayLike,
        test_size: Number = 0.1,
        shuffle: bool = True,
    ) -> Tuple[ndarray, ndarray, ndarray, ndarray, ndarray, ndarray]:
        """
        Divides up the dataset into training, validation, and testing phases.
        """
        vali_size = 1 / self.splits()
        xx, ex, yy, ey = train_test_split(xx, yy, test_size=test_size, train_size=None, shuffle=shuffle)
        tx, vx, ty, vy = train_test_split(xx, yy, test_size=vali_size, train_size=None, shuffle=shuffle)
        return tx, ty, vx, vy, ex, ey

    def create_split(self, x: ndarray, y: ndarray, index: int) -> None:
        """
        Randomly generates a split.
        """
        tx, ty, vx, vy, ex, ey = self.train_val_test(x, y)
        print('Saving....')
        ds = self.get_split(index)
        dtrain = ds.train()
        dval = ds.validation()
        dtest = ds.test()
        dtrain.x().save(tx)
        dtrain.y().save(ty)
        dval.x().save(vx)
        dval.y().save(vy)
        dtest.x().save(ex)
        dtest.y().save(ey)
        return

    def one_hot(self, y: ndarray, num_classes: int) -> ndarray:
        """
        Returns the one hot representation from an array of integers.
        """
        return to_categorical(y, num_classes=num_classes, dtype='int32')

    def get_predictions_factory(self) -> PredictionsFactory:
        """
        Abstract method.
        Returns an instance of PredictionsFactory.
        """
        raise NotImplementedError

    def exists(self) -> bool:
        """
        Returns true if the dataset was already prepared.
        """
        for i in range(self.splits()):
            if not self.get_split(i).exists():
                return False
        return True

    def splits(self) -> int:
        """
        Returns the number of splits.
        """
        raise NotImplementedError

    def name(self) -> str:
        """
        Returns a simple abbreviated name for filenames, command line interface, and factories.
        """
        raise NotImplementedError
