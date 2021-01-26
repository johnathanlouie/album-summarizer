from architecture.classifier import Vgg16A, Vgg16B, Vgg16C
from architecture.rater import Smi13, Smi13_1, Smi13_2
from core.archidata import ArchiSplitAdapter, ArchitectureSet
from core.dataset import DataSet
from core.model import LOSS, METRIC, OPTIMIZER, Architecture, ModelFactory
from dataset.anifood import CccafDataSet
from dataset.cc import Ccc, Ccr, CcrCategorical
from dataset.lamem import Lamem


class DeepLearningFactory(object):
    """
    Convenience functions to create deep learning models.
    """

    ARCHITECTURES = {
        'smi': Smi13(),
        'smi1': Smi13_1(),
        'smi2': Smi13_2(),
    }

    DATASETS = {
        'ccr': Ccr(),
        'ccc': Ccc(),
        'ccrc': CcrCategorical(),
        'lamem': Lamem(),
        'cccaf': CccafDataSet()
    }

    @classmethod
    def create_set(cls, mf: str, ds: str, l: int, o: int, m: int) -> ArchitectureSet:
        """
        Compiles the dataset, architecture, and options into a architecture set.
        """
        a = Architecture(cls.ARCHITECTURES[mf], LOSS[l], OPTIMIZER[o], METRIC[m])
        return ArchitectureSet(a, cls.DATASETS[ds])

    @classmethod
    def create_split(cls, mf: str, ds: str, split: int, l: int, o: int, m: int) -> ArchiSplitAdapter:
        """
        Compiles the dataset, architecture, and options into a split.
        """
        return cls.create_set(mf, ds, l, o, m).split(split)

    @classmethod
    def architecture(cls, architecture: ModelFactory) -> None:
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
