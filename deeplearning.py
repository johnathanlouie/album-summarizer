from anifood import CccafDataSet
from archidata import ArchitectureSet, ArchitectureSplit
from cc import Ccc, Ccr, CcrCategorical
from classifier import Vgg16A, Vgg16B, Vgg16C
from dataset import DataSet
from lamem import Lamem
from model import LOSS, METRIC, OPTIMIZER, Architecture, ModelFactory
from rater import Smi13, Smi13_1, Smi13_2


class DeepLearningFactory(object):
    """
    Convenience functions to create deep learning models.
    """

    ARCHITECTURES = {
        'vgg': Vgg16A(),
        'vgg1': Vgg16B(),
        'vgg2': Vgg16C(),
        'smi': Smi13(),
        'smi1': Smi13_1(),
        'smi2': Smi13_2()
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
    def create_split(cls, mf: str, ds: str, split: int, l: int, o: int, m: int) -> ArchitectureSplit:
        """
        Compiles the dataset, architecture, and options into a split.
        """
        return cls.create_set(mf, ds, l, o, m).split(split)
