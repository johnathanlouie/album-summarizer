import json
from typing import Tuple

import aaa
import addon
import core.modelbuilder


def builds() -> Tuple[str, str, str, str, str]:
    for metric in core.modelbuilder.ModelBuilder.METRICS.keys():
        for architecture in core.modelbuilder.ModelBuilder.ARCHITECTURES.keys():
            for dataset in core.modelbuilder.ModelBuilder.DATASETS.keys():
                for loss in core.modelbuilder.ModelBuilder.LOSSES.keys():
                    for optimizer in core.modelbuilder.ModelBuilder.OPTIMIZERS.keys():
                        yield architecture, dataset, loss, optimizer, metric


def main():
    results = list()
    for architecture, dataset, loss, optimizer, metric in builds():
        try:
            model = core.modelbuilder.ModelBuilder.create(
                architecture,
                dataset,
                loss,
                optimizer,
                metric,
                epochs=0,
                patience=3,
            )
            if not model.is_complete():
                results.append(model.evaluate_test_set())
        except ValueError:
            print('Incompatible model: %s %s %s %s %s' % (
                architecture,
                dataset,
                loss,
                optimizer,
                metric,
            ))
    json.dump(results, open('out/testall.json', 'w'))


if __name__ == '__main__':
    main()
