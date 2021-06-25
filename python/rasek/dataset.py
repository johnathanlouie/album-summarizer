import abc
import csv
import os
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas
from numpy import ndarray

import rasek.helpers
from rasek.typing2 import Primitive, Url


class DataSource(abc.ABC):
    """
    A source of data for datasets.
    """

    @abc.abstractmethod
    def x(self) -> Optional[ndarray]:
        pass

    @abc.abstractmethod
    def y(self) -> Optional[ndarray]:
        pass


class TabularDataFile(DataSource):
    """
    CSVs with commas, tabs, or spaces or single column files.
    """

    def __init__(
        self,
        filepath: Url,
        x: Optional[List[int]] = None,
        y: Optional[List[int]] = None,
        has_header: Optional[bool] = None,
    ) -> None:
        """
        has_header is None, then it automatically detects if there is a header.
        """
        super().__init__()
        with open(filepath) as f:
            sniffer = csv.Sniffer()
            if has_header == None:
                has_header = sniffer.has_header(f.read())
                f.seek(0)
            try:
                delimiter = sniffer.sniff(f.read(), ',\t ').delimiter
            except:
                delimiter = ','
        if has_header:
            self._data_frame = pandas.read_csv(filepath, sep=delimiter, header=0)
        else:
            self._data_frame = pandas.read_csv(filepath, sep=delimiter, header=None)
        self._xcols = x
        self._ycols = y

    def x(self) -> Optional[ndarray]:
        if self._xcols == None:
            return None
        return self._data_frame.values[:, self._xcols]

    def y(self) -> Optional[ndarray]:
        if self._xcols == None:
            return None
        return self._data_frame.values[:, self._ycols]


class ImageDirectory(DataSource):
    """
    Represents a directory and its subdirectories containing image files.
    """

    def __init__(self, filepath: Url, y_value: Primitive, k: Optional[int] = None, recursive: bool = False) -> None:
        if not os.path.isdir(filepath):
            raise NotADirectoryError
        files = rasek.helpers.list_files(filepath, recursive)
        images = list(filter(rasek.helpers.is_image, files))
        self._images = rasek.helpers.sample(images, k)
        self._y_value = y_value

    def x(self) -> ndarray:
        """
        Returns an array of image filepaths from this directory.
        """
        return np.asarray(self._images)

    def y(self) -> ndarray:
        """
        Returns an array of [value] the same size as x.
        """
        return np.full(len(self._images), self._y_value)
