from warnings import warn

from keras.backend import get_value
from keras.callbacks import Callback, ModelCheckpoint, ReduceLROnPlateau
from keras.utils import Sequence
from numpy import asarray, ceil

from dataholder import DataHolder
from jl import Url, resize_img


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
    It saves the training state whenever ModelCheckpoint saves the training model.
    """

    def __init__(self, mcp: ModelCheckpoint, mcpb: ModelCheckpoint, lr: ReduceLROnPlateau, url: Url, total_epoch: int) -> None:
        super(PickleCheckpoint, self).__init__()
        self._mcp = mcp
        self._copy_mcp(mcp)
        self._mcpb = mcpb
        self._lr = lr
        self._total_epoch = total_epoch
        self._url = url
        return

    def on_epoch_end(self, epoch, logs=None) -> None:
        logs = logs or {}
        self.epochs_since_last_save += 1
        current_epoch = epoch + 1
        if self.epochs_since_last_save >= self.period:
            self.epochs_since_last_save = 0
            # filepath = self.filepath.format(epoch=epoch + 1, **logs)
            if self.save_best_only:
                current = logs.get(self.monitor)
                if current is None:
                    warn('Can save best Keras callback objects only with %s available, skipping.' % (self.monitor), RuntimeWarning)
                else:
                    if self.monitor_op(current, self.best):
                        if self.verbose > 0:
                            print('\nEpoch %05d: %s improved from %0.5f to %0.5f, saving training state to %s' % (epoch + 1, self.monitor, self.best, current, self._url))
                        self.best = current
                        dh = DataHolder(self._url, current_epoch, self._total_epoch, self._lr, self._mcp, self._mcpb)
                        if self.save_weights_only:
                            dh.save()
                        else:
                            dh.save()
                    else:
                        if self.verbose > 0:
                            print('\nEpoch %05d: %s did not improve from %0.5f' % (epoch + 1, self.monitor, self.best))
            else:
                if self.verbose > 0:
                    print('\nEpoch %05d: saving training state to %s' % (epoch + 1, self._url))
                dh = DataHolder(self._url, current_epoch, self._total_epoch, self._lr, self._mcp, self._mcpb)
                if self.save_weights_only:
                    dh.save()
                else:
                    dh.save()
        return

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
