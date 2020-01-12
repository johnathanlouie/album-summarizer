import aaa
from archidata import ArchitectureSet, ArchitectureSplit
from cc import Ccc, Ccr, CcrCategorical
from classifier import Vgg16A, Vgg16B, Vgg16C
from dataset import DataSet
from lamem import Lamem
from model import LOSS, METRIC, OPTIMIZER, Architecture, ModelFactory
from rater import Smi13, Smi13_1, Smi13_2


def create_split(mf: ModelFactory, ds: DataSet, split: int, l: int, o: int, m: int) -> ArchitectureSplit:
    """
    Compiles the dataset, architecture, and options into a split.
    """
    a = Architecture(mf, LOSS[l], OPTIMIZER[o], METRIC[m])
    aset = ArchitectureSet(a, ds)
    return aset.split(split)


def create_set(mf: ModelFactory, ds: DataSet, l: int, o: int, m: int) -> None:
    """
    Compiles the dataset, architecture, and options into a architecture set.
    """
    a = Architecture(mf, LOSS[l], OPTIMIZER[o], METRIC[m])
    return ArchitectureSet(a, ds)


# MODEL FACTORIES
vgg = Vgg16A()
vgg1 = Vgg16B()
vgg2 = Vgg16C()
smi = Smi13()
smi1 = Smi13_1()
smi2 = Smi13_2()

# DATASETS
ccr = Ccr()
ccc = Ccc()
ccrc = CcrCategorical()
lamem = Lamem()

# ARCHITECTURE-DATASET COMBOS
# create_set(vgg, ccc, 8, 0, 2)
# create_set(vgg1, ccc, 8, 0, 2)
# create_set(vgg2, ccc, 8, 0, 2)
# create_set(smi, ccr, 14, 0, 0)
# create_set(smi, ccr, 14, 7, 0)
# create_set(smi1, ccrc, 14, 0, 0)
# create_set(smi, lamem, 14, 0, 0)

# PREPARE DATASETS
# ccc.prepare()
# ccr.prepare()
# ccrc.prepare()
# lamem.prepare()

# RUN
# create_split(vgg2, ccc, 0, 8, 0, 2).train2(100, 5)
# create_split(vgg2, ccc, 1, 8, 0, 2).train2(100, 5)
# create_split(vgg2, ccc, 2, 8, 0, 2).train2(100, 5)
# create_split(vgg2, ccc, 3, 8, 0, 2).train2(100, 5)
# create_split(vgg2, ccc, 4, 8, 0, 2).train2(100, 5)

# create_split(smi1, ccrc, 0, 14, 0, 0)
# create_split(smi1, ccrc, 1, 14, 0, 0)
# create_split(smi1, ccrc, 2, 14, 0, 0)
# create_split(smi1, ccrc, 3, 14, 0, 0)
# create_split(smi1, ccrc, 4, 14, 0, 0)
