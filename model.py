from keras import backend as K
import jl
import rater
import classifier
from keras.optimizers import SGD

loss = [
    'mean_squared_error',  # 0
    'mean_absolute_error',  # 1
    'mean_absolute_percentage_error',  # 2
    'mean_squared_logarithmic_error',  # 3
    'squared_hinge',  # 4
    'hinge',  # 5
    'categorical_hinge',  # 6
    'logcosh',  # 7
    'categorical_crossentropy',  # 8
    'sparse_categorical_crossentropy',  # 9
    'binary_crossentropy',  # 10
    'kullback_leibler_divergence',  # 11
    'poisson',  # 12
    'cosine_proximity'  # 13
]


optimizer = [
    'sgd',  # 0
    'RMSprop',  # 1
    'Adagrad',  # 2
    'Adadelta',  # 3
    'Adam',  # 4
    'Adamax',  # 5
    'Nadam'  # 6
]

metric = [
    'accuracy',  # 0
    'binary_accuracy',  # 1
    'categorical_accuracy',  # 2
    'sparse_categorical_accuracy',  # 3
    'top_k_categorical_accuracy',  # 4
    'sparse_top_k_categorical_accuracy'  # 5
]

models = {
    'vgg16': classifier.create,
    'vgg16a': classifier.create2,
    'vgg16b': classifier.create3,
    'kcnn': rater.create
}


def rmse(y_true, y_pred):
    return K.sqrt(K.mean(K.square(y_pred - y_true), axis=-1))


custom_rmse = {'rmse': rmse}


def loadweights(a):
    for i in jl.layers:
        w = jl.npload(i)
        l = a.get_layer(i)
        l.set_weights(w)
        l.trainable = False
    return


def compile(model, dataset, l, o, m):
    if type(m) != list or type(m) != dict:
        m = [m]
    modelx = models[model]()
    modelx.compile(loss=l, optimizer=o, metrics=m)
    return modelx


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
