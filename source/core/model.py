from __future__ import annotations

from enum import Enum, auto
from os.path import isfile
from typing import List

import keras.models
from jl import Image, Url, mkdirs
from keras.callbacks import CSVLogger, ReduceLROnPlateau
from numpy import asarray, ndarray

from core.architecture import (Architecture, CompiledArchitecture,
                               CompiledArchitectureName, CompileOption)
from core.dataset import (DataSet, DataSetSplit, DataSetSplitName, Predictions,
                          PredictionsFactory)
from core.kerashelper import (EpochObserver, EpochPickle, ModelCheckpoint2,
                              ModelCheckpoint2Pickle,
                              ReduceLROnPlateauObserver,
                              ReduceLROnPlateauPickle, SaveKmodelObserver,
                              Sequence1, TerminateOnDemand)


class ModelSplitName2(object):
    """
    """

    def __init__(self, dirname: Url, snapshot: Url):
        self.dirname: Url = '%s/%s' % (dirname, snapshot)

    def weights(self) -> Url:
        """
        Returns the URL of the training model file.
        """
        return "%s/weights.h5" % self.dirname

    def mcp(self) -> Url:
        """
        Returns the URL of the pickled ModelCheckpoint2.
        """
        return "%s/mcp.dill" % self.dirname

    def lr(self) -> Url:
        """
        """
        return "%s/lr.dill" % self.dirname

    def epoch(self) -> Url:
        return "%s/epoch.dill" % self.dirname


class ModelSplitName(object):
    """
    """

    def __init__(self, architecture: CompiledArchitectureName, data: DataSetSplitName, epochs: int, patience: int) -> None:
        self._architecture: str = architecture.architecture
        self._dataset: str = data.dataset
        self._split: int = data.split
        self._loss: str = architecture.loss
        self._optimizer: str = architecture.optimizer
        self._epochs: int = epochs
        self._patience: int = patience
        self.latest: ModelSplitName2 = ModelSplitName2(self.dirname(), 'latest')
        self.best: ModelSplitName2 = ModelSplitName2(self.dirname(), 'best')

    def dirname(self) -> Url:
        """
        Returns the path up to each file.
        """
        return "out/%s-%s-%s-%s/%d-%d/%d" % (self._architecture, self._dataset, self._loss, self._optimizer, self._epochs, self._patience, self._split)

    def log(self) -> Url:
        """
        Returns the URL of the training log.
        """
        return "%s/log.csv" % self.dirname()

    def predictions(self) -> Url:
        """
        Returns the URL of the predictions file.
        """
        return "%s/predictions.txt" % self.dirname()


class Evaluation(dict):
    """
    Dictionary that holds loss/metric names as keys and scalar values.
    """

    @staticmethod
    def mean(evals: List[Evaluation]) -> Evaluation:
        result = dict()
        for e in evals:
            for k, v in e.items():
                if k not in result:
                    result[k] = 0.0
                result[k] += v
        for k, v in result:
            result[k] = v / len(evals)
        return result


class KerasAdapter(object):
    """
    Wrapper class that encapsulates how the model and training state is saved and loaded.
    """

    def __init__(
        self,
        architecture: CompiledArchitecture,
        data: DataSetSplit,
        epochs: int,
        patience: int,
    ) -> None:
        self._architecture: CompiledArchitecture = architecture
        self._data: DataSetSplit = data
        self._names: ModelSplitName = ModelSplitName(architecture.name(), data.name(), epochs, patience)
        self._kmodel: keras.models.Model = None
        self._total_epochs: int = epochs
        self._patience: int = patience
        self._is_best: bool = False

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        del self._kmodel
        return False

    def train(self) -> None:
        """
        Trains the model
        """
        # Training state
        term = TerminateOnDemand()
        log = CSVLogger(self._names.log(), append=True)
        print('Loading training state')
        if not self._is_best:
            print('Loading %s' % self._names.latest.epoch())
            current_epoch: int = EpochPickle.load(self._names.latest.epoch()).get()
            print('Loading %s' % self._names.latest.lr())
            lr: ReduceLROnPlateau = ReduceLROnPlateauPickle.load(self._names.latest.lr()).get()
            print('Loading %s' % self._names.latest.mcp())
            mcp = ModelCheckpoint2.load(self._names.latest.mcp())
        else:
            print('Loading %s' % self._names.best.epoch())
            current_epoch: int = EpochPickle.load(self._names.best.epoch()).get()
            print('Loading %s' % self._names.best.lr())
            lr: ReduceLROnPlateau = ReduceLROnPlateauPickle.load(self._names.best.lr()).get()
            print('Loading %s' % self._names.best.mcp())
            mcp = ModelCheckpoint2.load(self._names.best.mcp())
        mcp.add_periodic_observer(SaveKmodelObserver(self._names.latest.weights()))
        mcp.add_periodic_observer(ReduceLROnPlateauObserver(self._names.latest.lr(), lr))
        mcp.add_periodic_observer(EpochObserver(self._names.latest.epoch()))
        mcp.add_improvement_observer(SaveKmodelObserver(self._names.best.weights()))
        mcp.add_improvement_observer(ReduceLROnPlateauObserver(self._names.best.lr(), lr))
        mcp.add_improvement_observer(EpochObserver(self._names.best.epoch()))

        # Training set
        print('Loading training X')
        x1 = self._data.train().x().load()
        print('Loading training Y')
        y1 = self._data.train().y().load()
        print('Loading validation X')
        x2 = self._data.validation().x().load()
        print('Loading validation Y')
        y2 = self._data.validation().y().load()
        print('Training sequence')
        seq1 = Sequence1(x1, y1, 10)
        print('Validation sequence')
        seq2 = Sequence1(x2, y2, 10)

        # Training
        print('Training starts')
        self._kmodel.fit_generator(
            generator=seq1,
            epochs=self._total_epochs,
            verbose=1,
            validation_data=seq2,
            shuffle=False,
            initial_epoch=current_epoch,
            callbacks=[
                lr,
                log,
                mcp,
                term,
            ],
        )
        print('Training finished')

    def evaluate(self, x: ndarray, y: ndarray) -> Evaluation:
        """
        Evaluates the model using the given x and y.
        Returns a list of metrics.
        """
        seq = Sequence1(x, y, 10)
        results: List[float] = self._kmodel.evaluate_generator(
            generator=seq,
            verbose=1
        )
        return Evaluation({metric: scalar for metric, scalar in zip(self._kmodel.metrics_names, results)})

    def evaluate_training_set(self) -> Evaluation:
        """
        Evaluates the model using the training set
        """
        print('Loading validation X')
        x = self._data.train().x().load()
        print('Loading validation Y')
        y = self._data.train().y().load()
        return self.evaluate(x, y)

    def validate(self) -> Evaluation:
        """
        Evaluates the model using the validation set
        """
        print('Loading validation X')
        x = self._data.validation().x().load()
        print('Loading validation Y')
        y = self._data.validation().y().load()
        return self.evaluate(x, y)

    def test(self) -> Evaluation:
        """
        Evaluates the model using the test set
        """
        print('Loading test X')
        x = self._data.test().x().load()
        print('Loading test Y')
        y = self._data.test().y().load()
        return self.evaluate(x, y)

    def predict(self, images: List[Image]) -> Predictions:
        """
        Predicts using the trained model
        """
        x = asarray(images)
        seq = Sequence1(x, x, 10)
        print('Predicting....')
        results = self._kmodel.predict_generator(generator=seq, verbose=1)
        print('Prediction finished')
        return self._data.translate_predictions(x, results).save_as_list(self._names.predictions())

    def create(self) -> None:
        """
        Creates and saves the model file and other training state files.
        Initial settings are found here.
        """
        # Blank model and training state
        print('Compiling architecture')
        kmodel = self._architecture.compile()
        mcp = ModelCheckpoint2(
            self._names.latest.mcp(),
            self._names.best.mcp(),
        )
        lr = ReduceLROnPlateauPickle(ReduceLROnPlateau(
            patience=self._patience,
            verbose=1,
        ))
        epoch = EpochPickle(0)

        # Latest snapshot
        print('Making %s' % self._names.latest.dirname)
        mkdirs(self._names.latest.dirname)
        print('Saving to %s' % self._names.latest.weights())
        kmodel.save_weights(self._names.latest.weights())
        print('Saving to %s' % self._names.latest.mcp())
        mcp.save(self._names.latest.mcp())
        print('Saving to %s' % self._names.latest.lr())
        lr.save(self._names.latest.lr())
        print('Saving to %s' % self._names.latest.epoch())
        epoch.save(self._names.latest.epoch())

        # Best snapshot
        print('Making %s' % self._names.best.dirname)
        mkdirs(self._names.best.dirname)
        print('Saving to %s' % self._names.best.weights())
        kmodel.save_weights(self._names.best.weights())
        print('Saving to %s' % self._names.best.mcp())
        mcp.save(self._names.best.mcp())
        print('Saving to %s' % self._names.best.lr())
        lr.save(self._names.best.lr())
        print('Saving to %s' % self._names.best.epoch())
        epoch.save(self._names.best.epoch())

    def is_saved(self) -> bool:
        """
        Returns true if all the saved files exist.
        """
        if not isfile(self._names.latest.weights()):
            print('Missing %s' % self._names.latest.weights())
            return False
        if not isfile(self._names.latest.mcp()):
            print('Missing %s' % self._names.latest.mcp())
            return False
        if not isfile(self._names.latest.lr()):
            print('Missing %s' % self._names.latest.lr())
            return False
        if not isfile(self._names.latest.epoch()):
            print('Missing %s' % self._names.latest.epoch())
            return False
        if not isfile(self._names.best.weights()):
            print('Missing %s' % self._names.best.weights())
            return False
        if not isfile(self._names.best.mcp()):
            print('Missing %s' % self._names.best.mcp())
            return False
        if not isfile(self._names.best.lr()):
            print('Missing %s' % self._names.best.lr())
            return False
        if not isfile(self._names.best.epoch()):
            print('Missing %s' % self._names.best.epoch())
            return False
        return True

    def load(self, best_snapshot: bool = False) -> None:
        """
        Loads the training model file and other training state files.
        """
        self._is_best = best_snapshot
        print('Compiling architecture')
        self._kmodel = self._architecture.compile()
        if best_snapshot:
            print('Loading best snapshot')
            self._kmodel.load_weights(self._names.best.weights())
        else:
            print('Loading weights')
            self._kmodel.load_weights(self._names.latest.weights())

    def delete(self) -> None:
        """
        Deletes the model file and other training state files.
        """
        raise NotImplementedError


class ModelSplit(object):
    """
    """

    def __init__(
        self,
        architecture: CompiledArchitecture,
        data: DataSetSplit,
        epochs: int,
        patience: int
    ) -> None:
        self._architecture = architecture
        self._data = data
        self._epochs = epochs
        self._patience = patience

    def train(self) -> None:
        """
        Trains the model
        """
        kadapter = KerasAdapter(
            self._architecture,
            self._data,
            self._epochs,
            self._patience,
        )
        if not kadapter.is_saved():
            kadapter.create()
        kadapter.load()
        kadapter.train()

    def evaluate_training_set(self) -> Evaluation:
        """
        Measures the effectiveness of the model against the training set
        """
        kadapter = KerasAdapter(
            self._architecture,
            self._data,
            self._epochs,
            self._patience,
        )
        if not kadapter.is_saved():
            kadapter.create()
        kadapter.load()
        return kadapter.evaluate_training_set()

    def validate(self) -> Evaluation:
        """
        Measures the effectiveness of the model against the validation set
        """
        kadapter = KerasAdapter(
            self._architecture,
            self._data,
            self._epochs,
            self._patience,
        )
        if not kadapter.is_saved():
            kadapter.create()
        kadapter.load()
        return kadapter.validate()

    def test(self) -> Evaluation:
        """
        Measures the effectiveness of the model against the test set
        """
        kadapter = KerasAdapter(
            self._architecture,
            self._data,
            self._epochs,
            self._patience,
        )
        if not kadapter.is_saved():
            kadapter.create()
        kadapter.load()
        return kadapter.test()

    def predict(self, images: List[Url]) -> Predictions:
        """
        Takes the input and returns an output
        """
        kadapter = KerasAdapter(
            self._architecture,
            self._data,
            self._epochs,
            self._patience,
        )
        if not kadapter.is_saved():
            kadapter.create()
        kadapter.load()
        return kadapter.predict(images)


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
        Gets a specific split
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
        Starts or continues training the model
        """
        for i in range(self._dataset.splits()):
            print("Split %d / %d" % (i + 1, self._dataset.splits()))
            self.split(i).train()

    def evaluate_training_set(self) -> Evaluation:
        """
        Evaluates the model against the data's training set
        """
        evaluations: List[Evaluation] = list()
        for i in range(self._dataset.splits()):
            print("Split %d / %d" % (i + 1, self._dataset.splits()))
            evaluations.append(self.split(i).evaluate_training_set())
        return Evaluation.mean(evaluations)

    def validate(self) -> Evaluation:
        """
        Evaluates the model against the data's validation set
        """
        evaluations: List[Evaluation] = list()
        for i in range(self._dataset.splits()):
            print("Split %d / %d" % (i + 1, self._dataset.splits()))
            evaluations.append(self.split(i).validate())
        return Evaluation.mean(evaluations)

    def test(self) -> Evaluation:
        """
        Evaluates the model against the data's test set
        """
        evaluations: List[Evaluation] = list()
        for i in range(self._dataset.splits()):
            print("Split %d / %d" % (i + 1, self._dataset.splits()))
            evaluations.append(self.split(i).test())
        return Evaluation.mean(evaluations)
