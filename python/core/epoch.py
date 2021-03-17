import keras.models
from typing2 import Url

from core.kerashelper import CheckpointObserver, PickleAbstractClass


class EpochPickle(PickleAbstractClass):
    """
    """

    def __init__(self, current_epoch: int) -> None:
        self.current_epoch: int = current_epoch

    def get(self) -> int:
        return self.current_epoch


class EpochObserver(CheckpointObserver):
    """
    """

    def __init__(self, save_location: Url) -> None:
        self._url: Url = save_location

    def callback(
        self,
        kmodel: keras.models.Model,
        epoch: int = None,
        batch: int = None,
    ) -> None:
        EpochPickle(epoch + 1).save(self._url)
