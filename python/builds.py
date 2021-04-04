from typing import Tuple

import addon
import core.modelbuilder


def builds() -> Tuple[str, str, str, str]:
    for architecture in core.modelbuilder.ModelBuilder.ARCHITECTURES.keys():
        for dataset in core.modelbuilder.ModelBuilder.DATASETS.keys():
            for loss in core.modelbuilder.ModelBuilder.LOSSES.keys():
                for optimizer in core.modelbuilder.ModelBuilder.OPTIMIZERS.keys():
                    yield architecture, dataset, loss, optimizer
