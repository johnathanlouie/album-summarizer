from os.path import isfile

from keras.callbacks import CSVLogger, ModelCheckpoint, ReduceLROnPlateau
from keras.models import load_model

from dataholder import DataHolder
from dataset import DataSet, DataSetSplit
from jl import ListFile, Url, mkdirs
from kerashelper import PickleCheckpoint, Sequence1, TerminateOnDemand
from model import Architecture, ArchitectureName


class ArchitectureSplitName(object):
    """
    Naming object for the files used by the ArchitectureSplit class.
    """

    def __init__(self, architecture: ArchitectureName, split: DataSetSplit) -> None:
        self.model = architecture.model
        self.dataset = split.dataset
        self.loss = architecture.loss
        self.optimizer = architecture.optimizer
        self.split = split.split
        return

    def _path(self) -> Url:
        """
        Returns the path up to each file.
        Example:
        out/model.dataset.loss.optimizer/split/saved.file
        """
        return "out/%s.%s.%s.%s/%d" % (self.model, self.dataset, self.loss, self.optimizer, self.split)

    def train(self) -> Url:
        """
        Returns the URL of the training model file.
        """
        return "%s/model.h5" % self._path()

    def test(self) -> Url:
        """
        Returns the URL of the testing model file.
        """
        return "%s/best.h5" % self._path()

    def data_holder(self) -> Url:
        """
        Returns the URL of the dill file.
        """
        return "%s/train.dill" % self._path()

    def csv(self) -> Url:
        """
        Returns the URL of the training log.
        """
        return "%s/log.csv" % self._path()

    def predictions(self) -> Url:
        """
        Returns the URL of the predictions file.
        """
        return "%s/pred.txt" % self._path()


class ArchitectureSplit(object):
    """
    Produced by the ArchitectureSet class.
    A combination of the ArchitectureSet class and the DataSetSplit class.
    Trains, validates, tests, and predicts.
    """

    def __init__(self, architecture: Architecture, split: DataSetSplit) -> None:
        self._architecture = architecture
        self._split = split

    def name(self) -> ArchitectureSplitName:
        """
        Returns the naming object for this combination of architecture, dataset, and compile options.
        """
        return ArchitectureSplitName(self._architecture.name(), self._split)

    def train(self) -> None:
        """
        Trains the model.
        """
        self._load_train_model()
        print('Loading training X')
        x1 = self._split.train().x().load()
        print('Loading training Y')
        y1 = self._split.train().y().load()
        print('Loading validation X')
        x2 = self._split.validatation().x().load()
        print('Loading validation Y')
        y2 = self._split.validatation().y().load()
        print('Training sequence')
        seq1 = Sequence1(x1, y1, 10)
        print('Validation sequence')
        seq2 = Sequence1(x2, y2, 10)
        print('Training starts')
        term = TerminateOnDemand()
        csv = CSVLogger(self.name().csv(), append=True)
        self._model.fit_generator(
            generator=seq1,
            epochs=self._max_epoch,
            verbose=1,
            validation_data=seq2,
            shuffle=False,
            initial_epoch=self._current_epoch,
            callbacks=[
                self._lr,
                self._mcp,
                self._mcpb,
                self._pcp,
                csv,
                term
            ]
        )
        print('Training finished')
        return

    def validate(self) -> None:
        """
        Tests the model using the validation set.
        """
        self._load_test_model()
        print('Loading validation X')
        x = self._split.validatation().x().load()
        print('Loading validation Y')
        y = self._split.validatation().y().load()
        print('Validation sequence')
        seq = Sequence1(x, y, 10)
        print('Validation starts')
        results = self._model.evaluate_generator(generator=seq, verbose=1)
        print('Validation finished')
        if type(results) != list:
            results = [results]
        for metric, scalar in zip(self._model.metrics_names, results):
            print('%s: %f' % (metric, scalar))
        return

    def test(self) -> None:
        """
        Tests the model using the test set.
        """
        self._load_test_model()
        print('Loading test X')
        x = self._split.test().x().load()
        print('Loading test Y')
        y = self._split.test().y().load()
        print('Testing sequence')
        seq = Sequence1(x, y, 10)
        print('Testing starts')
        results = self._model.evaluate_generator(generator=seq, verbose=1)
        print('Testing finished')
        if type(results) != list:
            results = [results]
        for metric, scalar in zip(self._model.metrics_names, results):
            print('%s: %f' % (metric, scalar))
        return

    def predict(self) -> None:
        """
        Predicts using the trained model.
        """
        self._load_test_model()
        print('Loading test X')
        x = self._split.test().x().load()
        print('Loading test Y')
        y = self._split.test().y().load()
        print('Prediction sequence')
        seq = Sequence1(x, y, 10)
        print('Prediction starts')
        results = self._model.predict_generator(generator=seq, verbose=1)
        print('Prediction finished')
        if len(results.shape) == 2:
            if results.shape[1] == 1:
                results = results.flatten()
            else:
                results = results.argmax(1)
                # results = class_str_int(results)
        url = self.name().predictions()
        ListFile(url).write(results)
        print('Saved predictions to %s' % (url))
        return results

    def create(self, epochs: int = 2**64, patience: int = 5) -> None:
        """
        Creates and saves the model file and other training state files.
        Initial settings are found here.
        """
        print('No saved files found.')
        print('Creating new model.')
        url = self.name()
        mkdirs(url.train())
        self._architecture.compile().save(url.train())
        print('Saved model.')
        print('Creating new training status.')
        mcp = ModelCheckpoint(url.train(), verbose=1)
        mcpb = ModelCheckpoint(url.test(), verbose=1, save_best_only=True)
        lr = ReduceLROnPlateau(patience=patience, verbose=1)
        DataHolder(url.data_holder(), 0, epochs, lr, mcp, mcpb).save()
        print('Saved DataHolder.')
        return

    def _load_train_model(self) -> None:
        """
        Loads the training model file and other training state files.
        """
        url = self.name()
        if not isfile(url.train()):
            print('Missing training model file.')
            raise SystemExit
        dh_url = url.data_holder()
        if not isfile(dh_url):
            print('Missing training model file.')
            raise SystemExit
        self._model = load_model(url.train(), self._architecture.custom())
        dh = DataHolder.load(dh_url)
        self._current_epoch = dh.current_epoch
        self._max_epoch = dh.total_epoch
        self._lr = dh.get_lr()
        self._mcp = dh.get_mcp()
        self._mcpb = dh.get_mcpb()
        self._pcp = PickleCheckpoint(self._mcp, self._mcpb, self._lr, self.name(), dh.total_epoch)
        return

    def _load_test_model(self) -> None:
        """
        Loads the best model file.
        """
        url = self.name().test()
        if not isfile(url):
            print('Missing training model file.')
            raise SystemExit
        self._best_model = load_model(url, self._architecture.custom())
        return

    def delete(self) -> None:
        """
        Deletes the model file and other training state files.
        """
        raise NotImplementedError


class ArchitectureSet(object):
    """
    A combination of a DataSet object and Architecture object.
    It oversees the cross-validation process, which is training and testing over multiple splits.
    Each split is handled by an ArchitectureSplit object produced by this class.
    """

    def __init__(self, architecture: Architecture, dataset: DataSet) -> None:
        self._architecture = architecture
        self._dataset = dataset
        return

    def split(self, num: int) -> ArchitectureSplit:
        """
        Get a specific split.
        """
        return ArchitectureSplit(self._architecture, self._dataset.split(num))
