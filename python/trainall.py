from typing import Tuple

import aaa
import addon
import core.modelbuilder


def builds() -> Tuple[str, str, str, str]:
    for architecture in core.modelbuilder.ModelBuilder.ARCHITECTURES.keys():
        for dataset in core.modelbuilder.ModelBuilder.DATASETS.keys():
            for loss in core.modelbuilder.ModelBuilder.LOSSES.keys():
                for optimizer in core.modelbuilder.ModelBuilder.OPTIMIZERS.keys():
                    yield architecture, dataset, loss, optimizer


def main():
    for architecture, dataset, loss, optimizer in builds():
        print()
        try:
            model = core.modelbuilder.ModelBuilder.create(
                architecture,
                dataset,
                loss,
                optimizer,
                'acc',
                epochs=0,
                patience=3,
            ).split(0)
            if model.is_complete():
                print('Complete model: %s %s %s %s %s' % (
                    architecture,
                    dataset,
                    loss,
                    optimizer,
                    'acc',
                ))
            elif model.has_error():
                print('Error model: %s %s %s %s %s' % (
                    architecture,
                    dataset,
                    loss,
                    optimizer,
                    'acc',
                ))
            else:
                model.train()
        except ValueError:
            print('Incompatible model: %s %s %s %s %s' % (
                architecture,
                dataset,
                loss,
                optimizer,
                'acc',
            ))


if __name__ == '__main__':
    main()
