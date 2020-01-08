from warnings import warn

from keras.backend import get_value
from keras.callbacks import Callback, ModelCheckpoint, ReduceLROnPlateau
from keras.utils import Sequence
from numpy import asarray, ceil

from dataholder import DataHolder
from jl import resize_img


class Sequence1(Sequence):
    """
    Generate batches of data.
    """

    def __init__(self, x_set, y_set, batch_size):
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

    def __init__(self, mcp: ModelCheckpoint, mcpb: ModelCheckpoint, lr: ReduceLROnPlateau, archisplit: str, total_epoch: int = 2**64) -> None:
        super(PickleCheckpoint, self).__init__()
        self._mcp = mcp
        self._copy_mcp(mcp)
        self._mcpb = mcpb
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
                    warn('Can save best Keras callback objects only with %s available, skipping.' % (self.monitor), RuntimeWarning)
                else:
                    if self.monitor_op(current, self.best):
                        if self.verbose > 0:
                            print('\nEpoch %05d: %s improved from %0.5f to %0.5f, saving Keras callback objects to %s' % (epoch + 1, self.monitor, self.best, current, filepath))
                        self.best = current
                        dh = DataHolder(url, current_epoch, self._total_epoch, self._lr, self._mcp, self._mcpb)
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
                dh = DataHolder(url, current_epoch, self._total_epoch, self._lr, self._mcp, self._mcpb)
                if self.save_weights_only:
                    dh.save()
                else:
                    dh.save()

    def _copy_mcp(self, mcp: ModelCheckpoint) -> None:
        """
        Copies a ModelCheckpoint instance.
        """
        try:
            self.best = mcp.best
        except AttributeError:
            pass
        try:
            self.epochs_since_last_save = mcp.epochs_since_last_save
        except AttributeError:
            pass
        try:
            self.filepath = mcp.filepath
        except AttributeError:
            pass
        try:
            self.monitor = mcp.monitor
        except AttributeError:
            pass
        try:
            self.period = mcp.period
        except AttributeError:
            pass
        try:
            self.save_best_only = mcp.save_best_only
        except AttributeError:
            pass
        try:
            self.save_weights_only = mcp.save_weights_only
        except AttributeError:
            pass
        try:
            self.verbose = mcp.verbose
        except AttributeError:
            pass
        try:
            self.monitor_op = mcp.monitor_op
        except AttributeError:
            pass
        return


class TerminateOnDemand(Callback):
    """
    Callback that terminates training when a NaN loss is encountered.
    """

    def on_epoch_begin(self, epoch, logs) -> None:
        lr = get_value(self.model.optimizer.lr)
        print('Learning rate: %f' % (lr))

    def on_epoch_end(self, epoch, logs=None) -> None:
        with open('gen/terminate.txt', 'r') as f:
            a = f.read()
            if a == 'die':
                print('Manual early terminate command found in gen/terminate.txt')
                self.stopped_epoch = epoch
                self.model.stop_training = True
