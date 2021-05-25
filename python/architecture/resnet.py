from typing import Optional

from core import modelbuilder
from core.architecture import Architecture
from core.jl import Resolution
from core.modeltype import OutputType
from keras.applications.resnet import ResNet101
from keras.engine.input_layer import Input
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


modelbuilder.ModelBuilder.architecture(Resnet101())
