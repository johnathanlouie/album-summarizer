class ModelName:
    def __init__(self, architecture, version, loss, optimizer):
        self.architecture = architecture
        self.version = version
        self.loss = loss
        self.optimizer = optimizer
        return

    def __str__(self):
        return '%s.%d.%s.%s' % (self.architecture, self.version, self.loss, self.optimizer)

    def __add__(self, other):
        return str(self) + other

    def __radd__(self, other):
        return other + str(self)


class DataModelName:
    def __init__(self, model, dataset):
        self._model_name = model
        self._ds = dataset
        return

    def pickle(self):
        return 'gen/%s.%s.p' % (self._model_name, self._ds)

    def model(self):
        return 'gen/%s.%s.h5' % (self._model_name, self._ds)

    def training(self):
        return 'gen/%s.%s.train.h5' % (self._model_name, self._ds)
