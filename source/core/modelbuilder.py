from core.architecture import Architecture, CompiledArchitecture, CompileOption
from core.dataset import DataSet
from core.model import Model, ModelSplitAdapter


class ModelBuilder(object):
    """
    Convenience functions to create deep learning models.
    """

    ARCHITECTURES = dict()
    DATASETS = dict()
    LOSSES = dict()
    OPTIMIZERS = dict()
    METRICS = dict()

    @classmethod
    def create_set(
        cls,
        architecture: str,
        dataset: str,
        loss: str,
        optimizer: str,
        metrics: str,
    ) -> Model:
        """
        Compiles the dataset, architecture, and options into a architecture set.
        """
        a = CompiledArchitecture(
            cls.ARCHITECTURES[architecture],
            cls.LOSSES[loss],
            cls.OPTIMIZERS[optimizer],
            cls.METRICS[metrics],
        )
        return Model(a, cls.DATASETS[dataset])

    @classmethod
    def create_split(
        cls,
        architecture: str,
        dataset: str,
        split: int,
        loss: str,
        optimizer: str,
        metrics: str,
    ) -> ModelSplitAdapter:
        """
        Compiles the dataset, architecture, and options into a split.
        """
        return cls.create_set(architecture, dataset, loss, optimizer, metrics).split(split)

    @classmethod
    def architecture(cls, architecture: Architecture) -> None:
        if architecture.NAME in cls.ARCHITECTURES:
            raise KeyError
        else:
            cls.ARCHITECTURES[architecture.NAME] = architecture

    @classmethod
    def dataset(cls, dataset: DataSet) -> None:
        if dataset.NAME in cls.DATASETS:
            raise KeyError
        else:
            cls.DATASETS[dataset.NAME] = dataset

    @classmethod
    def loss(cls, option: CompileOption) -> None:
        if option.name in cls.LOSSES:
            raise KeyError
        else:
            cls.LOSSES[option.name] = option

    @classmethod
    def optimizer(cls, option: CompileOption) -> None:
        if option.name in cls.OPTIMIZERS:
            raise KeyError
        else:
            cls.OPTIMIZERS[option.name] = option

    @classmethod
    def metric(cls, option: CompileOption) -> None:
        if option.name in cls.METRICS:
            raise KeyError
        else:
            cls.METRICS[option.name] = option
