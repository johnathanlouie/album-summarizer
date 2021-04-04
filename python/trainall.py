from typing import Tuple

import aaa
import builds
import core.model
import core.modelbuilder


def main():
    for architecture, dataset, loss, optimizer in builds.builds():
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
        except core.model.BadModelSettings:
            print('Incompatible model: %s %s %s %s %s' % (
                architecture,
                dataset,
                loss,
                optimizer,
                'acc',
            ))


if __name__ == '__main__':
    main()
