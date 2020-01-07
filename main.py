from __future__ import annotations

import os
import warnings
from os.path import isfile
from typing import Any, Dict, List, Tuple, Union

import dill
import keras
import numpy as np
from keras.callbacks import (Callback, CSVLogger, ModelCheckpoint,
                             ReduceLROnPlateau)
from keras.models import load_model

import cv2 as cv
from dataset import DataSet, DataSetSplit
from jl import ListFile, Url, mkdirs, resize_img
from model import Architecture

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def resize_imgs(src: Url, dst: Url) -> None:
    """
    Resizes the images based on the list of URLs found in the source file and outputs to the list of URLs found in the destination file.
    """
    urls1 = ListFile(src).read()
    urls2 = ListFile(dst).read()
    resize_imgs2(urls1, urls2)
    return


def resize_imgs2(src_list: List[Url], dst_list: List[Url]) -> None:
    """
    Resizes a list of images.
    """
    for src, dst in zip(src_list, dst_list):
        print(src)
        print(dst)
        img2 = resize_img(src)
        mkdirs(dst)
        cv.imwrite(dst, img2)
    print('done')
    return


class Sequence1(keras.utils.Sequence):
    """Generate batches of data."""

    def __init__(self, x_set, y_set, batch_size):
        self.x = x_set
        self.y = y_set
        self.batch_size = batch_size

    def __len__(self):
        a = float(len(self.x)) / float(self.batch_size)
        a = int(np.ceil(a))
        return a

    def __getitem__(self, idx):
        a = idx * self.batch_size
        b = (idx + 1) * self.batch_size
        batch_x = self.x[a:b]
        batch_y = self.y[a:b]
        xx = np.asarray([resize_img(filename) for filename in batch_x])
        yy = np.asarray(batch_y)
        return xx, yy


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


class PickleCheckpoint(Callback):
    """
    Save the model after every epoch.
    `filepath` can contain named formatting options,
    which will be filled with the values of `epoch` and
    keys in `logs` (passed in `on_epoch_end`).
    For example: if `filepath` is `weights.{epoch:02d}-{val_loss:.2f}.hdf5`,
    then the model checkpoints will be saved with the epoch number and
    the validation loss in the filename.
    # Arguments
        filepath: string, path to save the model file.
        monitor: quantity to monitor.
        verbose: verbosity mode, 0 or 1.
        save_best_only: if `save_best_only=True`,
            the latest best model according to
            the quantity monitored will not be overwritten.
        save_weights_only: if True, then only the model's weights will be
            saved (`model.save_weights(filepath)`), else the full model
            is saved (`model.save(filepath)`).
        mode: one of {auto, min, max}.
            If `save_best_only=True`, the decision
            to overwrite the current save file is made
            based on either the maximization or the
            minimization of the monitored quantity. For `val_acc`,
            this should be `max`, for `val_loss` this should
            be `min`, etc. In `auto` mode, the direction is
            automatically inferred from the name of the monitored quantity.
        period: Interval (number of epochs) between checkpoints.
    """

    def __init__(self, mcp: ModelCheckpoint, lr: ReduceLROnPlateau, archisplit: str,  total_epoch: int = 2**64) -> None:
        super(PickleCheckpoint, self).__init__()
        self._mcp = mcp
        self._copy_mcp(mcp)
        self._lr = lr
        self._total_epoch = total_epoch
        self._archisplit = archisplit

    def on_epoch_end(self, epoch, logs=None) -> None:
        logs = logs or {}
        self.epochs_since_last_save += 1
        current_epoch = epoch + 1
        url = DataHolder.url(self._archisplit)
        if self.epochs_since_last_save >= self.period:
            self.epochs_since_last_save = 0
            filepath = self.filepath.format(epoch=epoch + 1, **logs)
            if self.save_best_only:
                current = logs.get(self.monitor)
                if current is None:
                    warnings.warn('Can save best Keras callback objects only with %s available, skipping.' % (self.monitor), RuntimeWarning)
                else:
                    if self.monitor_op(current, self.best):
                        if self.verbose > 0:
                            print('\nEpoch %05d: %s improved from %0.5f to %0.5f, saving Keras callback objects to %s' % (epoch + 1, self.monitor, self.best, current, filepath))
                        self.best = current
                        dh = DataHolder(url, current_epoch, self._total_epoch, self._lr, self._mcp)
                        if self.save_weights_only:
                            dh.save()
                        else:
                            dh.save()
                    else:
                        if self.verbose > 0:
                            print('\nEpoch %05d: %s did not improve from %0.5f' % (epoch + 1, self.monitor, self.best))
            else:
                if self.verbose > 0:
                    print('\nEpoch %05d: saving Keras callback objects to %s' % (epoch + 1, filepath))
                dh = DataHolder(url, current_epoch, self._total_epoch, self._lr, self._mcp)
                if self.save_weights_only:
                    dh.save()
                else:
                    dh.save()

    def _copy_mcp(self, mcp: ModelCheckpoint) -> None:
        """
        Copies a ModelCheckpoint instance.
        """
        self.best = mcp.best
        self.epochs_since_last_save = mcp.epochs_since_last_save
        self.filepath = mcp.filepath
        self.monitor = mcp.monitor
        self.period = mcp.period
        self.save_best_only = mcp.save_best_only
        self.save_weights_only = mcp.save_weights_only
        self.verbose = mcp.verbose
        self.monitor_op = mcp.monitor_op
        return


class TerminateOnDemand(Callback):
    """Callback that terminates training when a NaN loss is encountered."""

    def on_epoch_begin(self, epoch, logs) -> None:
        lr = keras.backend.get_value(self.model.optimizer.lr)
        print('Learning rate: %f' % (lr))

    def on_epoch_end(self, epoch, logs=None) -> None:
        with open('gen/terminate.txt', 'r') as f:
            a = f.read()
            if a == 'die':
                print('Manual early terminate command found in gen/terminate.txt')
                self.stopped_epoch = epoch
                self.model.stop_training = True


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


class ArchitectureSplit(object):
    """
    Produced by the ArchitectureSet class.
    A combination of the ArchitectureSet class and the DataSetSplit class.
    Trains, validates, tests, and predicts.
    """

    def __init__(self, architecture: Architecture, split: DataSetSplit) -> None:
        self._architecture = architecture
        self._split = split
        self._continue()

    def name(self) -> str:
        """
        Returns the unique identifier of this combination of architecture, dataset, and compile options.
        """
        return "%s.%s.%d" % (self._architecture.name(), self._split.name, self._split.split)

    def _model_url(self) -> str:
        """
        Returns the URL of the model save file.
        """
        return "gen/%s.h5" % (self.name())

    def train(self) -> None:
        """
        Trains the model.
        """
        print('Loading training X')
        x1 = self._split.train().x().load()
        print('Loading training Y')
        y1 = self._split.train().y().load()
        print('Loading validation X')
        x2 = self._split.validatation().x().load()
        print('Loading validation Y')
        y2 = self._split.validatation().y().load()
        print('Training sequence')
        seq1 = Sequence1(x1, y1, 10)
        print('Validation sequence')
        seq2 = Sequence1(x2, y2, 10)
        print('Training starts')
        term = TerminateOnDemand()
        csv = CSVLogger('gen/training.csv', append=True)
        self._model.fit_generator(
            generator=seq1,
            epochs=1000,
            verbose=1,
            validation_data=seq2,
            shuffle=False,
            initial_epoch=self._mcp.epoch,
            callbacks=[
                self._lr,
                self._mcp,
                self._pcp,
                csv,
                term
            ]
        )
        print('Training finished')
        return

    def validate(self) -> None:
        """
        Tests the model using the validation set.
        """
        print('Loading validation X')
        x = self._split.validatation().x().load()
        print('Loading validation Y')
        y = self._split.validatation().y().load()
        print('Validation sequence')
        seq = Sequence1(x, y, 10)
        print('Validation starts')
        results = self._model.evaluate_generator(generator=seq, verbose=1)
        print('Validation finished')
        if type(results) != list:
            results = [results]
        for metric, scalar in zip(self._model.metrics_names, results):
            print('%s: %f' % (metric, scalar))
        return

    def test(self) -> None:
        """
        Tests the model using the test set.
        """
        print('Loading test X')
        x = self._split.test().x().load()
        print('Loading test Y')
        y = self._split.test().y().load()
        print('Testing sequence')
        seq = Sequence1(x, y, 10)
        print('Testing starts')
        results = self._model.evaluate_generator(generator=seq, verbose=1)
        print('Testing finished')
        if type(results) != list:
            results = [results]
        for metric, scalar in zip(self._model.metrics_names, results):
            print('%s: %f' % (metric, scalar))
        return

    def predict(self) -> None:
        """
        Predicts using the trained model.
        """
        print('Loading test X')
        x = self._split.test().x().load()
        print('Loading test Y')
        y = self._split.test().y().load()
        print('Prediction sequence')
        seq = Sequence1(x, y, 10)
        print('Prediction starts')
        results = self._model.predict_generator(generator=seq, verbose=1)
        print('Prediction finished')
        if len(results.shape) == 2:
            if results.shape[1] == 1:
                results = results.flatten()
            else:
                results = results.argmax(1)
                # results = class_str_int(results)
        results_file = 'gen/pred.txt'
        ListFile(results_file).write(results)
        print('Saved predictions to %s' % (results_file))
        return results

    def _create(self) -> None:
        """
        Creates and saves the model file and other training state files.
        Initial settings are found here.
        """
        self._architecture.compile().save(self._model_url())
        mcp = ModelCheckpoint(self._model_url(), verbose=1, save_best_only=True)
        lr = ReduceLROnPlateau(patience=5, verbose=1)
        dh_url = DataHolder.url(self.name())
        dh = DataHolder(dh_url, 0, 1000, lr, mcp)
        dh.save()
        return

    def _load(self) -> None:
        """
        Loads the model file and other training state files.
        """
        self._model = load_model(self._model_url(), self._architecture.custom())
        dh_url = DataHolder.url(self.name())
        dh = DataHolder.load(dh_url)
        self._lr = dh.get_lr()
        self._mcp = dh.get_mcp
        self._pcp = PickleCheckpoint(self._mcp, self._lr, self.name())
        return

    def _delete(self) -> None:
        """
        Deletes the model file and other training state files.
        Not implemented since _load overwrites.
        """
        return

    def _continue(self) -> None:
        """
        Loads the saved files if they exist.
        Create and load them if they do not exist.
        """
        if not isfile(self._model_url()):
            self._create()
        self._load()
        return

    def reset(self) -> None:
        """
        Starts the training process from the beginning.
        """
        self._delete()
        self._create()
        self._load()
        return


class ArchitectureSet(object):
    """
    A combination of a DataSet object and Architecture object.
    It oversees the cross-validation process, which is training and testing over multiple splits.
    Each split is handled by an ArchitectureSplit object produced by this class.
    """

    def __init__(self, architecture: Architecture, dataset: DataSet) -> None:
        self._architecture = architecture
        self._dataset = dataset
        return

    def split(self, num: int) -> ArchitectureSplit:
        """
        Get a specific split.
        """
        return ArchitectureSplit(self._architecture, self._dataset.split(num))


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
