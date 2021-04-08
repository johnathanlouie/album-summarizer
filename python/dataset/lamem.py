from os import getcwd
from os.path import join, normpath
from typing import Any, List

from core import modelbuilder
from core.dataset import DataSet, LabelTranslator
from core.modeltype import OutputType
from jl import ListFile
from numpy import asarray, ndarray
from typing2 import Url


class LamemDataFile(object):
    """
    Represents one of the data files found in the splits directory of the LaMem project.
    """

    def __init__(self, url: Url) -> None:
        self._url = url

    def read(self) -> List[List[str]]:
        """
        Gets the data as a 2D list of strings.
        """
        return [line.split(' ') for line in ListFile(self._url).read()]

    def list_x(self) -> List[str]:
        """
        Gets the x column for deep learning.
        """
        b = asarray(self.read())
        return b[:, 0].tolist()

    def list_y(self) -> List[float]:
        """
        Gets the y column for deep learning.
        """
        b = asarray(self.read())
        return [float(x) for x in b[:, 1]]


class LamemLabelTranslator(LabelTranslator):
    """
    """

    def translate(self, y: List[Any]) -> List[Any]:
        """
        """
        return y


class Lamem(DataSet):
    """
    Dataset used for large scale image memorability.
    """

    NAME = 'lamem'
    OUTPUT_TYPE: OutputType = OutputType.SCALAR
    CLASSES = None

    _phases = ['train', 'test', 'val']

    def _data_file_url(self, split: int, phase: str) -> str:
        """
        Returns the url of a data file.
        """
        return 'data/lamem/splits/%s_%d.txt' % (phase, split)

    def _relative_url(self, url: Url) -> str:
        """
        Returns the relative url of the image from the filename.
        """
        a = join(getcwd(), 'data/lamem/images', url)
        return normpath(a)

    def _prep_data_file(self, split: int, phase: str) -> None:
        """
        Produce 1 input and 1 output NumPy file from the data file.
        """
        url = self._data_file_url(split, phase)
        datafile = LamemDataFile(url)
        x = [self._relative_url(i) for i in datafile.list_x()]
        x = asarray(x)
        y = asarray(datafile.list_y())
        ds = self.get_split(split - 1)
        if phase == self._phases[0]:
            dp = ds.train()
        elif phase == self._phases[1]:
            dp = ds.test()
        elif phase == self._phases[2]:
            dp = ds.validation()
        else:
            raise Exception()
        dp.x().save(x)
        dp.y().save(y)
        return

    def prepare(self) -> None:
        """
        Produce NumPy files from the dataset data files.
        """
        for i in range(1, self.splits() + 1):
            for j in self._phases:
                self._prep_data_file(i, j)
        return

    def splits(self) -> int:
        """
        Returns the number of splits.
        """
        return 5

    def _label_translator(self) -> LabelTranslator:
        """
        """
        return LamemLabelTranslator()


modelbuilder.ModelBuilder.dataset(Lamem())
