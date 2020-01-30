from keras.applications.vgg16 import VGG16
from keras.engine.input_layer import Input
from keras.layers import Conv2D, Dense, Flatten, MaxPooling2D
from keras.models import Model

from core.model import ModelFactory
from jl import res2 as resolution


class Vgg16A(ModelFactory):
    """
    Fully manual configuration of VGG16.
    """

    name = 'vgg16'
    version = 'a'

    def create(self) -> Model:
        """
        Creates a keras.models.Model object.
        """
        img_input = Input(resolution)
        # Block 1
        x = Conv2D(64, (3, 3), activation='relu', padding='same', name='block1_conv1')(img_input)
        x = Conv2D(64, (3, 3), activation='relu', padding='same', name='block1_conv2')(x)
        x = MaxPooling2D((2, 2), strides=(2, 2), name='block1_pool')(x)

        # Block 2
        x = Conv2D(128, (3, 3), activation='relu', padding='same', name='block2_conv1')(x)
        x = Conv2D(128, (3, 3), activation='relu', padding='same', name='block2_conv2')(x)
        x = MaxPooling2D((2, 2), strides=(2, 2), name='block2_pool')(x)

        # Block 3
        x = Conv2D(256, (3, 3), activation='relu', padding='same', name='block3_conv1')(x)
        x = Conv2D(256, (3, 3), activation='relu', padding='same', name='block3_conv2')(x)
        x = Conv2D(256, (3, 3), activation='relu', padding='same', name='block3_conv3')(x)
        x = MaxPooling2D((2, 2), strides=(2, 2), name='block3_pool')(x)

        # Block 4
        x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block4_conv1')(x)
        x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block4_conv2')(x)
        x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block4_conv3')(x)
        x = MaxPooling2D((2, 2), strides=(2, 2), name='block4_pool')(x)

        # Block 5
        x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block5_conv1')(x)
        x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block5_conv2')(x)
        x = Conv2D(512, (3, 3), activation='relu', padding='same', name='block5_conv3')(x)
        x = MaxPooling2D((2, 2), strides=(2, 2), name='block5_pool')(x)

        # Classification block
        x = Flatten(name='flatten')(x)
        x = Dense(4096, activation='relu', name='fc1')(x)
        x = Dense(4096, activation='relu', name='fc2')(x)
        x = Dense(6, activation='softmax', name='predictions')(x)
        model = Model(img_input, x, name='vgg16')
        return model


class Vgg16B(ModelFactory):
    """
    The convolution blocks of VGG16 are constructed by Keras.
    The classification block is manually configured.
    """

    name = 'vgg16'
    version = 'b'

    def create(self) -> Model:
        """
        Creates a keras.models.Model object.
        """
        base = VGG16(include_top=False, input_shape=resolution)
        x = Flatten(name='flatten')(base.output)
        x = Dense(4096, activation='relu', name='fc1')(x)
        x = Dense(4096, activation='relu', name='fc2')(x)
        x = Dense(6, activation='softmax', name='predictions')(x)
        model = Model(base.input, x, name='vgg16')
        return model


class Vgg16C(ModelFactory):
    """
    VGG16 by Keras.
    """

    name = 'vgg16'
    version = 'c'

    def create(self) -> Model:
        """
        Creates a keras.models.Model object.
        """
        return VGG16(weights=None, input_tensor=Input(resolution), classes=6)
