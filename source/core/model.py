from __future__ import annotations

from os.path import isfile
from typing import List

from jl import Image, Url, mkdirs
from keras.callbacks import CSVLogger, ReduceLROnPlateau
from keras.models import load_model
from numpy import asarray, ndarray

from core.architecture import Architecture, CompiledArchitecture, CompiledArchitectureName, CompileOption
from core.dataset import DataSet, DataSetSplit, DataSetSplitName, Predictions, PredictionsFactory
from core.kerashelper import Sequence1, TerminateOnDemand


class ModelSplitName(object):
    """
    """

    def __init__(self, architecture: CompiledArchitectureName, data: DataSetSplitName, epochs: int, patience: int) -> None:
        self.architecture: str = architecture.architecture
        self.dataset: str = data.dataset
        self.split: int = data.split
        self.loss: str = architecture.loss
        self.optimizer: str = architecture.optimizer
        self.epochs: int = epochs
        self.patience: int = patience

    def _dirname(self) -> Url:
        """
        Returns the path up to each file.
        """
        return "out/%s-%s-%s-%s/%d-%d/%d" % (self.architecture, self.dataset, self.loss, self.optimizer, self.epochs, self.patience, self.split)

    def model(self) -> Url:
        """
        Returns the URL of the training model file.
        """
        return "%s/model.h5" % self._dirname()

    def best_model(self) -> Url:
        """
        Returns the URL of the model file that measured the best against the validation set.
        """
        return "%s/best.h5" % self._dirname()

    def mcp(self) -> Url:
        """
        Returns the URL of the pickled ModelCheckpoint2.
        """
        return "%s/mcp.dill" % self._dirname()

    def best_mcp(self) -> Url:
        """
        Returns the URL of the pickled ModelCheckpoint2 when the best model was saved.
        """
        return "%s/bestmcp.dill" % self._dirname()

    def lr(self) -> Url:
        """
        """
        return "%s/lr.dill" % self._dirname()

    def best_lr(self) -> Url:
        """
        """
        return "%s/bestlr.dill" % self._dirname()

    def epoch(self) -> Url:
        return "%s/epoch.dill" % self._dirname()

    def best_epoch(self) -> Url:
        return "%s/bestepoch.dill" % self._dirname()

    def log(self) -> Url:
        """
        Returns the URL of the training log.
        """
        return "%s/log.csv" % self._dirname()

    def predictions(self) -> Url:
        """
        Returns the URL of the predictions file.
        """
        return "%s/predictions.txt" % self._dirname()


class Evaluation(object):
    """
    """

    def __init__(self, label: str, value: float) -> None:
        self.label = label
        self.value = value
        return

    @staticmethod
    def mean(evals: List[Evaluation]) -> Evaluation:
        label = None
        value = 0
        for e in evals:
            if label == None:
                label = e.label
            if label != e.label:
                raise Exception('Evaluation labels do not match.')
            value = value + e.value
        value = value / len(evals)
        return Evaluation(label, value)


class KerasAdapter(object):
    """
    Wrapper class that encapsulates how the model and training state is saved and loaded.
    """

    def __init__(self, architecture: CompiledArchitecture, split: DataSetSplit, prediction: PredictionsFactory) -> None:
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

    def name(self) -> ModelSplitName:
        """
        Returns the naming object for this combination of architecture, dataset, and compile options.
        """
        return ModelSplitName(self._architecture.name(), self._split)

    def is_train_loaded(self) -> bool:
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

    def is_test_loaded(self) -> bool:
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

    def evaluate(self, x: ndarray, y: ndarray) -> List[Evaluation]:
        """
        Tests the model using the given x and y.
        Returns a list of metrics
        """
        seq = Sequence1(x, y, 10)
        results = self._best_model.evaluate_generator(generator=seq, verbose=1)
        return [Evaluation(label, value) for label, value in zip(self._best_model.metrics_names, results)]

    def validate(self) -> List[Evaluation]:
        """
        Tests the model using the validation set.
        """
        print('Loading validation X')
        x = self._split.validation().x().load()
        print('Loading validation Y')
        y = self._split.validation().y().load()
        return self.evaluate(x, y)

    def test(self) -> List[Evaluation]:
        """
        Tests the model using the test set.
        """
        print('Loading test X')
        x = self._split.test().x().load()
        print('Loading test Y')
        y = self._split.test().y().load()
        return self.evaluate(x, y)

    def predict(self, images: List[Image]) -> Predictions:
        """
        Predicts using the trained model.
        """
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

    def is_saved(self) -> bool:
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
        url = self.name()
        self._model = load_model(url.train(), self._architecture.custom())
        dh = DataHolder.load(url.data_holder())
        self._current_epoch = dh.current_epoch
        self._max_epoch = dh.total_epoch
        self._lr = dh.get_lr()
        self._mcp = dh.get_mcp()
        self._mcpb = dh.get_mcpb()
        self._pcp = PickleCheckpoint(
            self._mcp, self._mcpb, self._lr, url.data_holder(), dh.total_epoch)
        return

    def load_test_model(self) -> None:
        """
        Loads the best model file.
        """
        url = self.name().test()
        self._best_model = load_model(url, self._architecture.custom())
        return

    def delete(self) -> None:
        """
        Deletes the model file and other training state files.
        """
        raise NotImplementedError


class ModelSplit(object):
    """
    """

    def __init__(self, architecture: CompiledArchitecture, data: DataSetSplit, epochs: int, patience: int) -> None:
        self._architecture = architecture
        self._data = data
        self._epochs = epochs
        self._patience = patience

    def train(self) -> None:
        """
        Convenience method to create if there are no saved files, load if not yet loaded, and then train.
        """
        if not self._archisplit.is_train_loaded():
            if not self._archisplit.is_saved():
                self._archisplit.create(epochs, patience)
            self._archisplit.load_train_model()
        self._archisplit.train()
        return

    def validate(self) -> List[Evaluation]:
        """
        Convenience method to create if there are no saved files, load if not yet loaded, and then test against the validation set.
        """
        if not self._archisplit.is_test_loaded():
            if not self._archisplit.is_saved():
                self._archisplit.create(epochs, patience)
            self._archisplit.load_test_model()
        return self._archisplit.validate()

    def test(self) -> List[Evaluation]:
        """
        Convenience method to create if there are no saved files, load if not yet loaded, and then test against the test set.
        """
        if not self._archisplit.is_test_loaded():
            if not self._archisplit.is_saved():
                self._archisplit.create(epochs, patience)
            self._archisplit.load_test_model()
        return self._archisplit.test()

    def predict(self, images: List[Url]) -> Predictions:
        """
        """
        if not self._archisplit.is_test_loaded():
            if not self._archisplit.is_saved():
                self._archisplit.create(epochs, patience)
            self._archisplit.load_test_model()
        return self._archisplit.predict(images)


class Model(object):
    """
    A combination of a DataSet object and Architecture object.
    It oversees the cross-validation process, which is training and testing over multiple splits.
    Each split is handled by an ArchitectureSplit object produced by this class.
    """

    def __init__(
        self,
        architecture: Architecture,
        dataset: DataSet,
        loss: CompileOption,
        optimizer: CompileOption,
        metrics: CompileOption,
        epochs: int = 2**64,
        patience: int = 5,
    ) -> None:
        self._architecture: CompiledArchitecture = CompiledArchitecture(
            architecture,
            loss,
            optimizer,
            metrics,
        )
        self._dataset: DataSet = dataset
        self._epochs: int = epochs
        self._patience: int = patience

    def split(self, num: int) -> ModelSplit:
        """
        Get a specific split.
        """
        if not self._dataset.exists():
            self._dataset.prepare()
        return ModelSplit(
            self._architecture,
            self._dataset.get_split(num),
            self._epochs,
            self._patience,
        )

    def train(self) -> None:
        """
        Starts or continues training the model.
        """
        for i in range(self._dataset.splits()):
            print("Split %d / %d" % (i + 1, self._dataset.splits()))
            self.split(i).train()

    def test(self) -> List[Evaluation]:
        """
        Tests the model against the data set's provided test set.
        """
        results = list()
        for i in range(self._dataset.splits()):
            print("Split %d / %d" % (i + 1, self._dataset.splits()))
            r = self.split(i).test()
            results.append(r)
        averages = list()
        for i in range(len(results[0])):
            c = [split[i] for split in results]
            m = Evaluation.mean(c)
            averages.append(m)
        return averages

    def validate(self) -> List[Evaluation]:
        """
        Tests the model against the data set's provided validation set.
        """
        results = list()
        for i in range(self._dataset.splits()):
            print("Split %d / %d" % (i + 1, self._dataset.splits()))
            r = self.split(i).validate()
            results.append(r)
        averages = list()
        for i in range(len(results[0])):
            c = [split[i] for split in results]
            m = Evaluation.mean(c)
            averages.append(m)
        return averages
