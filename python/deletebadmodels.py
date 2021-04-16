import aaa
import builds
import core.model
import core.modelbuilder


def main():
    for architecture, dataset, loss, optimizer in builds.builds():
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
            print()
            if model.has_error():
                model.delete(True)
        except core.model.BadModelSettings:
            print("IGNORE: %s %s %s %s" % (architecture, dataset, loss, optimizer))


if __name__ == '__main__':
    main()
