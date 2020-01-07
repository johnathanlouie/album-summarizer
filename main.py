from __future__ import annotations

import os
from os.path import isfile
from typing import Any, Dict, List, Tuple, Union

import dill
import keras
import numpy as np
from keras.callbacks import (Callback, CSVLogger, ModelCheckpoint,
                             ReduceLROnPlateau)
from keras.models import load_model

import cv2 as cv
from cc import Ccr
from dataset import DataSet, DataSetSplit
from jl import ListFile, Url, mkdirs, resize_img
from model import LOSS, METRIC, OPTIMIZER, Architecture
from rater import Smi13

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class LrData(object):
    """
    A picklable class that contains the data fields from ReduceLROnPlateau.
    """

    def __init__(self, lr: ReduceLROnPlateau) -> None:
        self._copy(lr, self)
        return

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
        return

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
        return

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
        return

    def get(self) -> ModelCheckpoint:
        """
        Gets a copy of ModelCheckpoint based on this instance data.
        """
        other = ModelCheckpoint('')
        self._copy(self, other)
        if self.monitor_op == 'greater':
            other.monitor_op = np.greater
        elif self.monitor_op == 'less':
            other.monitor_op = np.less
        else:
            raise Exception('monitor_op field missing')
        return other


class DataHolder(object):
    """
    Holds the picklable state of training and callbacks.
    """

    def __init__(self, url: str, current_epoch: int, total_epoch: int, lr: ReduceLROnPlateau, mcp: ModelCheckpoint) -> None:
        self._url = url
        self.current_epoch = current_epoch
        self.total_epoch = total_epoch
        self._lr = LrData(lr)
        self._mcp = McpData(mcp)
        return

    def get_mcp(self) -> ModelCheckpoint:
        """
        Returns the saved ModelCheckpoint instance.
        """
        return self._mcp.get()

    def get_lr(self) -> ReduceLROnPlateau:
        """
        Returns the saved ReduceLROnPlateau instance.
        """
        return self._lr.get()

    @staticmethod
    def load(url) -> DataHolder:
        """
        Loads a saved instance from a binary file.
        """
        return dill.load(open(url, 'rb'))

    def save(self) -> None:
        """
        Saves this instance to a binary file.
        """
        dill.dump(self, open(self._url, "wb"))
        return

    @staticmethod
    def url(archisplit: str) -> str:
        """
        Returns the filepath of the dill file for the training status.
        """
        return "gen/%s.dill" % (archisplit)


class ModelName:
    def __init__(self, architecture, version, loss, optimizer):
        self.architecture = architecture
        self.version = version
        self.loss = loss
        self.optimizer = optimizer
        return

    def __str__(self):
        return '%s.%d.%s.%s' % (self.architecture, self.version, self.loss, self.optimizer)

    def __add__(self, other):
        return str(self) + other

    def __radd__(self, other):
        return other + str(self)


class DataModelName:
    def __init__(self, model, dataset):
        self._model_name = model
        self._ds = dataset
        return

    def pickle(self):
        return 'gen/%s.%s.p' % (self._model_name, self._ds)

    def model(self):
        return 'gen/%s.%s.h5' % (self._model_name, self._ds)

    def training(self):
        return 'gen/%s.%s.train.h5' % (self._model_name, self._ds)


# ccr = Ccr()
# # ccr.prepare()
# smi13_1 = Architecture(Smi13(), LOSS[14], OPTIMIZER[0], METRIC[0])
# ccr1 = ArchitectureSet(smi13_1, ccr)
# ccr1_1 = ccr1.split(1)
# # ccr1_1.reset()
# ccr1_1.train()

# ccc_prep()
# model.ccc()
# train('vgg16', 'ccc', 1)
# test('vgg16', 'ccc', 1)
# predict('vgg16', 'ccc', 1)

# ccc_prep()
# model.ccc2()
# train('vgg16a', 'ccc', 1)
# test('vgg16a', 'ccc', 1)
# predict('vgg16a', 'ccc', 1)

# ccc_prep()
# model.ccc3()
# train('vgg16b', 'ccc', 1)
# test('vgg16b', 'ccc', 1)
# predict('vgg16b', 'ccc', 1)

# ccr_prep()
# model.ccr()
# train('kcnn', 'ccr', 1, custom=model.custom_rmse)
# test('kcnn', 'ccr', 1, custom=model.custom_rmse)
# predict('kcnn', 'ccr', 1, custom=model.custom_rmse)

# lamem_prep_all()
# model.lamem()
# train('kcnn', 'lamem', 1, custom=model.custom_rmse)
# test('kcnn', 'lamem', 1, custom=model.custom_rmse)
# predict('kcnn', 'lamem', 1, custom=model.custom_rmse)
