from rasek.architecture import CompileOption
from rasek.modelbuilder import ModelBuilder
from keras import backend as K


def rmse(y_true, y_pred):
    """
    Root mean square error loss function.
    """
    return K.sqrt(K.mean(K.square(y_pred - y_true), axis=-1))


ModelBuilder.loss(CompileOption('rmse', rmse))
