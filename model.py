from keras import backend as K
import jl
import rater
import classifier

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
    'cosine_proximity',  # 13
    rmse  # 14
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


def rmse(y_true, y_pred):
    return K.sqrt(K.mean(K.square(y_pred - y_true), axis=-1))


def loadweights(a):
    for i in jl.layers:
        w = jl.npload(i)
        l = a.get_layer(i)
        l.set_weights(w)
        l.trainable = False
    return


def compile(model, filename, l, o, m):
    model.compile(loss=l, optimizer=o, metrics=m)
    model.save(filename)
    return model


def ccc():
    return compile(classifier.create(), loss[8], optimizer[0], metric[2], 'gen/ccc.h5')


def ccc2():
    return compile(classifier.create2(), loss[8], optimizer[0], metric[2], 'gen/ccc2.h5')


def ccc3():
    return compile(classifier.create3(), loss[8], optimizer[0], metric[2], 'gen/ccc3.h5')


def ccr():
    return compile(rater.create(), loss[14], optimizer[0], metric[0], 'gen/ccr.h5')


def lamem():
    return compile(rater.create(), loss[14], optimizer[0], metric[0], 'gen/lamem.h5')
