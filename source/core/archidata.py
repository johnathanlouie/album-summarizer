from os.path import isfile
from typing import Callable, List, Union

from keras.callbacks import CSVLogger, ModelCheckpoint, ReduceLROnPlateau
from keras.models import load_model
from numpy import asarray, ndarray

from core.dataholder import DataHolder
from core.dataset import DataSet, DataSetSplit, Predictions, PredictionsFactory
from core.kerashelper import PickleCheckpoint, Sequence1, TerminateOnDemand
from core.model import Architecture, ArchitectureName
from jl import Image, ImageDirectory, ListFile, Url, mkdirs


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

    def __init__(self, architecture: Architecture, split: DataSetSplit, prediction: PredictionsFactory) -> None:
        self._architecture = architecture
        self._split = split
        self._pf = prediction
        self._model = None
        self._current_epoch = None
        self._max_epoch = None
        self._lr = None
        self._mcp = None
        self._mcpb = None
        self._pcp = None
        self._best_model = None

    def name(self) -> ArchitectureSplitName:
        """
        Returns the naming object for this combination of architecture, dataset, and compile options.
        """
        return ArchitectureSplitName(self._architecture.name(), self._split)

    def _is_train_loaded(self) -> bool:
        """
        Returns true if all items are loaded.
        """
        if self._model == None:
            return False
        if self._current_epoch == None:
            return False
        if self._max_epoch == None:
            return False
        if self._lr == None:
            return False
        if self._mcp == None:
            return False
        if self._mcpb == None:
            return False
        if self._pcp == None:
            return False
        return True

    def _is_test_loaded(self) -> bool:
        """
        Returns true if the test model is loaded.
        """
        if self._best_model == None:
            return False
        return True

    def train(self) -> None:
        """
        Trains the model.
        """
        if not self._is_train_loaded():
            return
        print('Loading training X')
        x1 = self._split.train().x().load()
        print('Loading training Y')
        y1 = self._split.train().y().load()
        print('Loading validation X')
        x2 = self._split.validation().x().load()
        print('Loading validation Y')
        y2 = self._split.validation().y().load()
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

    def _test(self, x: ndarray, y: ndarray) -> None:
        """
        Tests the model using the given x and y.
        """
        if not self._is_test_loaded():
            return
        seq = Sequence1(x, y, 10)
        results = self._best_model.evaluate_generator(generator=seq, verbose=1)
        if type(results) != list:
            results = [results]
        for metric, scalar in zip(self._best_model.metrics_names, results):
            print('%s: %f' % (metric, scalar))
        return

    def validate(self) -> None:
        """
        Tests the model using the validation set.
        """
        if not self._is_test_loaded():
            return
        print('Loading validation X')
        x = self._split.validation().x().load()
        print('Loading validation Y')
        y = self._split.validation().y().load()
        self._test(x, y)
        return

    def test(self) -> None:
        """
        Tests the model using the test set.
        """
        if not self._is_test_loaded():
            return
        print('Loading test X')
        x = self._split.test().x().load()
        print('Loading test Y')
        y = self._split.test().y().load()
        self._test(x, y)
        return

    def predict(self, images: List[Image]) -> Predictions:
        """
        Predicts using the trained model.
        """
        if not self._is_test_loaded():
            return
        x = asarray(images)
        seq = Sequence1(x, x, 10)
        print('Predicting....')
        results = self._best_model.predict_generator(generator=seq, verbose=1)
        print('Prediction finished.')
        return self._pf.predictions(x, results, self.name().predictions())

    def create(self, epochs: int = 2**64, patience: int = 5) -> None:
        """
        Creates and saves the model file and other training state files.
        Initial settings are found here.
        """
        print('No saved files found.')
        print('Creating new model.')
        url = self.name()
        mkdirs(url.train())
        model = self._architecture.compile()
        model.save(url.train())
        model.save(url.test())
        print('Saved model.')
        print('Creating new training status.')
        mcp = ModelCheckpoint(url.train(), verbose=1)
        mcpb = ModelCheckpoint(url.test(), verbose=1, save_best_only=True)
        lr = ReduceLROnPlateau(patience=patience, verbose=1)
        DataHolder(url.data_holder(), 0, epochs, lr, mcp, mcpb).save()
        print('Saved DataHolder.')
        return

    def _is_saved(self) -> bool:
        """
        Returns true if all the saved files exist.
        """
        url = self.name()
        if not isfile(url.train()):
            print('Missing training model file.')
            return False
        if not isfile(url.test()):
            print('Missing training model file.')
            return False
        if not isfile(url.data_holder()):
            print('Missing training model file.')
            return False
        return True

    def load_train_model(self) -> None:
        """
        Loads the training model file and other training state files.
        """
        if not self._is_saved():
            return
        url = self.name()
        self._model = load_model(url.train(), self._architecture.custom())
        dh = DataHolder.load(url.data_holder())
        self._current_epoch = dh.current_epoch
        self._max_epoch = dh.total_epoch
        self._lr = dh.get_lr()
        self._mcp = dh.get_mcp()
        self._mcpb = dh.get_mcpb()
        self._pcp = PickleCheckpoint(self._mcp, self._mcpb, self._lr, url.data_holder(), dh.total_epoch)
        return

    def load_test_model(self) -> None:
        """
        Loads the best model file.
        """
        if not self._is_saved():
            return
        url = self.name().test()
        self._best_model = load_model(url, self._architecture.custom())
        return

    def delete(self) -> None:
        """
        Deletes the model file and other training state files.
        """
        raise NotImplementedError

    def train2(self, epochs: int = 2**64, patience: int = 5) -> None:
        """
        Convenience method to create if there are no saved files, load if not yet loaded, and then train.
        """
        if not self._is_saved():
            self.create(epochs, patience)
        if not self._is_train_loaded():
            self.load_train_model()
        self.train()
        return

    def validate2(self, epochs: int = 2**64, patience: int = 5) -> None:
        """
        Convenience method to create if there are no saved files, load if not yet loaded, and then test against the validation set.
        """
        if not self._is_saved():
            self.create(epochs, patience)
        if not self._is_test_loaded():
            self.load_test_model()
        self.validate()
        return

    def test2(self, epochs: int = 2**64, patience: int = 5) -> None:
        """
        Convenience method to create if there are no saved files, load if not yet loaded, and then test against the test set.
        """
        if not self._is_saved():
            self.create(epochs, patience)
        if not self._is_test_loaded():
            self.load_test_model()
        self.test()
        return

    def predict2(self, images: List[Image], epochs: int = 2**64, patience: int = 5) -> Predictions:
        """
        Convenience method to create if there are no saved files, load if not yet loaded, and then predict using the test set.
        """
        if not self._is_saved():
            self.create(epochs, patience)
        if not self._is_test_loaded():
            self.load_test_model()
        return self.predict(images)


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
        if not self._dataset.exists():
            self._dataset.prepare()
        return ArchitectureSplit(self._architecture, self._dataset.get_split(num), self._dataset.get_predictions_factory())

    def train_all(self, epochs: int = 2**64, patience: int = 5) -> None:
        for i in range(self._dataset.splits()):
            print("Split %d/%d" % (i + 1, self._dataset.splits()))
            self.split(i).train2(epochs, patience)
        return
