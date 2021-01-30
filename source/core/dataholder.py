from __future__ import annotations

from typing import Union

from dill import dump, load
from jl import Url
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
from numpy import greater, less


class LrData(object):
    """
    A picklable class that contains the data fields from ReduceLROnPlateau.
    """

    def __init__(self, lr: ReduceLROnPlateau) -> None:
        self._copy(lr, self)

    @staticmethod
    def _copy(src: Union[LrData, ReduceLROnPlateau], dst: Union[LrData, ReduceLROnPlateau]) -> None:
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
        self._copy(self, other)
        return other


class McpData(object):
    """
    A picklable class that contains the data fields from ModelCheckpoint.
    """

    def __init__(self, mcp: ModelCheckpoint) -> None:
        self._copy(mcp, self)
        self.monitor_op = mcp.monitor_op.__name__

    @staticmethod
    def _copy(src: Union[LrData, ModelCheckpoint], dst: Union[LrData, ModelCheckpoint]) -> None:
        """
        Copies the data from one type to another.
        """
        dst.best = src.best
        dst.epochs_since_last_save = src.epochs_since_last_save
        dst.filepath = src.filepath
        dst.monitor = src.monitor
        dst.period = src.period
        dst.save_best_only = src.save_best_only
        dst.save_weights_only = src.save_weights_only
        dst.verbose = src.verbose

    def get(self) -> ModelCheckpoint:
        """
        Gets a copy of ModelCheckpoint based on this instance data.
        """
        other = ModelCheckpoint('')
        self._copy(self, other)
        if self.monitor_op == 'greater':
            other.monitor_op = greater
        elif self.monitor_op == 'less':
            other.monitor_op = less
        else:
            raise Exception('monitor_op field missing')
        return other


class DataHolder(object):
    """
    Holds the picklable state of training and callbacks.
    """

    def __init__(self, current_epoch: int, lr: ReduceLROnPlateau, mcp: ModelCheckpoint, mcpb: ModelCheckpoint) -> None:
        self.current_epoch = current_epoch
        self._lr = LrData(lr)
        self._mcp = McpData(mcp)
        self._mcpb = McpData(mcpb)

    def get_mcp(self) -> ModelCheckpoint:
        """
        Returns the saved ModelCheckpoint instance.
        """
        return self._mcp.get()

    def get_mcpb(self) -> ModelCheckpoint:
        """
        Returns the saved best ModelCheckpoint instance.
        """
        return self._mcpb.get()

    def get_lr(self) -> ReduceLROnPlateau:
        """
        Returns the saved ReduceLROnPlateau instance.
        """
        return self._lr.get()

    @staticmethod
    def load(url: Url) -> DataHolder:
        """
        Loads a saved instance from a binary file.
        """
        return load(open(url, 'rb'))

    def save(self, url: Url) -> None:
        """
        Saves this instance to a binary file.
        """
        dump(self, open(url, "wb"))
