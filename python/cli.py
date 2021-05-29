import argparse
import json
from typing import Dict

import aaa
import addon
import core.modelbuilder
import core.model


def doSomething(
        architecture,
        dataset,
        loss,
        optimizer,
        metrics,
        epochs,
        patience,
        split=None,
        summary=False,
        train=False,
        evaluate=False,
        remove_bad=False
):
    try:
        print()
        print()
        model = core.modelbuilder.ModelBuilder.create(
            architecture,
            dataset,
            loss,
            optimizer,
            metrics,
            epochs,
            patience,
        )
        if summary:
            model.summary()
        else:
            if split != None:
                model = model.split(split)
            if train and evaluate and remove_bad:
                model.auto_train()
            else:
                if train:
                    if model.is_complete():
                        print('COMPLETE: %s %s %s %s %s' % (
                            architecture,
                            dataset,
                            loss,
                            optimizer,
                            'acc',
                        ))
                    elif model.has_error():
                        print('ERROR: %s %s %s %s %s' % (
                            architecture,
                            dataset,
                            loss,
                            optimizer,
                            'acc',
                        ))
                    else:
                        print('TRAINING: %s %s %s %s %s' % (
                            architecture,
                            dataset,
                            loss,
                            optimizer,
                            'acc',
                        ))
                        model.train()
                if evaluate:
                    if model.is_complete():
                        model.evaluate_training_set()
                        model.evaluate_validation_set()
                        model.evaluate_test_set()
                if remove_bad:
                    if model.has_error():
                        model.delete(True)
    except core.model.BadModelSettings:
        print("IGNORE: %s %s %s %s" % (architecture, dataset, loss, optimizer))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--options', action='store_true')
    parser.add_argument('--summary', action='store_true')
    parser.add_argument('--train', action='store_true')
    parser.add_argument('--evaluate', action='store_true')
    parser.add_argument('--removebad', action='store_true')
    args = parser.parse_args()
    if args.options:
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
    elif args.model != None:
        try:
            with open(args.model) as f:
                settings: Dict[str, str] = json.load(f)
                doSomething(
                    settings['architecture'],
                    settings['dataset'],
                    settings['loss'],
                    settings['optimizer'],
                    settings['metrics'],
                    settings['epochs'],
                    settings['patience'],
                    settings.get('split'),
                    args.summary,
                    args.train,
                    args.evaluate,
                    args.removebad,
                )
        except FileNotFoundError:
            print("MISSING: %s" % args.model)
    elif args.all:
        for architecture, dataset, loss, optimizer in core.modelbuilder.ModelBuilder.builds():
            print()
            doSomething(
                architecture,
                dataset,
                loss,
                optimizer,
                'acc',
                epochs=0,
                patience=3,
                split=0,
                summary=args.summary,
                train=args.train,
                evaluate=args.evaluate,
                remove_bad=args.removebad,
            )


if __name__ == '__main__':
    main()
