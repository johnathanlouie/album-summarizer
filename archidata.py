from os.path import isfile

from keras.callbacks import CSVLogger, ModelCheckpoint, ReduceLROnPlateau
from keras.models import load_model

from dataholder import DataHolder
from dataset import DataSet, DataSetSplit
from jl import ListFile
from kerashelper import PickleCheckpoint, Sequence1, TerminateOnDemand
from model import Architecture


class ArchitectureSplit(object):
    """
    Produced by the ArchitectureSet class.
    A combination of the ArchitectureSet class and the DataSetSplit class.
    Trains, validates, tests, and predicts.
    """

    def __init__(self, architecture: Architecture, split: DataSetSplit) -> None:
        self._architecture = architecture
        self._split = split
        self._continue()

    def name(self) -> str:
        """
        Returns the unique identifier of this combination of architecture, dataset, and compile options.
        """
        return "%s.%s.%d" % (self._architecture.name(), self._split.name, self._split.split)

    def _model_url(self) -> str:
        """
        Returns the URL of the model save file.
        """
        return "gen/%s.h5" % (self.name())

    def _best_model_url(self) -> str:
        """
        Returns the URL of the model save file.
        """
        return "gen/%s.best.h5" % (self.name())

    def train(self) -> None:
        """
        Trains the model.
        """
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
        csv = CSVLogger('gen/training.csv', append=True)
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
        results_file = 'gen/pred.txt'
        ListFile(results_file).write(results)
        print('Saved predictions to %s' % (results_file))
        return results

    def _create(self) -> None:
        """
        Creates and saves the model file and other training state files.
        Initial settings are found here.
        """
        print('No saved files found.')
        print('Creating new model.')
        self._architecture.compile().save(self._model_url())
        print('Saved model.')
        print('Creating new training status.')
        mcp = ModelCheckpoint(self._model_url(), verbose=1)
        mcpb = ModelCheckpoint(self._best_model_url(), verbose=1, save_best_only=True)
        lr = ReduceLROnPlateau(patience=5, verbose=1)
        dh_url = DataHolder.url(self.name())
        DataHolder(dh_url, 0, 1000, lr, mcp, mcpb).save()
        print('Saved DataHolder.')
        return

    def _load(self) -> None:
        """
        Loads the model file and other training state files.
        """
        self._model = load_model(self._model_url(), self._architecture.custom())
        dh_url = DataHolder.url(self.name())
        dh = DataHolder.load(dh_url)
        self._current_epoch = dh.current_epoch
        self._max_epoch = dh.total_epoch
        self._lr = dh.get_lr()
        self._mcp = dh.get_mcp()
        self._mcpb = dh.get_mcpb()
        self._pcp = PickleCheckpoint(self._mcp, self._mcpb, self._lr, self.name())
        return

    def _delete(self) -> None:
        """
        Deletes the model file and other training state files.
        Not implemented since _load overwrites.
        """
        return

    def _continue(self) -> None:
        """
        Loads the saved files if they exist.
        Create and load them if they do not exist.
        """
        if not isfile(self._model_url()):
            self._create()
        self._load()
        return

    def reset(self) -> None:
        """
        Starts the training process from the beginning.
        """
        print('Resetting training data.')
        self._delete()
        self._create()
        self._load()
        return


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
