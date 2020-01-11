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
MACHINES = [
    create_set(vgg, ccc, 8, 0, 2),  # 0
    create_set(vgg1, ccc, 8, 0, 2),  # 1
    create_set(vgg2, ccc, 8, 0, 2),  # 2
    create_set(smi, ccr, 14, 0, 0),  # 3
    create_set(smi, ccr, 14, 7, 0),  # 4
    create_set(smi1, ccrc, 14, 0, 0),  # 5
    create_set(smi, lamem, 14, 0, 0)  # 6
]

# PREPARE DATASETS
# ccc.prepare()
# ccr.prepare()
# ccrc.prepare()
# lamem.prepare()

# RUN
for m in MACHINES:
    m.train_all(100, 5)
