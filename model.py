from typing import Any, Callable, Dict, List, Tuple, Union

from keras import backend as K
from keras.models import Model
from keras.optimizers import SGD

import classifier
import jl
import rater

models = {
    'vgg16': classifier.create,
    'vgg16a': classifier.create2,
    'vgg16b': classifier.create3,
    'kcnn': rater.create
}


def rmse(y_true, y_pred):
    """
    Root mean square error loss function.
    """
    return K.sqrt(K.mean(K.square(y_pred - y_true), axis=-1))


custom_rmse = {'rmse': rmse}


def loadweights(a):
    for i in jl.layers:
        w = jl.npload(i)
        l = a.get_layer(i)
        l.set_weights(w)
        l.trainable = False
    return


def ccc():
    return compile('vgg16', 'ccc', loss[8], optimizer[0], metric[2])


def ccc2():
    return compile('vgg16a', 'ccc', loss[8], optimizer[0], metric[2])


def ccc3():
    return compile('vgg16b', 'ccc', loss[8], optimizer[0], metric[2])


def ccr():
    return compile('kcnn', 'ccr', rmse, SGD(lr=0.01, momentum=0.9, decay=0.0005, nesterov=True), metric[0])


def lamem():
    return compile('kcnn', 'lamem', rmse, optimizer[0], metric[0])


class ModelFactory(object):
    """
    Abstract factory class for keras.models.Model.
    """

    name = ''
    version = -1

    def create(self) -> Model:
        """
        Abstract method for ModelFactory.
        """
        raise NotImplementedError


class CompileOption(object):
    """
    Options for the Architecture class.
    """

    def __init__(self, name: str, value: Union[Callable, str]) -> None:
        self.name = name
        self.value = value


LOSS = [
    CompileOption('mse', 'mean_squared_error'),  # 0
    CompileOption('mae', 'mean_absolute_error'),  # 1
    CompileOption('mape', 'mean_absolute_percentage_error'),  # 2
    CompileOption('msle', 'mean_squared_logarithmic_error'),  # 3
    CompileOption('sh', 'squared_hinge'),  # 4
    CompileOption('h', 'hinge'),  # 5
    CompileOption('ch', 'categorical_hinge'),  # 6
    CompileOption('lch', 'logcosh'),  # 7
    CompileOption('cce', 'categorical_crossentropy'),  # 8
    CompileOption('scce', 'sparse_categorical_crossentropy'),  # 9
    CompileOption('bce', 'binary_crossentropy'),  # 10
    CompileOption('kld', 'kullback_leibler_divergence'),  # 11
    CompileOption('p', 'poisson'),  # 12
    CompileOption('cp', 'cosine_proximity'),  # 13
    CompileOption('rmse', rmse)  # 14
]

OPTIMIZER = [
    CompileOption('sgd', 'sgd'),  # 0
    CompileOption('rmsp', 'RMSprop'),  # 1
    CompileOption('ag', 'Adagrad'),  # 2
    CompileOption('ad', 'Adadelta'),  # 3
    CompileOption('ame', 'Adam'),  # 4
    CompileOption('am', 'Adamax'),  # 5
    CompileOption('na', 'Nadam')  # 6
]

METRIC = [
    CompileOption('a', 'accuracy'),  # 0
    CompileOption('ba', 'binary_accuracy'),  # 1
    CompileOption('ca', 'categorical_accuracy'),  # 2
    CompileOption('sca', 'sparse_categorical_accuracy'),  # 3
    CompileOption('tkca', 'top_k_categorical_accuracy'),  # 4
    CompileOption('stkca', 'sparse_top_k_categorical_accuracy')  # 5
]


class Architecture(object):
    """
    Creates a compiled keras.models.Model object with options and creates the argument for the custom_objects parameter for the keras.models.load_model function.
    """

    def __init__(self, model: ModelFactory, loss: CompileOption, optimizer: CompileOption, metric: CompileOption) -> None:
        self._model = model
        self._loss = loss
        self._optimizer = optimizer
        self._metric = metric

    def compile(self) -> Model:
        """
        Creates a compiled keras.models.Model object.
        """
        # if type(m) != list or type(m) != dict:
        #     m = [m]
        model = self._model.create()
        model.compile(loss=self._loss.value, optimizer=self._optimizer.value, metrics=[self._metric.value])
        return model

    def custom(self) -> Dict[str, Callable]:
        """
        Creates the argument for the custom_objects parameter for the keras.models.load_model function.
        """
        d = dict()
        if type(self._loss.value) != str:
            d['self._loss.value'] = self._loss.value
        if type(self._optimizer.value) != str:
            d['self._optimizer.value'] = self._optimizer.value
        if type(self._metric.value) != str:
            d['self._metric.value'] = self._metric.value
        return d

    def name(self) -> str:
        """
        Returns a unique identifier for the combination of model and compile options.
        """
        return "%s.%s.%s.%s" % (self._model.name, self._loss.name, self._optimizer.name, self._metric.name)
