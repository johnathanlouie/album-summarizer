from __future__ import annotations

from typing import Union

import keras
from keras.callbacks import ReduceLROnPlateau
from typing2 import Url

from core.kerashelper import CheckpointObserver, PickleAbstractClass


class ReduceLROnPlateauPickle(PickleAbstractClass):
    """
    A picklable class that contains the data fields from ReduceLROnPlateau.
    """

    def __init__(self, lr: ReduceLROnPlateau) -> None:
        self._copyTo(lr, self)

    @staticmethod
    def _copyTo(
        src: Union[ReduceLROnPlateauPickle, ReduceLROnPlateau],
        dst: Union[ReduceLROnPlateauPickle, ReduceLROnPlateau],
    ) -> None:
        """
        Copies the data from one type to another.
        """
        dst.best = src.best
        dst.cooldown = src.cooldown
        dst.cooldown_counter = src.cooldown_counter
        dst.factor = src.factor
        dst.min_delta = src.min_delta
        dst.min_lr = src.min_lr
        dst.mode = src.mode
        dst.monitor = src.monitor
        dst.patience = src.patience
        dst.verbose = src.verbose
        dst.wait = src.wait

    def get(self) -> ReduceLROnPlateau:
        """
        Gets a copy of ReduceLROnPlateau based on this instance data.
        """
        other = ReduceLROnPlateau()
        self._copyTo(self, other)
        return other


class ReduceLROnPlateauObserver(CheckpointObserver):
    """
    """

    def __init__(self, save_location: Url, lr: ReduceLROnPlateau):
        self._url: Url = save_location
        self._lr: ReduceLROnPlateau = lr

    def callback(
        self,
        kmodel: keras.models.Model,
        epoch: int = None,
        batch: int = None,
    ) -> None:
        ReduceLROnPlateauPickle(self._lr).save(self._url)
