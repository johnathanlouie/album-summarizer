
import warnings
import dill
import cv2 as cv
import numpy as np
import jl
from keras.models import load_model
import keras
from keras.callbacks import CSVLogger, ModelCheckpoint, Callback, ReduceLROnPlateau
import model
import os
from typing import Any, Dict, List, Tuple
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class DataSetName:

    def __init__(self, name: str, split: int, phase: str, xy: str) -> None:
        self.name = name
        self.split = split
        self.phase = phase
        self.xy = xy
        return

    def __str__(self) -> str:
        return '%s.%d.%s.%s' % (self.name, self.split, self.phase, self.xy)

    def __add__(self, other) -> str:
        return str(self) + other

    def __radd__(self, other) -> str:
        return other + str(self)

    def save(self, data: Any) -> None:
        jl.npsave(self, data)
        return

    def load(self) -> np.ndarray:
        return jl.npload(self)


class DataSetNameFactory:
    TRAIN = 'train'
    VALIDATION = 'val'
    TEST = 'test'
    X = 'x'
    Y = 'y'

    def __init__(self, name: str, split: int):
        self.name = name
        self.split = split

    def xtrain(self) -> DataSetName:
        return self.x(self.TRAIN)

    def xval(self) -> DataSetName:
        return self.x(self.VALIDATION)

    def xtest(self) -> DataSetName:
        return self.x(self.TEST)

    def ytrain(self) -> DataSetName:
        return self.y(self.TRAIN)

    def yval(self) -> DataSetName:
        return self.y(self.VALIDATION)

    def ytest(self) -> DataSetName:
        return self.y(self.TEST)

    def x(self, phase: str) -> DataSetName:
        return DataSetName(self.name, self.split, phase, self.X)

    def y(self, phase: str) -> DataSetName:
        return DataSetName(self.name, self.split, phase, self.Y)


class Ccc:
    name = 'ccc'

    @classmethod
    def prep(cls) -> None:
        print("Reading data file")
        x = jl.getcol(0)
        y = jl.getcol(2)
        y = jl.class_str_int(y)
        print('Generating data splits')
        tx, ty, vx, vy, ex, ey = jl.train_valid_test_split(x, y, test_size=0.1, valid_size=0.1)
        print('Converting to one hot')
        ty = keras.utils.to_categorical(ty, num_classes=6, dtype='int32')
        vy = keras.utils.to_categorical(vy, num_classes=6, dtype='int32')
        ey = keras.utils.to_categorical(ey, num_classes=6, dtype='int32')
        print('Saving')
        ds = DataSetNameFactory(cls.name, 1)
        ds.xtrain().save(tx)
        ds.xtrain().save(vx)
        ds.xtrain().save(ex)
        ds.ytrain().save(ty)
        ds.ytrain().save(vy)
        ds.ytrain().save(ey)
        print('Prep complete')
        return


class Ccr:
    name = 'ccr'

    @classmethod
    def prep(cls) -> None:
        print("Reading data file")
        x = jl.getcol(0)
        y = jl.getcol(1)
        y = jl.intize(y)
        print('Generating data splits')
        tx, ty, vx, vy, ex, ey = jl.train_valid_test_split(x, y, test_size=0.1, valid_size=0.1)
        print('Saving')
        ds = DataSetNameFactory(cls.name, 1)
        ds.xtrain().save(tx)
        ds.xtrain().save(vx)
        ds.xtrain().save(ex)
        ds.ytrain().save(ty)
        ds.ytrain().save(vy)
        ds.ytrain().save(ey)
        print('Prep complete')
        return


def resize_imgs(src_list, dst_list) -> None:
    urls1 = jl.readtxt(src_list)
    urls2 = jl.readtxt(dst_list)
    resize_imgs2(urls1, urls2)
    return


def resize_imgs2(src_list, dst_list) -> None:
    for src, dst in zip(src_list, dst_list):
        print(src)
        print(dst)
        img2 = jl.resize_img(src)
        jl.mkdirs(dst)
        cv.imwrite(dst, img2)
    print('done')
    return


class Lamem:
    """Dataset used for large scale image memorability."""

    name = 'lamem'
    splits = range(1, 6)
    phases = [
        ('train', DataSetNameFactory.TRAIN),
        ('val', DataSetNameFactory.VALIDATION),
        ('test', DataSetNameFactory.TEST)
    ]

    @staticmethod
    def read(phase, split):
        filename = 'lamem/splits/%s_%d.txt' % (phase, split)
        b = np.asarray([line.split(' ') for line in jl.readtxt(filename)])
        x = np.asarray(b[:, 0])
        y = np.asarray([float(x) for x in b[:, 1]])
        return x, y

    @staticmethod
    def rel_url(url):
        a = os.path.join(os.getcwd(), 'lamem/images', url)
        return os.path.normpath(a)

    @classmethod
    def prep_txt(cls, phase, split) -> None:
        x, y = cls.read(phase[0], split)
        x = np.asarray([cls.rel_url(url) for url in x])
        y = np.asarray(y)
        ds = DataSetNameFactory(cls.name, split)
        ds.x(phase[1]).save(x)
        ds.y(phase[1]).save(y)
        return

    @classmethod
    def prep(cls) -> None:
        for j in cls.phases:
            for i in cls.splits:
                cls.prep_txt(j, i)
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
        xx = np.asarray([jl.resize_img(filename) for filename in batch_x])
        yy = np.asarray(batch_y)
        return xx, yy


class DataHolder:
    """Holds the picklable state of training and callbacks."""

    def get_mcp(self):
        mcp = ModelCheckpoint('')
        DataHolder.copy_ModelCheckpoint(self.mcp, mcp)
        return mcp

    def get_lr(self):
        lr = ReduceLROnPlateau()
        DataHolder.copy_ReduceLROnPlateau(self.lr, lr)
        return lr

    @staticmethod
    def load(filepath):
        return dill.load(open(filepath, 'rb'))

    def save(self, filepath) -> None:
        dill.dump(self, open(filepath, "wb"))
        return

    @staticmethod
    def as_data(epoch, mcp, lr):
        dh = DataHolder()
        dh.mcp = DataHolder()
        dh.lr = DataHolder()
        DataHolder.copy_ModelCheckpoint(mcp, dh.mcp)
        DataHolder.copy_ReduceLROnPlateau(lr, dh.lr)
        dh.epoch = epoch
        return dh

    @staticmethod
    def copy_ModelCheckpoint(src, dst) -> None:
        dst.best = src.best
        dst.epochs_since_last_save = src.epochs_since_last_save
        dst.filepath = src.filepath
        dst.monitor = src.monitor
        dst.period = src.period
        dst.save_best_only = src.save_best_only
        dst.save_weights_only = src.save_weights_only
        dst.verbose = src.verbose
        return

    @staticmethod
    def copy_ReduceLROnPlateau(src, dst) -> None:
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


class PickleCheckpoint(Callback):
    """Save the model after every epoch.
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

    def __init__(self, filepath, mcp, lr, epoch=0, monitor='val_loss', verbose=1,
                 save_best_only=True, save_weights_only=False,
                 mode='auto', period=1):
        super(PickleCheckpoint, self).__init__()
        self.monitor = monitor
        self.verbose = verbose
        self.filepath = filepath
        self.save_best_only = save_best_only
        self.save_weights_only = save_weights_only
        self.period = period
        self.epochs_since_last_save = 0
        self.mcp = mcp
        self.lr = lr
        self.epoch = epoch

        if mode not in ['auto', 'min', 'max']:
            warnings.warn('PickleCheckpoint mode %s is unknown, fallback to auto mode.' % (mode), RuntimeWarning)
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

    def on_epoch_end(self, epoch, logs=None) -> None:
        logs = logs or {}
        self.epochs_since_last_save += 1
        self.epoch = epoch + 1
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
                        if self.save_weights_only:
                            DataHolder.as_data(epoch+1, self.mcp, self.lr).save(filepath)
                        else:
                            DataHolder.as_data(epoch+1, self.mcp, self.lr).save(filepath)
                    else:
                        if self.verbose > 0:
                            print('\nEpoch %05d: %s did not improve from %0.5f' % (epoch + 1, self.monitor, self.best))
            else:
                if self.verbose > 0:
                    print('\nEpoch %05d: saving Keras callback objects to %s' % (epoch + 1, filepath))
                if self.save_weights_only:
                    DataHolder.as_data(epoch+1, self.mcp, self.lr).save(filepath)
                else:
                    DataHolder.as_data(epoch+1, self.mcp, self.lr).save(filepath)


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
        self.model = model
        self.ds = dataset
        return

    def picklename(self):
        return 'gen/%s.%s.p' % (self.model, self.ds)

    def modelname(self):
        return 'gen/%s.%s.h5' % (self.model, self.ds)

    def trainingname(self):
        return 'gen/%s.%s.train.h5' % (self.model, self.ds)


class DataModel:
    def __init__(self, datamodelname):
        self.dmn = datamodelname
        return

    def setmodel(self, model) -> None:
        self.model = model
        return

    def loadmodel(self, custom) -> None:
        mfn = self.dmn.modelname()
        self.model = load_model(mfn, custom_objects=custom)
        return

    def loadpicklecheckpoint(self):
        modelfilepath = self.dmn.modelname()
        mcp = ModelCheckpoint(modelfilepath, verbose=1, save_best_only=True)
        lr = ReduceLROnPlateau(patience=5, verbose=1)
        pickle_name = self.dmn.picklename()
        pcp = PickleCheckpoint(pickle_name, mcp, lr)
        if os.path.exists(pickle_name):
            dh = DataHolder.load(pickle_name)
            mcp = dh.get_mcp()
            lr = dh.get_lr()
            pcp = PickleCheckpoint(pickle_name, mcp, lr, dh.epoch)
            DataHolder.copy_ModelCheckpoint(mcp, pcp)
        return pcp

    def train(self, initial_epoch=0, epochs=10000) -> None:
        print('Loading training X')
        x1 = self.dmn.ds.xtrain().load()
        print('Loading training Y')
        y1 = self.dmn.ds.ytrain().load()
        print('Loading validation X')
        x2 = self.dmn.ds.xval().load()
        print('Loading validation Y')
        y2 = self.dmn.ds.yval().load()
        # train_name = model.filename_training(modelname, dataset)
        print('Training sequence')
        seq1 = Sequence1(x1, y1, 10)
        print('Validation sequence')
        seq2 = Sequence1(x2, y2, 10)
        print('Training starts')
        term = TerminateOnDemand()
        # save = ModelCheckpoint(train_name, verbose=1, period=2)
        csv = CSVLogger('gen/training.csv', append=True)
        sbcp = self.loadpicklecheckpoint()
        best = sbcp.mcp
        lr = sbcp.lr
        self.model.fit_generator(
            generator=seq1,
            epochs=epochs,
            verbose=1,
            validation_data=seq2,
            shuffle=False,
            initial_epoch=sbcp.epoch,
            callbacks=[
                lr,
                best,
                # save,
                csv,
                term,
                sbcp
            ]
        )
        print('Training finished')
        return

    def test(self) -> None:
        print('Loading test X')
        x = self.dmn.ds.xtest().load()
        print('Loading test Y')
        y = self.dmn.ds.ytest().load()
        print('Testing sequence')
        seq = Sequence1(x, y, 10)
        print('Testing starts')
        results = self.model.evaluate_generator(generator=seq, verbose=1)
        print('Testing finished')
        if type(results) != list:
            results = [results]
        for metric, scalar in zip(self.model.metrics_names, results):
            print('%s: %f' % (metric, scalar))
        return

    def predict(self):
        print('Loading test X')
        x = self.dmn.ds.xtest().load()
        print('Loading test Y')
        y = self.dmn.ds.ytest().load()
        print('Prediction sequence')
        seq = Sequence1(x, y, 10)
        print('Prediction starts')
        results = self.model.predict_generator(generator=seq, verbose=1)
        print('Prediction finished')
        if len(results.shape) == 2:
            if results.shape[1] == 1:
                results = results.flatten()
            else:
                results = results.argmax(1)
                results = jl.class_str_int(results)
        results_file = 'gen/pred.txt'
        jl.writetxt(results_file, results)
        print('Saved predictions to %s' % (results_file))
        return results


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
