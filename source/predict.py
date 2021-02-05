import argparse
import json
import os.path
from typing import Dict

import aaa
import architecture.classifier
import architecture.rater
import coption.custom
import coption.keras
import coption.keras2
import core.modelbuilder
import dataset.anifood
import dataset.cc
import dataset.lamem
import jl


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
    parser.add_argument('images')
    parser.add_argument('results')
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
        if os.path.isdir(args.images):
            images = jl.ImageDirectory(args.images).jpeg(False)
        elif os.path.isfile(args.images):
            images = json.load(open('args.images'))
        else:
            raise FileNotFoundError(args.images)
        if 'split' in settings:
            model.split(settings['split']).predict(images).save_json(args.results)
        else:
            model.split(0).predict(images).save_json(args.results)


if __name__ == '__main__':
    main()
