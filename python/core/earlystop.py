from __future__ import annotations

from typing import Union

import keras
import numpy as np
from keras.callbacks import EarlyStopping
from typing2 import Url

from core.kerashelper import CheckpointObserver, PickleAbstractClass


class EarlyStoppingPickle(PickleAbstractClass):
    """
    A picklable class that contains the data fields from ReduceLROnPlateau.
    """

    def __init__(self, es: EarlyStopping) -> None:
        self._copyTo(es, self)
        self.monitor_op = es.monitor_op.__name__

    @staticmethod
    def _copyTo(
        src: Union[EarlyStoppingPickle, EarlyStopping],
        dst: Union[EarlyStoppingPickle, EarlyStopping],
    ) -> None:
        """
        Copies the data from one type to another.
        """
        dst.monitor = src.monitor
        dst.baseline = src.baseline
        dst.patience = src.patience
        dst.verbose = src.verbose
        dst.min_delta = src.min_delta
        dst.wait = src.wait
        dst.stopped_epoch = src.stopped_epoch
        dst.restore_best_weights = src.restore_best_weights
        dst.best_weights = src.best_weights
        if hasattr(src, 'best'):
            dst.best = src.best

    def get(self) -> EarlyStopping:
        """
        Gets a copy of ReduceLROnPlateau based on this instance data.
        """
        other = EarlyStopping()
        self._copyTo(self, other)
        if self.monitor_op == 'greater':
            other.monitor_op = np.greater
        elif self.monitor_op == 'less':
            other.monitor_op = np.less
        else:
            raise Exception('monitor_op field missing')
        return other


class EarlyStoppingObserver(CheckpointObserver):
    """
    """

    def __init__(self, save_location: Url, es: EarlyStopping):
        self._url: Url = save_location
        self._es: EarlyStopping = es

    def callback(
        self,
        kmodel: keras.models.Model,
        epoch: int = None,
        batch: int = None,
    ) -> None:
        EarlyStoppingPickle(self._es).save(self._url)
