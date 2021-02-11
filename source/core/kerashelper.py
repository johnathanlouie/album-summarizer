from __future__ import annotations

import enum
import warnings
from typing import Any, Dict, List, Union

import dill
import keras
import numpy as np
from jl import Url, mkdirname, resize_img
from keras.backend import get_value
from keras.callbacks import Callback, EarlyStopping, ReduceLROnPlateau
from keras.utils import Sequence
from numpy import asarray, ceil, ndarray


class Sequence1(Sequence):
    """
    Generate batches of data.
    """

    def __init__(self, x_set: ndarray, y_set: ndarray, batch_size: int):
        self.x = x_set
        self.y = y_set
        self.batch_size = batch_size

    def __len__(self):
        a = float(len(self.x)) / float(self.batch_size)
        a = int(ceil(a))
        return a

    def __getitem__(self, idx):
        a = idx * self.batch_size
        b = (idx + 1) * self.batch_size
        batch_x = self.x[a:b]
        batch_y = self.y[a:b]
        xx = asarray([resize_img(filename) for filename in batch_x])
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

    def save(self) -> None:
        with open(self._url, 'w') as f:
            f.write(self.status.value)

    def is_complete(self) -> bool:
        return self.status == TrainingStatus.COMPLETE

    @classmethod
    def load(cls, url: Url) -> TrainingStatusData:
        with open(url) as f:
            self = cls(url)
            self.status = TrainingStatus(f.read())
            return self


class PickleAbstractClass(object):
    """
    """

    def __init__(self):
        raise NotImplementedError

    def get(self) -> Any:
        raise NotImplementedError

    def save(self, save_location: Url) -> None:
        mkdirname(save_location)
        dill.dump(self, open(save_location, 'wb'))

    @staticmethod
    def load(save_location: Url) -> PickleAbstractClass:
        return dill.load(open(save_location, 'rb'))


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


class EpochPickle(PickleAbstractClass):
    """
    """

    def __init__(self, current_epoch: int) -> None:
        self.current_epoch: int = current_epoch

    def get(self) -> int:
        return self.current_epoch


class CheckpointObserver(object):
    """
    Observer interface for ModelCheckpoint2.
    """

    def __init__(self):
        raise NotImplementedError

    def callback(
        self,
        kmodel: keras.models.Model,
        epoch: int = None,
        batch: int = None,
    ) -> None:
        raise NotImplementedError


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


class EarlyStoppingObserver(CheckpointObserver):
    """
    """

    def __init__(self, save_location: Url, es: EarlyStopping):
        self._url: Url = save_location
        self._es: ReduceLROnPlateau = es

    def callback(
        self,
        kmodel: keras.models.Model,
        epoch: int = None,
        batch: int = None,
    ) -> None:
        EarlyStoppingPickle(self._es).save(self._url)


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
        kmodel.save_weights(self._url, overwrite=True)


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
        mode: str = 'auto',
        period: int = 1,
    ):
        super(ModelCheckpoint2, self).__init__()
        self.monitor: str = 'val_loss'
        self.period: int = period
        self.epochs_since_last_save: int = 0
        self._total_epochs: int = 0
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
            print('\nEpoch %05d: saving model' % (epoch + 1))
            for observer in self._periodic:
                observer.callback(self.model, epoch=epoch)
        # Checks if last epoch improved the model.
        logs = logs or {}
        current = logs.get(self.monitor)
        if current is None:
            warnings.warn('Can save best model only with %s available, skipping.' % (self.monitor), RuntimeWarning)
        else:
            if self.monitor_op(current, self.best):
                print('\nEpoch %05d: %s improved from %0.5f to %0.5f, saving model' % (epoch + 1, self.monitor, self.best, current))
                self.best = current
                for observer in self._best:
                    observer.callback(self.model, epoch=epoch)
            else:
                print('\nEpoch %05d: %s did not improve from %0.5f' % (epoch + 1, self.monitor, self.best))
        if epoch + 1 >= self._total_epochs:
            for observer in self._completion:
                observer.callback(self.model, epoch=epoch)


    def on_batch_end(self, batch: int, logs: Dict = None):
        logs = logs or {}
        loss = logs.get('loss')
        if loss is not None:
            if np.isnan(loss) or np.isinf(loss):
                for observer in self._naninf:
                    observer.callback(self.model, batch=batch)

    def set_total_epochs(self, epochs: int) -> None:
        self._total_epochs = epochs

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
