from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Union

from keras.models import Model
from keras.optimizers import Optimizer

from rasek.jl import Resolution
from rasek.modeltype import OutputType


class Architecture(ABC):
    """
    Factory for keras.models.Model.
    """

    @property
    @staticmethod
    @abstractmethod
    def NAME() -> str:
        pass

    @property
    @staticmethod
    @abstractmethod
    def OUTPUT_TYPE() -> OutputType:
        pass

    @abstractmethod
    def create(self, res: Resolution, classes: Optional[int]) -> Model:
        """
        Creates an keras.models.Model.
        """
        pass

    def summary(self, res: Resolution, classes: Optional[int]):
        """
        """
        kmodel = self.create(res, classes)
        kmodel.summary()
        model_summary = {
            'name': self.NAME,
            'params': kmodel.count_params(),
            'layers': list(),
        }
        for layer in kmodel.layers:
            layer_config = layer.get_config()
            layer_dict = {
                'name': layer.name,
                'layer_type': layer.__class__.__name__,
                'params': layer.count_params(),
            }
            if type(layer.output_shape) == tuple:
                output_shape = layer.output_shape
            elif type(layer.output_shape) == list:
                output_shape = layer.output_shape[0]
            else:
                raise Exception
            layer_dict['output_shape'] = [int(i) for i in output_shape[1:]]
            if 'activation' in layer_config:
                layer_dict['activation'] = layer_config['activation']
            else:
                layer_dict['activation'] = None
            if hasattr(layer, 'kernel_size'):
                layer_dict['kernel_size'] = layer.kernel_size
            else:
                layer_dict['kernel_size'] = None
            if hasattr(layer, 'pool_size'):
                layer_dict['pool_size'] = layer.pool_size
            else:
                layer_dict['pool_size'] = None
            model_summary['layers'].append(layer_dict)
        return model_summary


class CompileOption(object):
    """
    Options for compiling deep learning architecture.
    """

    def __init__(self, name: str, value: Union[Callable, str, Optimizer]) -> None:
        self.name: str = name
        self.value: Union[Callable, str, Optimizer] = value


class CompiledArchitectureName(object):
    """
    Passes information to the ArchitectureSplit class for making URLs.
    """

    def __init__(self, architecture: str, loss: str, optimizer: str, metric: str):
        self.architecture: str = architecture
        self.loss: str = loss
        self.optimizer: str = optimizer
        self.metric: str = metric


class CompiledArchitecture(object):
    """
    Creates a compiled keras.models.Model object with options and creates the argument for the custom_objects parameter for the keras.models.load_model function.
    """

    def __init__(
        self,
        architecture: Architecture,
        loss: CompileOption,
        optimizer: CompileOption,
        metric: CompileOption,
    ) -> None:
        self._architecture: architecture = architecture
        self._loss: CompileOption = loss
        self._optimizer: CompileOption = optimizer
        self._metric: CompileOption = metric

    def compile(self, res: Resolution, classes: Optional[int]) -> Model:
        """
        Creates a compiled keras.models.Model object.
        """
        # if type(m) != list or type(m) != dict:
        #     m = [m]
        kmodel = self._architecture.create(res, classes)
        kmodel.compile(
            loss=self._loss.value,
            optimizer=self._optimizer.value,
            metrics=[self._metric.value],
        )
        return kmodel

    @staticmethod
    def _is_custom(x: Any) -> bool:
        if isinstance(x, Optimizer) or type(x) == str:
            return False
        elif callable(x):
            return True
        else:
            raise TypeError

    def custom(self) -> Dict[str, Callable]:
        """
        Creates the argument for the custom_objects parameter for the keras.models.load_model function.
        """
        d = dict()
        if self._is_custom(self._loss.value):
            d[self._loss.value.__name__] = self._loss.value
        if self._is_custom(self._optimizer.value):
            d[self._optimizer.value.__name__] = self._optimizer.value
        if self._is_custom(self._metric.value):
            d[self._metric.value.__name__] = self._metric.value
        return d

    def name(self) -> CompiledArchitectureName:
        """
        Creates a data object with the names of the architecture and compile options.
        """
        return CompiledArchitectureName(self._architecture.NAME, self._loss.name, self._optimizer.name, self._metric.name)

    def summary(self, res: Resolution, classes: Optional[int]) -> None:
        return self._architecture.summary(res, classes)
