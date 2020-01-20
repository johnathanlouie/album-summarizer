from argparse import ArgumentParser, Namespace

import aaa
from anifood import CccafDataSet
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


def create_set(mf: ModelFactory, ds: DataSet, l: int, o: int, m: int) -> ArchitectureSet:
    """
    Compiles the dataset, architecture, and options into a architecture set.
    """
    a = Architecture(mf, LOSS[l], OPTIMIZER[o], METRIC[m])
    return ArchitectureSet(a, ds)


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


def proc_args() -> Namespace:
    """
    Parses program arguments.
    """
    parser = ArgumentParser(description='Deep learning section of the album summarizer.')
    parser.add_argument('mode', help='', choices=['train', 'predict'])
    parser.add_argument('architecture', help='', choices=ARCHITECTURES.keys())
    parser.add_argument('dataset', help='', choices=DATASETS.keys())
    parser.add_argument('split', help='', type=int)
    parser.add_argument('loss', help='', type=int)
    parser.add_argument('optimizer', help='', type=int)
    parser.add_argument('metric', help='', type=int)
    parser.add_argument('-e', '--epochs', help='', type=int, default=100)
    parser.add_argument('-p', '--patience', help='', type=int, default=5)
    args = parser.parse_args()
    return args


# DATASETS
# ccr = Ccr()
# ccc = Ccc()
# ccrc = CcrCategorical()
# lamem = Lamem()
# cccaf = CccafDataSet()

# PREPARE DATASETS
# ccc.prepare()
# ccr.prepare()
# ccrc.prepare()
# lamem.prepare()
# cccaf.prepare()


def main() -> None:
    """
    Starts the program.
    """
    args = proc_args()
    mode = args.mode
    architecture = ARCHITECTURES[args.architecture]
    dataset = DATASETS[args.dataset]
    epochs = args.epochs
    patience = args.patience
    x = create_split(
        architecture,
        dataset,
        args.split,
        args.loss,
        args.optimizer,
        args.metric
    )
    if mode == 'train':
        x.train2(epochs, patience)
    elif mode == 'validate':
        x.validate2(epochs, patience)
    elif mode == 'test':
        x.test2(epochs, patience)
    elif mode == 'predict':
        x.predict2(epochs, patience)
    else:
        raise Exception
    return


main()
