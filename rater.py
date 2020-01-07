from keras.engine.input_layer import Input
from keras.layers import (BatchNormalization, Conv2D, Dense, Flatten,
                          MaxPooling2D)
from keras.models import Model

from jl import res2 as resolution
from model import ModelFactory


class Smi13(ModelFactory):
    """
    A deep learning model for predicting memorability.
    """

    name = 'smi13'
    version = 0

    def create(self) -> Model:
        """
        Returns a Keras Model object.
        """
        img_input = Input(resolution)

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
        x = Dense(1, activation='relu', name='predictions2')(x)
        model = Model(img_input, x, name='smi13')
        return model


class Smi13_1(ModelFactory):
    """
    A deep learning model for predicting memorability.
    """

    name = 'smi13'
    version = 1

    def create(self) -> Model:
        """
        Returns a Keras Model object.
        """
        img_input = Input(resolution)

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
        x = Dense(3, activation='softmax', name='predictions')(x)
        model = Model(img_input, x, name='smi13')
        return model
