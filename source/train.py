import argparse
import json
from typing import Dict

import aaa
import architecture.vgg16
import architecture.smi13
import coption.custom
import coption.keras
import coption.keras2
import core.modelbuilder
import dataset.anifood
import dataset.cc
import dataset.lamem


def main():
    print()
    print('Architectures')
    for i in core.modelbuilder.ModelBuilder.ARCHITECTURES.keys():
        print(' - %s' % i)
    print('Data Sets')
    for i in core.modelbuilder.ModelBuilder.DATASETS.keys():
        print(' - %s' % i)
    print('Losses')
    for i in core.modelbuilder.ModelBuilder.LOSSES.keys():
        print(' - %s' % i)
    print('Optimizers')
    for i in core.modelbuilder.ModelBuilder.OPTIMIZERS.keys():
        print(' - %s' % i)
    print('Metrics')
    for i in core.modelbuilder.ModelBuilder.METRICS.keys():
        print(' - %s' % i)
    print()
    parser = argparse.ArgumentParser()
    parser.add_argument('model')
    args = parser.parse_args()
    with open(args.model) as f:
        settings: Dict[str, str] = json.load(f)
        model = core.modelbuilder.ModelBuilder.create(
            settings['architecture'],
            settings['dataset'],
            settings['loss'],
            settings['optimizer'],
            settings['metrics'],
            settings['epochs'],
            settings['patience'],
        )
        if 'split' in settings:
            model.split(settings['split']).train()
        else:
            model.train()


if __name__ == '__main__':
    main()
