import gc
import json
import os
from enum import Enum, auto
from os.path import isfile
from typing import Any, Dict, List, Union

import dill
import keras.models
import tensorflow as tf
from keras.backend import clear_session
from keras.callbacks import CSVLogger, ReduceLROnPlateau
from numpy import asarray, ndarray

from core.architecture import (Architecture, CompiledArchitecture,
                               CompiledArchitectureName, CompileOption)
from core.dataset import DataSet, DataSetSplit, DataSetSplitName
from core.epoch import EpochObserver, EpochPickle
from core.jl import ListFile, Resolution, hash_images, mkdirname, mkdirs
from core.kerashelper import (CompletionStatusObserver, ModelCheckpoint2,
                              ModelCheckpoint2Observer, ModelCheckpoint2Pickle,
                              NanInfStatusObserver, SaveKmodelObserver,
                              Sequence1, TerminateOnDemand,
                              TerminateOnNanInfObserver, TrainingStatus,
                              TrainingStatusData)
from core.reducelr import ReduceLROnPlateauObserver, ReduceLROnPlateauPickle
from core.typing2 import Image, Url


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

    def early(self) -> Url:
        return '%s/early.dill' % self.dirname

    def list_all(self) -> List[Url]:
        return [
            self.weights(),
            self.mcp(),
            self.lr(),
            self.epoch(),
            self.early(),
        ]


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

    def model_id(self) -> Url:
        return "%s-%s-%s-%s/%d-%d/%d" % (self._architecture, self._dataset, self._loss, self._optimizer, self._epochs, self._patience, self._split)

    def dirname(self) -> Url:
        """
        Returns the path up to each file.
        """
        return "models/%s" % self.model_id()

    def log(self) -> Url:
        """
        Returns the URL of the training log.
        """
        return "%s/log.csv" % self.dirname()

    def status(self) -> Url:
        return '%s/status.txt' % self.dirname()

    def list_all(self) -> List[Url]:
        return [
            self.status(),
            self.log(),
        ] + self.best.list_all() + self.latest.list_all()

    def prediction_cache(self, images: List[Url]) -> Url:
        return "cache/%s/%s/prediction.dill" % (hash_images(images), self.model_id())

    def evaluation_cache(self) -> Url:
        return "cache/%s" % self.model_id()

    def training_set_evaluation_cache(self) -> Url:
        return "%s/training.dill" % self.evaluation_cache()

    def validation_set_evaluation_cache(self) -> Url:
        return "%s/validation.dill" % self.evaluation_cache()

    def test_set_evaluation_cache(self) -> Url:
        return "%s/test.dill" % self.evaluation_cache()


class Evaluation(dict):
    """
    Dictionary that holds loss/metric names as keys and scalar values.
    """

    def __init__(self):
        super().__init__()
        self['splits']: List[Dict[str, float]] = list()
        self['mean'] = dict()

    def append(self, resultx: Dict[str, float]) -> None:
        self['splits'].append(resultx)
        # New mean
        mean = dict()
        for e in self['splits']:
            for k, v in e.items():
                if k not in mean:
                    mean[k] = 0.0
                mean[k] += v
        for k, v in mean:
            mean[k] = v / len(self['splits'])
        self['mean'] = mean

    def mean(self) -> Dict[str, float]:
        return self['mean'].copy()

    def split(self, split: int) -> Dict[str, float]:
        return self['splits'][split].copy()

    def save(self, url: Url, verbose: bool = True) -> None:
        if verbose:
            print('SAVING: %s' % url)
        with open(url, 'w') as f:
            json.dump(self, f)


class PredictionY(object):
    def __init__(self, predicted: List[Any], truth: List[Any]):
        self.predicted = predicted
        self.truth = truth


class Prediction(object):
    """
    """

    def __init__(self, x: List[Any], predicted_y: List[Any], true_y: List[Any] = []) -> None:
        self.x: List[Any] = x
        self.y = PredictionY(predicted_y, true_y)

    def get_dict(self) -> Dict[str, Union[List[Any], Dict[str, List[Any]]]]:
        return {
            'x': self.x,
            'y': {
                'predicted': self.y.predicted,
                'truth': self.y.truth,
            },
        }

    def save_as_list(self, url: Url) -> None:
        """
        Saves to a text file in human readable format.
        """
        ListFile(url).write(self.get_dict())

    def save_json(self, url: Url) -> None:
        json.dump(self.get_dict(), open(url, 'w'))


class TrainingIncompleteException(RuntimeError):
    pass


class ModelStateMissingError(FileNotFoundError):
    pass


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
        """
        # Arguments
        epochs:
        - 0 for automatically stopping when training yields no improvements for a specified number of epochs
        - any positive integer for a set number of epochs
        """
        self._architecture: CompiledArchitecture = architecture
        self._data: DataSetSplit = data
        self._names: ModelSplitName = ModelSplitName(
            architecture.name(),
            data.name(),
            epochs,
            patience,
        )
        self._kmodel: keras.models.Model = None
        self._total_epochs: int = epochs
        self._patience: int = patience
        self._is_best: bool = False
        self._status: TrainingStatusData = None
        self._res = Resolution(190)
        self._batch = 10

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        self.close()
        return False

    def status(self) -> TrainingStatus:
        if self._status is None:
            self._status = TrainingStatusData.load(self._names.status())
        return self._status.status

    def is_complete(self) -> bool:
        if self._status is None:
            self._status = TrainingStatusData.load(self._names.status())
        return self._status.is_complete()

    def has_error(self) -> bool:
        if self._status is None:
            self._status = TrainingStatusData.load(self._names.status())
        return self._status.has_error()

    def train(self) -> TrainingStatus:
        """
        Trains the model
        """
        if self.is_complete():
            return TrainingStatus.COMPLETE

        # Training state
        term = TerminateOnDemand()
        term.clear()
        log = CSVLogger(self._names.log(), append=True)
        if not self._is_best:
            current_epoch: int = EpochPickle.load(self._names.latest.epoch()).get()
            lr: ReduceLROnPlateau = ReduceLROnPlateauPickle.load(self._names.latest.lr()).get()
            mcp = ModelCheckpoint2Pickle.load(self._names.latest.mcp()).get()
        else:
            current_epoch: int = EpochPickle.load(self._names.best.epoch()).get()
            lr: ReduceLROnPlateau = ReduceLROnPlateauPickle.load(self._names.best.lr()).get()
            mcp = ModelCheckpoint2Pickle.load(self._names.best.mcp()).get()

        mcp.on_period(SaveKmodelObserver(self._names.latest.weights()))
        mcp.on_period(ReduceLROnPlateauObserver(self._names.latest.lr(), lr))
        mcp.on_period(EpochObserver(self._names.latest.epoch()))
        mcp.on_period(ModelCheckpoint2Observer(self._names.latest.mcp(), mcp))
        mcp.on_improvement(SaveKmodelObserver(self._names.best.weights()))
        mcp.on_improvement(ReduceLROnPlateauObserver(self._names.best.lr(), lr))
        mcp.on_improvement(EpochObserver(self._names.best.epoch()))
        mcp.on_improvement(ModelCheckpoint2Observer(self._names.best.mcp(), mcp))
        mcp.on_completion(SaveKmodelObserver(self._names.latest.weights()))
        mcp.on_completion(ReduceLROnPlateauObserver(self._names.latest.lr(), lr))
        mcp.on_completion(EpochObserver(self._names.latest.epoch()))
        mcp.on_completion(ModelCheckpoint2Observer(self._names.latest.mcp(), mcp))
        mcp.on_completion(CompletionStatusObserver(self._status))
        mcp.on_nan_inf(NanInfStatusObserver(self._status))
        mcp.on_nan_inf(TerminateOnNanInfObserver())

        callbacks = list()
        callbacks.append(lr)
        callbacks.append(log)
        callbacks.append(mcp)
        callbacks.append(term)

        total_epochs = self._total_epochs
        if self._total_epochs == 0:
            total_epochs = 2**64

        # Training set
        x1 = self._data.train().x().load()
        y1 = self._data.train().y().load()
        x2 = self._data.validation().x().load()
        y2 = self._data.validation().y().load()
        # print('Training sequence')
        seq1 = Sequence1(x1, y1, self._res, self._batch)
        # print('Validation sequence')
        seq2 = Sequence1(x2, y2, self._res, self._batch)

        # Training
        print('TRAINING: %s\n' % self._names.dirname())
        try:
            self._kmodel.fit_generator(
                generator=seq1,
                epochs=total_epochs,
                verbose=1,
                validation_data=seq2,
                shuffle=False,
                initial_epoch=current_epoch,
                callbacks=callbacks,
            )
        except tf.errors.ResourceExhaustedError:
            print('\nTraining resource exhaustion: %s' % self._names.dirname())
            self._status.status = TrainingStatus.RESOURCE
            self._status.save()
            return self._status.status
        except ValueError as e:
            print('\nIncompatible settings: %s\n%s' % (self._names.dirname(), e))
            self._status.status = TrainingStatus.BAD_SETTINGS
            self._status.save()
            return self._status.status

        if self._status.is_complete():
            print('Training completed: %s' % self._names.dirname())
        return self._status.status

    def evaluate(self, x: ndarray, y: ndarray) -> Dict[str, float]:
        """
        Evaluates the model using the given x and y.
        Returns a list of metrics.
        """
        seq = Sequence1(x, y, self._res, self._batch)
        results: List[float] = self._kmodel.evaluate_generator(
            generator=seq,
            verbose=1,
        )
        return {metric: scalar for metric, scalar in zip(self._kmodel.metrics_names, results)}

    def evaluate_training_set(self) -> Dict[str, float]:
        """
        Evaluates the model using the training set
        """
        filepath = self._names.training_set_evaluation_cache()
        mkdirname(filepath)
        if os.path.exists(filepath):
            print("LOADING: %s" % filepath)
            with open(filepath, 'rb') as f:
                return dill.load(f)
        x = self._data.train().x().load()
        y = self._data.train().y().load()
        results = self.evaluate(x, y)
        print("SAVING: %s" % filepath)
        with open(filepath, 'wb') as f:
            dill.dump(results, f)
        return results

    def evaluate_validation_set(self) -> Dict[str, float]:
        """
        Evaluates the model using the validation set
        """
        filepath = self._names.validation_set_evaluation_cache()
        mkdirname(filepath)
        if os.path.exists(filepath):
            print("LOADING: %s" % filepath)
            with open(filepath, 'rb') as f:
                return dill.load(f)
        x = self._data.validation().x().load()
        y = self._data.validation().y().load()
        results = self.evaluate(x, y)
        print("SAVING: %s" % filepath)
        with open(filepath, 'wb') as f:
            dill.dump(results, f)
        return results

    def evaluate_test_set(self) -> Dict[str, float]:
        """
        Evaluates the model using the test set
        """
        filepath = self._names.test_set_evaluation_cache()
        mkdirname(filepath)
        if os.path.exists(filepath):
            print("LOADING: %s" % filepath)
            with open(filepath, 'rb') as f:
                return dill.load(f)
        x = self._data.test().x().load()
        y = self._data.test().y().load()
        results = self.evaluate(x, y)
        print("SAVING: %s" % filepath)
        with open(filepath, 'wb') as f:
            dill.dump(results, f)
        return results

    def predict(self, images: List[Url], simple: bool) -> Prediction:
        """
        Predicts using the trained model
        """
        filepath = self._names.prediction_cache(images)
        mkdirname(filepath)
        if os.path.exists(filepath):
            print("LOADING: %s" % filepath)
            with open(filepath, 'rb') as f:
                return dill.load(f)
        x = asarray(images)
        seq = Sequence1(x, x, self._res, self._batch)
        predictions: ndarray = self._kmodel.predict_generator(generator=seq, verbose=1)
        if simple:
            if predictions.ndim == 2 and predictions.shape[1] == 1:
                predictions = predictions.flatten()
        y = predictions.tolist()
        if simple:
            y = self._data.translate_predictions(y)
        results = Prediction(images, y)
        print("SAVING: %s" % filepath)
        with open(filepath, 'wb') as f:
            dill.dump(results, f)
        return results

    def predict_training_set(self, simple: bool) -> Prediction:
        x = self._data.train().x().load().tolist()
        y = self._data.train().y().load().tolist()
        prediction = self.predict(x, simple)
        prediction.y.truth = y
        return prediction

    def predict_validation_set(self, simple: bool) -> Prediction:
        x = self._data.validation().x().load().tolist()
        y = self._data.validation().y().load().tolist()
        prediction = self.predict(x, simple)
        prediction.y.truth = y
        return prediction

    def predict_test_set(self, simple: bool) -> Prediction:
        x = self._data.test().x().load().tolist()
        y = self._data.test().y().load().tolist()
        prediction = self.predict(x, simple)
        prediction.y.truth = y
        return prediction

    def create(self) -> None:
        """
        Creates and saves the model file and other training state files.
        Initial settings are found here.
        """
        try:
            # Training status
            mkdirs(self._names.dirname())
            if self._status == None:
                self._status = TrainingStatusData.load(self._names.status())
            self._status.status = TrainingStatus.TRAINING
            self._status.save()

            # Blank model and training state
            self._kmodel = self._architecture.compile(self._res, self._data.classes)
            if self._total_epochs == 0:
                mcp = ModelCheckpoint2Pickle(ModelCheckpoint2(patience=10))
            else:
                mcp = ModelCheckpoint2Pickle(ModelCheckpoint2(total_epochs=self._total_epochs))
            lr = ReduceLROnPlateauPickle(ReduceLROnPlateau(
                patience=self._patience,
                verbose=1,
            ))
            epoch = EpochPickle(0)

            # Latest snapshot
            mkdirs(self._names.latest.dirname)
            print('SAVING: %s' % self._names.latest.weights())
            self._kmodel.save_weights(self._names.latest.weights())
            mcp.save(self._names.latest.mcp())
            lr.save(self._names.latest.lr())
            epoch.save(self._names.latest.epoch())

            # Best snapshot
            mkdirs(self._names.best.dirname)
            print('SAVING: %s' % self._names.best.weights())
            self._kmodel.save_weights(self._names.best.weights())
            mcp.save(self._names.best.mcp())
            lr.save(self._names.best.lr())
            epoch.save(self._names.best.epoch())
        except tf.errors.ResourceExhaustedError:
            print('\nTraining resource exhaustion: %s' % self._names.dirname())
            self._status.status = TrainingStatus.RESOURCE2
            self._status.save()

    def is_saved(self) -> bool:
        """
        Returns true if all the saved files exist.
        """
        files = [
            self._names.status(),
            self._names.latest.weights(),
            self._names.latest.mcp(),
            self._names.latest.lr(),
            self._names.latest.epoch(),
            self._names.best.weights(),
            self._names.best.mcp(),
            self._names.best.lr(),
            self._names.best.epoch(),
        ]
        for filename in files:
            if not isfile(filename):
                print('MISSING: %s' % filename)
                return False
        return True

    def load(self, best_snapshot: bool = False) -> None:
        """
        Loads the training model file and other training state files.
        """
        try:
            print()
            if self._status == None:
                self._status = TrainingStatusData.load(self._names.status())
            self._is_best = best_snapshot
            # print('Compiling architecture')
            self._kmodel = self._architecture.compile(self._res, self._data.classes)
            if best_snapshot:
                print('LOADING: %s' % self._names.best.weights())
                self._kmodel.load_weights(self._names.best.weights())
            else:
                print('LOADING: %s' % self._names.latest.weights())
                self._kmodel.load_weights(self._names.latest.weights())
        except tf.errors.ResourceExhaustedError:
            print('\nTraining resource exhaustion: %s' % self._names.dirname())
            self._status.status = TrainingStatus.RESOURCE2
            self._status.save()

    def delete(self, keep_history: bool) -> None:
        """
        Deletes the model file and other training state files.
        """
        if keep_history:
            files = self._names.best.list_all() + self._names.latest.list_all()
        else:
            files = self._names.list_all()
        for f in files:
            try:
                print("DELETING: %s" % f)
                os.remove(f)
            except:
                pass
        if keep_history:
            try:
                print("DELETING: %s" % self._names.best.dirname())
                os.rmdir(self._names.best.dirname())
            except:
                pass
            try:
                print("DELETING: %s" % self._names.latest.dirname())
                os.rmdir(self._names.latest.dirname())
            except:
                pass
        else:
            try:
                print("DELETING: %s" % self._names.dirname())
                os.rmdir(self._names.dirname())
            except:
                pass

    def close(self) -> None:
        """
        Clears Keras model from memory.
        """
        self._kmodel = None
        clear_session()
        gc.collect()

    def summary(self) -> None:
        return self._architecture.summary(self._res, self._data.classes)


class ModelSplit(object):
    """
    """

    def __init__(
        self,
        architecture: CompiledArchitecture,
        data: DataSetSplit,
        epochs: int,
        patience: int,
    ) -> None:
        self._architecture = architecture
        self._data = data
        self._epochs = epochs
        self._patience = patience

    def status(self) -> TrainingStatus:
        with KerasAdapter(
            self._architecture,
            self._data,
            self._epochs,
            self._patience,
        ) as kadapter:
            return kadapter.status()

    def is_complete(self) -> bool:
        with KerasAdapter(
            self._architecture,
            self._data,
            self._epochs,
            self._patience,
        ) as kadapter:
            return kadapter.is_complete()

    def has_error(self) -> bool:
        with KerasAdapter(
            self._architecture,
            self._data,
            self._epochs,
            self._patience,
        ) as kadapter:
            return kadapter.has_error()

    def train(self) -> TrainingStatus:
        """
        Trains the model
        """
        with KerasAdapter(
            self._architecture,
            self._data,
            self._epochs,
            self._patience,
        ) as kadapter:
            if self.is_complete():
                return TrainingStatus.COMPLETE
            if not kadapter.is_saved():
                kadapter.create()
            else:
                kadapter.load()
            return kadapter.train()

    def evaluate_training_set(self) -> Dict[str, float]:
        """
        Measures the effectiveness of the model against the training set
        """
        if not self.is_complete():
            raise TrainingIncompleteException()
        with KerasAdapter(
            self._architecture,
            self._data,
            self._epochs,
            self._patience,
        ) as kadapter:
            if not kadapter.is_saved():
                raise ModelStateMissingError()
            kadapter.load()
            return kadapter.evaluate_training_set()

    def evaluate_validation_set(self) -> Dict[str, float]:
        """
        Measures the effectiveness of the model against the validation set
        """
        if not self.is_complete():
            raise TrainingIncompleteException()
        with KerasAdapter(
            self._architecture,
            self._data,
            self._epochs,
            self._patience,
        ) as kadapter:
            if not kadapter.is_saved():
                raise ModelStateMissingError()
            kadapter.load()
            return kadapter.evaluate_validation_set()

    def evaluate_test_set(self) -> Dict[str, float]:
        """
        Measures the effectiveness of the model against the test set
        """
        if not self.is_complete():
            raise TrainingIncompleteException()
        with KerasAdapter(
            self._architecture,
            self._data,
            self._epochs,
            self._patience,
        ) as kadapter:
            if not kadapter.is_saved():
                raise ModelStateMissingError()
            kadapter.load()
            return kadapter.evaluate_test_set()

    def predict(self, images: List[Url], simple: bool) -> Prediction:
        """
        Takes the input and returns an output
        """
        if not self.is_complete():
            raise TrainingIncompleteException()
        with KerasAdapter(
            self._architecture,
            self._data,
            self._epochs,
            self._patience,
        ) as kadapter:
            if not kadapter.is_saved():
                raise ModelStateMissingError()
            kadapter.load()
            return kadapter.predict(images, simple)

    def predict_training_set(self, simple: bool) -> Prediction:
        """
        Takes the input and returns an output
        """
        if not self.is_complete():
            raise TrainingIncompleteException()
        with KerasAdapter(
            self._architecture,
            self._data,
            self._epochs,
            self._patience,
        ) as kadapter:
            if not kadapter.is_saved():
                raise ModelStateMissingError()
            kadapter.load()
            return kadapter.predict_training_set(simple)

    def predict_validation_set(self, simple: bool) -> Prediction:
        """
        Takes the input and returns an output
        """
        if not self.is_complete():
            raise TrainingIncompleteException()
        with KerasAdapter(
            self._architecture,
            self._data,
            self._epochs,
            self._patience,
        ) as kadapter:
            if not kadapter.is_saved():
                raise ModelStateMissingError()
            kadapter.load()
            return kadapter.predict_validation_set(simple)

    def predict_test_set(self, simple: bool) -> Prediction:
        """
        Takes the input and returns an output
        """
        if not self.is_complete():
            raise TrainingIncompleteException()
        with KerasAdapter(
            self._architecture,
            self._data,
            self._epochs,
            self._patience,
        ) as kadapter:
            if not kadapter.is_saved():
                raise ModelStateMissingError()
            kadapter.load()
            return kadapter.predict_test_set(simple)

    def delete(self, keep_history: bool) -> None:
        with KerasAdapter(
            self._architecture,
            self._data,
            self._epochs,
            self._patience,
        ) as kadapter:
            kadapter.delete(keep_history)

    def summary(self) -> None:
        with KerasAdapter(
            self._architecture,
            self._data,
            self._epochs,
            self._patience,
        ) as kadapter:
            return kadapter.summary()

    def auto_train(self) -> None:
        with KerasAdapter(
            self._architecture,
            self._data,
            self._epochs,
            self._patience,
        ) as kadapter:
            if not kadapter.has_error() and not kadapter.is_complete():
                if not kadapter.is_saved():
                    kadapter.create()
                else:
                    kadapter.load()
                kadapter.train()
            if kadapter.has_error():
                kadapter.delete(keep_history=True)
            elif kadapter.is_complete():
                kadapter.evaluate_training_set()
                kadapter.evaluate_validation_set()
                kadapter.evaluate_test_set()


class BadModelSettings(ValueError):
    pass


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
        epochs: int,
        patience: int,
    ) -> None:
        self._architecture: CompiledArchitecture = CompiledArchitecture(
            architecture,
            loss,
            optimizer,
            metrics,
        )
        self._dataset: DataSet = dataset
        if architecture.OUTPUT_TYPE != dataset.OUTPUT_TYPE:
            raise BadModelSettings('Architecture and data set are not compatible')
        self._epochs: int = epochs
        self._patience: int = patience

    def status(self) -> TrainingStatus:
        for i in range(self._dataset.splits()):
            status = self.split(i).status()
            if status != TrainingStatus.COMPLETE:
                return status
        return TrainingStatus.COMPLETE

    def is_complete(self) -> bool:
        for i in range(self._dataset.splits()):
            if not self.split(i).is_complete():
                return False
        return True

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

    def train(self) -> TrainingStatus:
        """
        Starts or continues training the model
        """
        for i in range(self._dataset.splits()):
            # print("Split %d / %d" % (i + 1, self._dataset.splits()))
            status = self.split(i).train()
            if status != TrainingStatus.COMPLETE:
                return status
        return TrainingStatus.COMPLETE

    def evaluate_training_set(self) -> Evaluation:
        """
        Evaluates the model against the data's training set
        """
        evaluation = Evaluation()
        for i in range(self._dataset.splits()):
            print("Split %d / %d" % (i + 1, self._dataset.splits()))
            evaluation.append(self.split(i).evaluate_training_set())
        return evaluation

    def evaluate_validation_set(self) -> Evaluation:
        """
        Evaluates the model against the data's validation set
        """
        evaluation = Evaluation()
        for i in range(self._dataset.splits()):
            print("Split %d / %d" % (i + 1, self._dataset.splits()))
            evaluation.append(self.split(i).evaluate_validation_set())
        return evaluation

    def evaluate_test_set(self) -> Evaluation:
        """
        Evaluates the model against the data's test set
        """
        evaluation = Evaluation()
        for i in range(self._dataset.splits()):
            print("Split %d / %d" % (i + 1, self._dataset.splits()))
            evaluation.append(self.split(i).evaluate_test_set())
        return evaluation

    def summary(self) -> None:
        """
        """
        return self.split(0).summary()
