import keras
import cv2
import numpy as np
from keras import layers
from keras.engine.input_layer import Input
from keras.applications.vgg16 import VGG16
from keras import models
import jl
import pprint


def createmodel():
    img_input = Input(jl.res2)
    # Block 1
    x = layers.Conv2D(64, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block1_conv1')(img_input)
    x = layers.Conv2D(64, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block1_conv2')(x)
    x = layers.MaxPooling2D((2, 2), strides=(2, 2), name='block1_pool')(x)

    # Block 2
    x = layers.Conv2D(128, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block2_conv1')(x)
    x = layers.Conv2D(128, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block2_conv2')(x)
    x = layers.MaxPooling2D((2, 2), strides=(2, 2), name='block2_pool')(x)

    # Block 3
    x = layers.Conv2D(256, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block3_conv1')(x)
    x = layers.Conv2D(256, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block3_conv2')(x)
    x = layers.Conv2D(256, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block3_conv3')(x)
    x = layers.MaxPooling2D((2, 2), strides=(2, 2), name='block3_pool')(x)

    # Block 4
    x = layers.Conv2D(512, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block4_conv1')(x)
    x = layers.Conv2D(512, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block4_conv2')(x)
    x = layers.Conv2D(512, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block4_conv3')(x)
    x = layers.MaxPooling2D((2, 2), strides=(2, 2), name='block4_pool')(x)

    # Block 5
    x = layers.Conv2D(512, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block5_conv1')(x)
    x = layers.Conv2D(512, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block5_conv2')(x)
    x = layers.Conv2D(512, (3, 3),
                      activation='relu',
                      padding='same',
                      name='block5_conv3')(x)
    x = layers.MaxPooling2D((2, 2), strides=(2, 2), name='block5_pool')(x)

    # Classification block
    x = layers.Flatten(name='flatten')(x)
    x = layers.Dense(4096, activation='relu', name='fc1')(x)
    x = layers.Dense(4096, activation='relu', name='fc2')(x)
    x = layers.Dense(6, activation='softmax', name='predictions')(x)
    # x = layers.Dense(1, activation='relu', name='predictions2')(x)
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
    model = createmodel2()
    # loadweights(model)
    model.compile(loss=l, optimizer=o, metrics=[m])
    model.save(name)
    return


def main():
    cc = 'categorical_crossentropy'
    mae = 'mean_absolute_error'
    sgd = 'sgd'
    acc = 'accuracy'
    compile2(cc, sgd, acc, jl.H5_CLASSIFIER)
    return


def createmodel2():
    base = VGG16(include_top=False, input_shape=jl.res2)
    x = layers.Flatten(name='flatten')(base.output)
    x = layers.Dense(4096, activation='relu', name='fc1')(x)
    x = layers.Dense(4096, activation='relu', name='fc2')(x)
    x = layers.Dense(6, activation='softmax', name='predictions')(x)
    model = models.Model(base.input, x, name='vgg16')
    return model


# main2()
