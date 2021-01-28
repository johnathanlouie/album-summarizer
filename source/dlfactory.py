from core.model import ModelSplitAdapter, Model
from core.dataset import DataSet
from core.architecture import LOSS, METRIC, OPTIMIZER, CompiledArchitecture, Architecture


class DeepLearningFactory(object):
    """
    Convenience functions to create deep learning models.
    """

    ARCHITECTURES = dict()
    DATASETS = dict()

    @classmethod
    def create_set(cls, mf: str, ds: str, l: int, o: int, m: int) -> Model:
        """
        Compiles the dataset, architecture, and options into a architecture set.
        """
        a = CompiledArchitecture(cls.ARCHITECTURES[mf], LOSS[l], OPTIMIZER[o], METRIC[m])
        return Model(a, cls.DATASETS[ds])

    @classmethod
    def create_split(cls, mf: str, ds: str, split: int, l: int, o: int, m: int) -> ModelSplitAdapter:
        """
        Compiles the dataset, architecture, and options into a split.
        """
        return cls.create_set(mf, ds, l, o, m).split(split)

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
