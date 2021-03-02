import aaa
import architecture.smi13
import architecture.vgg16
import coption.custom
import coption.keras
import coption.keras2
import core.modelbuilder
import dataset.anifood
import dataset.cc
import dataset.lamem


def main():
    for architecture in core.modelbuilder.ModelBuilder.ARCHITECTURES.keys():
        for dataset in core.modelbuilder.ModelBuilder.DATASETS.keys():
            for loss in core.modelbuilder.ModelBuilder.LOSSES.keys():
                for optimizer in core.modelbuilder.ModelBuilder.OPTIMIZERS.keys():
                    for metric in core.modelbuilder.ModelBuilder.METRICS.keys():
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
                                model.train()
                        except ValueError:
                            print('Incompatible model: %s %s %s %s %s' % (
                                architecture,
                                dataset,
                                loss,
                                optimizer,
                                metric,
                            ))


if __name__ == '__main__':
    main()
