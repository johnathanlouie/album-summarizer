import json
import os.path
from copy import deepcopy
from traceback import print_exc
from typing import Any, Dict, List

import flask

import aaa
import addon
from core.cluster import (ClusterRegistry, ClusterRegistryNameError,
                          ClusterResults, ClusterStrategy)
from core.jl import ImageDirectory, function_signature
from core.kerashelper import TrainingStatus
from core.model import (BadModelSettings, ModelSplit, ModelStateMissingError,
                        TrainingIncompleteException)
from core.modelbuilder import ModelBuilder
from core.typing2 import Url


class ClusterRank(object):
    """
    A ranking system that picks the best out of each cluster.
    """

    def __init__(self, clusters: ClusterResults, rates: List[float]) -> None:
        self._results = [[] for _ in range(clusters.k())]
        for clusterId, rate, path in zip(clusters.labels(), rates, clusters.get_all_urls()):
            self._results[clusterId].append({
                'path': path,
                'rating': rate,
                'cluster': clusterId,
            })
        for cluster in self._results:
            cluster.sort(key=lambda x: x['rating'], reverse=True)

    def save_results(self, dst: Url) -> None:
        """
        Saves the results to a JSON file.
        """
        with open(dst, 'w', encoding='utf8') as f:
            json.dump(self._results, f, indent=4)

    def jsonable(self) -> List[List[Dict[str, Any]]]:
        return deepcopy(self._results)


class Settings(object):
    """
    """

    FILENAME = 'out/settings.json'

    def __init__(self):
        self.architecture = 'smi13a'
        self.dataset = 'ccrc'
        self.loss = 'bce'
        self.optimizer = 'sgd'
        self.metrics = 'acc'
        self.epochs = 0
        self.patience = 3
        self.split = 0
        self.cluster = 'sift'

    def exists(self) -> bool:
        return os.path.isfile(self.FILENAME)

    def save(self) -> None:
        with open(self.FILENAME, 'w') as f:
            x = {
                'architecture': self.architecture,
                'dataset': self.dataset,
                'loss': self.loss,
                'optimizer': self.optimizer,
                'metrics': self.metrics,
                'epochs': self.epochs,
                'patience': self.patience,
                'split': self.split,
                'cluster': self.cluster,
            }
            json.dump(x, f)

    def load(self) -> None:
        with open(self.FILENAME) as f:
            x = json.load(f)
            self.architecture = x['architecture']
            self.dataset = x['dataset']
            self.loss = x['loss']
            self.optimizer = x['optimizer']
            self.metrics = x['metrics']
            self.epochs = x['epochs']
            self.patience = x['patience']
            self.split = x['split']
            self.cluster = x['cluster']


def Evaluation(model, status, training=None, validation=None, test=None):
    return {
        'model': model,
        'status': status,
        'training': training,
        'validation': validation,
        'test': test,
    }


def main(directory: Url, algorithm: ClusterStrategy, algorithm2: ModelSplit) -> List[List[Dict[str, Any]]]:
    """
    Does all the work.
    """
    images = ImageDirectory(directory).jpeg(False)
    if len(images) == 0:
        return list()
    clusters = algorithm.run_cached(images)
    rates = algorithm2.predict(images, True).y.predicted
    print('Ranking results....')
    cr = ClusterRank(clusters, rates)
    return cr.jsonable()


if __name__ == '__main__':
    app = flask.Flask(__name__)

    @app.route('/run', methods=['POST'])
    def run():
        try:
            if not flask.request.is_json:
                response = flask.Response()
                response.status_code = 400
                response.status = 'Error: Not JSON'
                return response
            request_data = flask.request.get_json()
            directory = request_data['url']
            settings = Settings()
            settings.__dict__.update(request_data)
            # if not settings.exists():
            #     settings.save()
            # else:
            #     settings.load()
            cluster = ClusterRegistry.get(settings.cluster)
            model = ModelBuilder.create(
                settings.architecture,
                settings.dataset,
                settings.loss,
                settings.optimizer,
                settings.metrics,
                settings.epochs,
                settings.patience,
            )
            split = model.split(settings.split)
            results = main(directory, cluster, split)
            results = flask.jsonify(results)
            return results
        except TrainingIncompleteException:
            response = flask.Response()
            response.status_code = 400
            response.status = 'Error: Training incomplete'
            return response
        except ModelStateMissingError:
            response = flask.Response()
            response.status_code = 400
            response.status = 'Error: Model state missing'
            return response
        except BadModelSettings:
            response = flask.Response()
            response.status_code = 400
            response.status = 'Error: Incompatible architecture/dataset'
            return response
        except ClusterRegistryNameError:
            response = flask.Response()
            response.status_code = 400
            response.status = 'Error: Bad cluster name'
            return response
        except:
            print_exc()
            response = flask.Response()
            response.status_code = 500
            response.status = 'Error: Unknown'
            return response

    @app.route('/options', methods=['GET'])
    def get_options():
        return {
            'architectures': list(ModelBuilder.ARCHITECTURES.keys()),
            'datasets': list(ModelBuilder.DATASETS.keys()),
            'losses': list(ModelBuilder.LOSSES.keys()),
            'optimizers': list(ModelBuilder.OPTIMIZERS.keys()),
            'clusters': ClusterRegistry.keys(),
        }

    @app.route('/predict', methods=['POST'])
    def predict():
        try:
            if not flask.request.is_json:
                response = flask.Response()
                response.status_code = 400
                response.status = 'Error: Not JSON'
                return response
            settings = flask.request.get_json()
            model = ModelBuilder.create(
                settings['architecture'],
                settings['dataset'],
                settings['loss'],
                settings['optimizer'],
                settings['metrics'],
                settings['epochs'],
                settings['patience'],
            )
            split = model.split(settings['split'])
            key_guide = ModelBuilder.DATASETS[settings['dataset']].classes()
            if settings['phase'] == 'training':
                results = split.predict_training_set(False)
            elif settings['phase'] == 'validation':
                results = split.predict_validation_set(False)
            elif settings['phase'] == 'test':
                results = split.predict_test_set(False)
            else:
                response = flask.Response()
                response.status_code = 400
                response.status = 'Error: Incorrect phase'
                return response
            return flask.jsonify({
                'keyGuide': key_guide,
                'prediction': results.get_dict(),
                'metrics': {
                    'accuracy': results.accuracy(),
                    'recall': results.recall(),
                    'precision': results.precision(),
                    'f1': results.f1(),
                },
            })
        except TrainingIncompleteException:
            response = flask.Response()
            response.status_code = 400
            response.status = 'Error: Training incomplete'
            return response
        except ModelStateMissingError:
            response = flask.Response()
            response.status_code = 400
            response.status = 'Error: Model state missing'
            return response
        except BadModelSettings:
            response = flask.Response()
            response.status_code = 400
            response.status = 'Error: Incompatible architecture/dataset'
            return response
        except:
            print_exc()
            response = flask.Response()
            response.status_code = 500
            response.status = 'Error: Unknown'
            return response

    @app.route('/cluster-algorithms', methods=['GET'])
    def cluster_algorithms():
        results = list()
        for name, algorithm in ClusterRegistry.items():
            parameters = function_signature(algorithm.run)
            if 'images' in parameters:
                del parameters['images']
            results.append({
                'name': name,
                'parameters': parameters,
            })
        return flask.jsonify(results)

    @app.route('/cluster', methods=['POST'])
    def cluster():
        try:
            if not flask.request.is_json:
                response = flask.Response()
                response.status_code = 400
                response.status = 'Error: Not JSON'
                return response
            settings = flask.request.get_json()
            images = ImageDirectory(settings['directory']).jpeg(False)
            cluster = ClusterRegistry.get(settings['cluster'])
            results = cluster.run_cached(images, **settings['args']).urls()
            results = flask.jsonify(results)
            return results
        except ClusterRegistryNameError:
            response = flask.Response()
            response.status_code = 400
            response.status = 'Error: Unknown clustering algorithm'
            return response
        except:
            print_exc()
            response = flask.Response()
            response.status_code = 500
            response.status = 'Error: Unknown'
            return response

    @app.route('/evaluate', methods=['POST'])
    def evaluate():
        if not flask.request.is_json:
            response = flask.Response()
            response.status_code = 400
            response.status = 'Error: Not JSON'
            return response
        try:
            settings = flask.request.get_json()
            model = ModelBuilder.create(
                settings['architecture'],
                settings['dataset'],
                settings['loss'],
                settings['optimizer'],
                settings['metrics'],
                settings['epochs'],
                settings['patience'],
            )
            split = model.split(settings['split'])
            status = str(split.status())
            if split.is_complete():
                training = split.evaluate_training_set()
                validation = split.evaluate_validation_set()
                test = split.evaluate_test_set()
                return flask.jsonify(Evaluation(settings, status, training, validation, test))
            else:
                return flask.jsonify(Evaluation(settings, status))
        except ModelStateMissingError:
            return flask.jsonify(Evaluation(settings, str(TrainingStatus.STATE_MISSING)))
        except BadModelSettings:
            return flask.jsonify(Evaluation(settings, str(TrainingStatus.BAD_SETTINGS)))
        except:
            print_exc()
            response = flask.Response()
            response.status_code = 500
            response.status = 'Error: Unknown'
            return response

    @app.route('/evaluate/all/0', methods=['GET'])
    def evaluate_all_0():
        try:
            results = []
            for architecture, dataset, loss, optimizer in ModelBuilder.builds():
                settings = {
                    'architecture': architecture,
                    'dataset': dataset,
                    'loss': loss,
                    'optimizer': optimizer,
                    'metrics': 'acc',
                    'epochs': 0,
                    'patience': 3,
                    'split': 0,
                }
                try:
                    model = ModelBuilder.create(
                        architecture,
                        dataset,
                        loss,
                        optimizer,
                        'acc',
                        0,
                        3,
                    )
                    split = model.split(0)
                    status = str(split.status())
                    if split.is_complete():
                        training = split.evaluate_training_set()
                        validation = split.evaluate_validation_set()
                        test = split.evaluate_test_set()
                        results.append(Evaluation(settings, status, training, validation, test))
                    else:
                        results.append(Evaluation(settings, status))
                except ModelStateMissingError:
                    results.append(Evaluation(settings, 'model state missing'))
                except BadModelSettings:
                    results.append(Evaluation(settings, 'incompatible'))
            return flask.jsonify(results)
        except:
            print_exc()
            response = flask.Response()
            response.status_code = 500
            response.status = 'Error: Unknown'
            return response

    @app.route('/modelsummary', methods=['POST'])
    def model_summary():
        try:
            if not flask.request.is_json:
                response = flask.Response()
                response.status_code = 400
                response.status = 'Error: Not JSON'
                return response
            settings = flask.request.get_json()
            model = ModelBuilder.create(
                settings['architecture'],
                settings['dataset'],
                settings['loss'],
                settings['optimizer'],
                settings['metrics'],
                settings['epochs'],
                settings['patience'],
            )
            return flask.jsonify(model.summary())
        except TrainingIncompleteException:
            response = flask.Response()
            response.status_code = 400
            response.status = 'Error: Training incomplete'
            return response
        except ModelStateMissingError:
            response = flask.Response()
            response.status_code = 400
            response.status = 'Error: Model state missing'
            return response
        except BadModelSettings:
            response = flask.Response()
            response.status_code = 400
            response.status = 'Error: Incompatible architecture/dataset'
            return response
        except:
            print_exc()
            response = flask.Response()
            response.status_code = 500
            response.status = 'Error: Unknown'
            return response

    @app.route('/training-statuses', methods=['GET'])
    def training_statuses():
        return flask.jsonify([str(e) for e in TrainingStatus])

    app.run(port=8080, threaded=False)
