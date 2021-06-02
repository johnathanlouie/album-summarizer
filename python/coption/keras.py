from rasek.architecture import CompileOption
from rasek.modelbuilder import ModelBuilder


"""Loss functions"""
ModelBuilder.loss(CompileOption('mse', 'mean_squared_error'))
ModelBuilder.loss(CompileOption('mae', 'mean_absolute_error'))
ModelBuilder.loss(CompileOption('mape', 'mean_absolute_percentage_error'))
ModelBuilder.loss(CompileOption('msle', 'mean_squared_logarithmic_error'))
ModelBuilder.loss(CompileOption('shinge', 'squared_hinge'))
ModelBuilder.loss(CompileOption('hinge', 'hinge'))
ModelBuilder.loss(CompileOption('chinge', 'categorical_hinge'))
ModelBuilder.loss(CompileOption('logcosh', 'logcosh'))
ModelBuilder.loss(CompileOption('cce', 'categorical_crossentropy'))
ModelBuilder.loss(CompileOption('scce', 'sparse_categorical_crossentropy'))
ModelBuilder.loss(CompileOption('bce', 'binary_crossentropy'))
ModelBuilder.loss(CompileOption('kld', 'kullback_leibler_divergence'))
ModelBuilder.loss(CompileOption('poisson', 'poisson'))
ModelBuilder.loss(CompileOption('cosprox', 'cosine_proximity'))


"""Optimizers"""
ModelBuilder.optimizer(CompileOption('sgd', 'sgd'))
ModelBuilder.optimizer(CompileOption('rmsp', 'RMSprop'))
ModelBuilder.optimizer(CompileOption('adag', 'Adagrad'))
ModelBuilder.optimizer(CompileOption('adad', 'Adadelta'))
ModelBuilder.optimizer(CompileOption('adam', 'Adam'))
ModelBuilder.optimizer(CompileOption('adamax', 'Adamax'))
ModelBuilder.optimizer(CompileOption('nadam', 'Nadam'))


"""Performance metrics"""
ModelBuilder.metric(CompileOption('acc', 'accuracy'))
ModelBuilder.metric(CompileOption('bacc', 'binary_accuracy'))
ModelBuilder.metric(CompileOption('cacc', 'categorical_accuracy'))
ModelBuilder.metric(CompileOption('scacc', 'sparse_categorical_accuracy'))
ModelBuilder.metric(CompileOption('tkcacc', 'top_k_categorical_accuracy'))
ModelBuilder.metric(CompileOption('stkcacc', 'sparse_top_k_categorical_accuracy'))
