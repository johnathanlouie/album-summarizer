from core.architecture import Architecture, CompileOption
from core.dataset import DataSet
from core.model import Model


class ModelBuilderInsertError(LookupError):
    pass


class ModelBuilder(object):
    """
    Builder class to create deep learning models.
    New architectures, data sets, and compile options are added here.
    """

    ARCHITECTURES = dict()
    DATASETS = dict()
    LOSSES = dict()
    OPTIMIZERS = dict()
    METRICS = dict()

    @classmethod
    def create(
        cls,
        architecture: str,
        dataset: str,
        loss: str,
        optimizer: str,
        metrics: str,
        epochs: int,
        patience: int,
    ) -> Model:
        """
        Builds a deep learning model from a pool of datasets, architectures, and options.
        """
        return Model(
            cls.ARCHITECTURES[architecture],
            cls.DATASETS[dataset],
            cls.LOSSES[loss],
            cls.OPTIMIZERS[optimizer],
            cls.METRICS[metrics],
            epochs,
            patience,
        )

    @classmethod
    def architecture(cls, architecture: Architecture) -> None:
        if architecture.NAME in cls.ARCHITECTURES:
            raise ModelBuilderInsertError
        else:
            cls.ARCHITECTURES[architecture.NAME] = architecture

    @classmethod
    def dataset(cls, dataset: DataSet) -> None:
        if dataset.NAME in cls.DATASETS:
            raise ModelBuilderInsertError
        else:
            cls.DATASETS[dataset.NAME] = dataset

    @classmethod
    def loss(cls, option: CompileOption) -> None:
        if option.name in cls.LOSSES:
            raise ModelBuilderInsertError
        else:
            cls.LOSSES[option.name] = option

    @classmethod
    def optimizer(cls, option: CompileOption) -> None:
        if option.name in cls.OPTIMIZERS:
            raise ModelBuilderInsertError
        else:
            cls.OPTIMIZERS[option.name] = option

    @classmethod
    def metric(cls, option: CompileOption) -> None:
        if option.name in cls.METRICS:
            raise ModelBuilderInsertError
        else:
            cls.METRICS[option.name] = option
