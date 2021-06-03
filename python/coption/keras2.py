from core.architecture import CompileOption
from core.modelbuilder import ModelBuilder

from keras.optimizers import SGD


ModelBuilder.optimizer(CompileOption('sgd1', SGD(lr=0.01, momentum=0.9, decay=0.0005, nesterov=True)))
