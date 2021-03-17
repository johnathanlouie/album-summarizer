from core import modelbuilder
from core.architecture import Architecture
from jl import Resolution
from keras.applications.vgg16 import VGG16
from keras.engine.input_layer import Input
from keras.layers import Conv2D, Dense, Flatten, MaxPooling2D
from keras.models import Model


class Vgg16(Architecture):
    """
    Untrained VGG16 for classification.
    """

    NAME = 'vgg16'
    OUTPUT_NUM: int = 6

    def create(self, res: Resolution) -> Model:
        """
        Creates a keras.models.Model object.
        """
        return VGG16(
            include_top=True,
            weights=None,
            input_tensor=Input(res.hwc()),
            classes=6,
        )


class Vgg16B(Architecture):
    """
    Fully manual configuration of VGG16.
    """

    NAME = 'vgg16b'
    OUTPUT_NUM: int = 6

    LAYERS = [
        'block1_conv1',
        'block1_conv2',
        'block2_conv1',
        'block2_conv2',
        'block3_conv1',
        'block3_conv2',
        'block3_conv3',
        'block4_conv1',
        'block4_conv2',
        'block4_conv3',
        'block5_conv1',
        'block5_conv2',
        'block5_conv3'
    ]

    def create(self, res: Resolution) -> Model:
        """
        Creates a keras.models.Model object.
        """
        img_input = Input(res.hwc())
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


class Vgg16Pt(Architecture):
    """
    Pretrained VGG16 with frozen convolution blocks for classifcation.
    """

    NAME = 'vgg16pt'
    OUTPUT_NUM: int = 6

    def create(self, res: Resolution) -> Model:
        """
        Creates a keras.models.Model object.
        """
        base = VGG16(
            include_top=False,
            weights='imagenet',
            input_shape=res.hwc(),
        )
        base.trainable = False
        x = Flatten(name='flatten')(base.output)
        x = Dense(4096, activation='relu', name='fc1')(x)
        x = Dense(4096, activation='relu', name='fc2')(x)
        x = Dense(6, activation='softmax', name='predictions')(x)
        model = Model(base.input, x, name='vgg16pt')
        return model


modelbuilder.ModelBuilder.architecture(Vgg16())
modelbuilder.ModelBuilder.architecture(Vgg16B())
modelbuilder.ModelBuilder.architecture(Vgg16Pt())
