import json
from typing import Tuple

import aaa
import addon
import core.modelbuilder


def main():
    results = list()
    for architecture, dataset, loss, optimizer, metric in core.modelbuilder.ModelBuilder.builds():
        try:
            model = core.modelbuilder.ModelBuilder.create(
                architecture,
                dataset,
                loss,
                optimizer,
                metrics='acc',
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
