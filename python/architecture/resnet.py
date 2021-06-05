from typing import Optional

from core import modelbuilder
from core.architecture import Architecture
from core.jl import Resolution
from core.modeltype import OutputType
from keras.applications.resnet import ResNet101
from keras.engine.input_layer import Input
from keras.layers import (BatchNormalization, Conv2D, Dense, Flatten,
                          MaxPooling2D)
from keras.models import Model


class Resnet101(Architecture):
    """
    Untrained VGG16 for classification.
    """

    NAME = 'resnet101'
    OUTPUT_TYPE: OutputType = OutputType.ONE_HOT

    def create(self, res: Resolution, classes: Optional[int]) -> Model:
        """
        Creates a keras.models.Model object.
        """
        if type(classes) is not int:
            raise ValueError(classes)
        return ResNet101(
            include_top=True,
            weights=None,
            input_tensor=Input(res.hwc()),
            classes=classes,
        )


class Resnet101a(Architecture):
    """
    Untrained VGG16 for classification.
    """

    NAME = 'resnet101a'
    OUTPUT_TYPE: OutputType = OutputType.SCALAR

    def create(self, res: Resolution, classes: Optional[int]) -> Model:
        """
        Creates a keras.models.Model object.
        """
        img_input = Input(res.hwc())
        x = ResNet101(
            include_top=True,
            weights=None,
            input_tensor=img_input,
        )
        x = Dense(1, activation='relu', name='predictions')(x.output)
        model = Model(img_input, x, name='resnet101a')
        return model


modelbuilder.ModelBuilder.architecture(Resnet101())
modelbuilder.ModelBuilder.architecture(Resnet101a())
