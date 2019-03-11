import keras
import cv2
import numpy as np
from keras.engine.input_layer import Input
from keras import models
from keras.layers import BatchNormalization, Conv2D, Dense, Flatten, MaxPooling2D
from keras import backend as K
import jl


def createmodel():
    img_input = Input(jl.res2)

    # Block 1
    x = Conv2D(
        filters=96,
        kernel_size=(11, 11),
        strides=4,
        activation='relu',
        padding='same',
        name='block1_conv1'
    )(img_input)
    x = BatchNormalization()(x)
    x = MaxPooling2D(
        (3, 3),
        strides=(2, 2),
        name='block1_pool'
    )(x)

    # Block 2
    x = Conv2D(
        filters=256,
        kernel_size=(5, 5),
        # strides=4,
        activation='relu',
        padding='same',
        name='block2_conv1'
    )(x)
    x = BatchNormalization()(x)
    x = MaxPooling2D(
        (3, 3),
        strides=(2, 2),
        name='block2_pool'
    )(x)

    # Block 3
    x = Conv2D(
        filters=384,
        kernel_size=(3, 3),
        # strides=4,
        activation='relu',
        padding='same',
        name='block3_conv1'
    )(x)

    # Block 4
    x = Conv2D(
        filters=384,
        kernel_size=(3, 3),
        # strides=4,
        activation='relu',
        padding='same',
        name='block4_conv1'
    )(x)

    # Block 5
    x = Conv2D(
        filters=256,
        kernel_size=(3, 3),
        # strides=4,
        activation='relu',
        padding='same',
        name='block5_conv1'
    )(x)
    x = MaxPooling2D(
        (3, 3),
        strides=(2, 2),
        name='block5_pool'
    )(x)

    # Classification block
    x = Flatten(name='flatten')(x)
    x = Dense(4096, activation='relu', name='fc1')(x)
    x = Dense(4096, activation='relu', name='fc2')(x)
    x = Dense(1000, activation='softmax', name='predictions')(x)
    # x = Dense(6, activation='softmax', name='predictions2')(x)
    x = Dense(1, activation='relu', name='predictions3')(x)
    model = models.Model(img_input, x, name='vgg16')
    return model


def loadweights(a):
    for i in jl.layers:
        w = jl.npload(i)
        l = a.get_layer(i)
        l.set_weights(w)
        l.trainable = False
    return


def compile2(l, o, m, name):
    model = createmodel()
    # loadweights(model)
    model.compile(loss=l, optimizer=o, metrics=[m])
    model.save(name)
    return


def rmse(y_true, y_pred):
    return K.sqrt(K.mean(K.square(y_pred - y_true), axis=-1))


def main():
    # loss
    loss = [
        'mean_squared_error',
        'mean_absolute_error',
        'mean_absolute_percentage_error',
        'mean_squared_logarithmic_error',
        'squared_hinge',
        'hinge',
        'categorical_hinge',
        'logcosh',
        'categorical_crossentropy',
        'sparse_categorical_crossentropy',
        'binary_crossentropy',
        'kullback_leibler_divergence',
        'poisson',
        'cosine_proximity'
    ]

    # optimizers
    sgd = 'sgd'
    rmsp = 'RMSprop'
    ag = 'Adagrad'
    ad = 'Adadelta'
    am = 'Adam'
    amax = 'Adamax'
    na = 'Nadam'

    # metrics
    acc = 'accuracy'

    compile2(rmse, sgd, acc, jl.H5_RATER)
    return


# main()
