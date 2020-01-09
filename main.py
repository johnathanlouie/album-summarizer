import aaa
from archidata import ArchitectureSet, ArchitectureSplit
from cc import Ccc, Ccr, CcrCategorical
from classifier import Vgg16A, Vgg16B, Vgg16C
from dataset import DataSet
from lamem import Lamem
from model import LOSS, METRIC, OPTIMIZER, Architecture, ModelFactory
from rater import Smi13, Smi13_1, Smi13_2


def create(mf: ModelFactory, ds: DataSet, split: int, l: int, o: int, m: int) -> ArchitectureSplit:
    """
    Compiles the dataset, architecture, and options into a split.
    """
    a = Architecture(mf, LOSS[l], OPTIMIZER[o], METRIC[m])
    aset = ArchitectureSet(a, ds)
    return aset.split(split)


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

# PREPARE DATASETS
# ccc.prepare()
# ccr.prepare()
# ccrc.prepare()
lamem.prepare()

# ARCHITECTURE-DATASET COMBOS
# archisplit = create(vgg, ccc, 1, 8, 0, 2)
# archisplit = create(vgg1, ccc, 1, 8, 0, 2)
# archisplit = create(vgg2, ccc, 1, 8, 0, 2)
# archisplit = create(smi, ccr, 1, 14, 0, 0)
# archisplit = create(smi, ccr, 1, 14, 7, 0)
# archisplit = create(smi1, ccrc, 1, 14, 0, 0)
archisplit = create(smi, lamem, 1, 14, 0, 0)

# RUN
# archisplit.create(100, 5)
archisplit.train()
