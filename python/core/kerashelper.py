from __future__ import annotations

import enum
import sys
import warnings
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union

import dill
import keras
import numpy as np
from jl import Resolution, Url, resize_img
from keras.callbacks import Callback
from keras.utils import Sequence
from numpy import asarray, ceil, ndarray


class Sequence1(Sequence):
    """
    Generate batches of data.
    """

    def __init__(self, x_set: ndarray, y_set: ndarray, res: Resolution, batch_size: int):
        self.x = x_set
        self.y = y_set
        self.batch_size = batch_size
        self._res = res

    def __len__(self):
        a = float(len(self.x)) / float(self.batch_size)
        a = int(ceil(a))
        return a

    def __getitem__(self, idx):
        a = idx * self.batch_size
        b = (idx + 1) * self.batch_size
        batch_x = self.x[a:b]
        batch_y = self.y[a:b]
        xx = asarray([resize_img(filename, self._res) for filename in batch_x])
        yy = asarray(batch_y)
        return xx, yy


class TrainingStatus(enum.Enum):
    TRAINING = 'training'
    COMPLETE = 'complete'
    NANINF = 'nan or inf error'
    RESOURCE = 'resource error'


class TrainingStatusData(object):
    """
    """

    def __init__(self, url: Url):
        self.status: TrainingStatus = TrainingStatus.TRAINING
        self._url: Url = url

    def save(self, verbose: bool = True) -> None:
        if verbose:
            print('Saving %s' % self._url)
        with open(self._url, 'w') as f:
            f.write(self.status.value)

    def is_complete(self) -> bool:
        return self.status == TrainingStatus.COMPLETE

    @classmethod
    def load(cls, url: Url, verbose: bool = True) -> TrainingStatusData:
        if verbose:
            print('Loading %s' % url)
        with open(url) as f:
            self = cls(url)
            self.status = TrainingStatus(f.read())
            return self


class PickleAbstractClass(ABC):
    """
    """

    @abstractmethod
    def get(self) -> Any:
        pass

    def save(self, save_location: Url, verbose: bool = True) -> None:
        if verbose:
            print('Saving %s' % save_location)
        dill.dump(self, open(save_location, 'wb'))

    @staticmethod
    def load(save_location: Url, verbose: bool = True) -> PickleAbstractClass:
        if verbose:
            print('Loading %s' % save_location)
        return dill.load(open(save_location, 'rb'))


class ModelCheckpoint2Pickle(PickleAbstractClass):
    """
    """

    def __init__(self, mcp: ModelCheckpoint2) -> None:
        self._copyTo(mcp, self)
        self.monitor_op = mcp.monitor_op.__name__

    @staticmethod
    def _copyTo(
        src: Union[ModelCheckpoint2, ModelCheckpoint2Pickle],
        dst: Union[ModelCheckpoint2, ModelCheckpoint2Pickle]
    ) -> None:
        """
        Copies the data from one type to another.
        """
        dst.best = src.best
        dst.epochs_since_last_save = src.epochs_since_last_save
        dst.monitor = src.monitor
        dst.period = src.period
        dst.patience = src.patience
        dst.wait = src.wait
        dst.total_epochs = src.total_epochs

    def get(self) -> ModelCheckpoint2:
        """
        Gets a copy of ModelCheckpoint2 based on this instance data.
        """
        mcp = ModelCheckpoint2()
        self._copyTo(self, mcp)
        if self.monitor_op == 'greater':
            mcp.monitor_op = np.greater
        elif self.monitor_op == 'less':
            mcp.monitor_op = np.less
        else:
            raise Exception('monitor_op field missing')
        return mcp


class CheckpointObserver(ABC):
    """
    Observer interface for ModelCheckpoint2.
    """

    @abstractmethod
    def callback(
        self,
        kmodel: keras.models.Model,
        epoch: int = None,
        batch: int = None,
    ) -> None:
        pass


class ModelCheckpoint2Observer(CheckpointObserver):
    """
    """

    def __init__(self, url: Url, mcp: ModelCheckpoint2):
        self._mcp = mcp
        self._url = url

    def callback(
        self,
        kmodel: keras.models.Model,
        epoch: int = None,
        batch: int = None,
    ) -> None:
        ModelCheckpoint2Pickle(self._mcp).save(self._url)


class SaveKmodelObserver(CheckpointObserver):
    """
    """

    def __init__(self, save_location: Url):
        self._url: Url = save_location

    def callback(
        self,
        kmodel: keras.models.Model,
        epoch: int = None,
        batch: int = None,
    ) -> None:
        print('Saving %s' % self._url)
        kmodel.save_weights(self._url, overwrite=True)


class NanInfStatusObserver(CheckpointObserver):
    """
    """

    def __init__(self, status: TrainingStatusData):
        self._status = status

    def callback(
        self,
        kmodel: keras.models.Model,
        epoch: int = None,
        batch: int = None,
    ) -> None:
        self._status.status = TrainingStatus.NANINF
        self._status.save()


class CompletionStatusObserver(CheckpointObserver):
    """
    """

    def __init__(self, status: TrainingStatusData):
        self._status = status

    def callback(
        self,
        kmodel: keras.models.Model,
        epoch: int = None,
        batch: int = None,
    ) -> None:
        self._status.status = TrainingStatus.COMPLETE
        self._status.save()


class TerminateOnNanInfObserver(CheckpointObserver):
    """
    """

    def __init__(self):
        pass

    def callback(
        self,
        kmodel: keras.models.Model,
        epoch: int = None,
        batch: int = None,
    ) -> None:
        kmodel.stop_training = True


class ModelCheckpoint2(Callback):
    """
    Subject for CheckpointObserver.
    """

    def __init__(
        self,
        total_epochs: int = np.Inf,
        patience: int = np.Inf,
        monitor: str = 'val_loss',
        mode: str = 'auto',
        period: int = 1,
    ):
        super(ModelCheckpoint2, self).__init__()
        self.monitor: str = monitor
        self.period: int = period
        self.epochs_since_last_save: int = 0
        self.patience = patience
        self.wait = 0
        self.total_epochs: int = total_epochs
        self._periodic: List[CheckpointObserver] = list()
        self._best: List[CheckpointObserver] = list()
        self._naninf: List[CheckpointObserver] = list()
        self._completion: List[CheckpointObserver] = list()

        if mode not in ['auto', 'min', 'max']:
            warnings.warn('ModelCheckpoint2 mode %s is unknown, fallback to auto mode.' % (mode), RuntimeWarning)
            mode = 'auto'

        if mode == 'min':
            self.monitor_op = np.less
            self.best = np.Inf
        elif mode == 'max':
            self.monitor_op = np.greater
            self.best = -np.Inf
        else:
            if 'acc' in self.monitor or self.monitor.startswith('fmeasure'):
                self.monitor_op = np.greater
                self.best = -np.Inf
            else:
                self.monitor_op = np.less
                self.best = np.Inf

    def on_epoch_end(self, epoch: int, logs: Dict = None):
        # Period check
        self.epochs_since_last_save += 1
        if self.epochs_since_last_save >= self.period:
            self.epochs_since_last_save = 0
            print('Epoch %05d: Periodic' % (epoch + 1))
            for observer in self._periodic:
                observer.callback(self.model, epoch=epoch)
        # Checks if last epoch improved the model.
        logs = logs or {}
        current = logs.get(self.monitor)
        if current is None:
            warnings.warn('Can save best model only with %s available, skipping.' % (self.monitor), RuntimeWarning)
        else:
            # Improved
            if self.monitor_op(current, self.best):
                print('Epoch %05d: %s improved from %0.5f to %0.5f' % (epoch + 1, self.monitor, self.best, current))
                self.best = current
                self.wait = 0
                for observer in self._best:
                    observer.callback(self.model, epoch=epoch)
            # No improvement
            else:
                print('Epoch %05d: %s did not improve from %0.5f' % (epoch + 1, self.monitor, self.best))
                self.wait += 1
                if self.wait >= self.patience:
                    self.model.stop_training = True
                    for observer in self._completion:
                        observer.callback(self.model, epoch=epoch)
        if epoch + 1 >= self.total_epochs:
            for observer in self._completion:
                observer.callback(self.model, epoch=epoch)
        print()

    def on_batch_end(self, batch: int, logs: Dict = None):
        logs = logs or {}
        loss = logs.get('loss')
        if loss is not None:
            if np.isnan(loss) or np.isinf(loss):
                for observer in self._naninf:
                    observer.callback(self.model, batch=batch)

    def on_period(self, obs: CheckpointObserver) -> None:
        self._periodic.append(obs)

    def on_improvement(self, obs: CheckpointObserver) -> None:
        self._best.append(obs)

    def on_nan_inf(self, obs: CheckpointObserver) -> None:
        self._naninf.append(obs)

    def on_completion(self, obs: CheckpointObserver) -> None:
        self._completion.append(obs)


class TerminateOnDemand(Callback):
    """
    Callback that terminates training when the die command is given.
    """

    _URL = 'out/terminate.txt'

    def on_epoch_end(self, epoch, logs=None) -> None:
        with open(self._URL, 'r') as f:
            a = f.read()
            if a == 'die':
                print("Manual early terminate command found in %s" % self._URL)
                self.stopped_epoch = epoch
                self.model.stop_training = True
                sys.exit()

    def clear(self) -> None:
        with open(self._URL, 'w') as f:
            f.write('')
