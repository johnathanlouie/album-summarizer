import json
import os.path
from copy import deepcopy
from traceback import print_exc
from typing import Any, Dict, List
from urllib.parse import quote

import flask

import aaa
import addon
from core.cluster import (ClusterRegistry, ClusterRegistryNameError,
                          ClusterResults, ClusterStrategy)
from core.model import BadModelSettings, ModelSplit
from core.modelbuilder import ModelBuilder
from jl import ImageDirectory
from typing2 import Url


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
        Saves the results to a JSON file at 'electron/public/data/***.json'.
        """
        dst = 'electron/public/data/%s.json' % quote(dst)
        with open(dst, 'w', encoding='utf8') as f:
            json.dump(self._results, f, indent=4)

    def jsonable(self) -> List[List[Dict[str, Any]]]:
        return deepcopy(self._results)


class Settings(object):
    """
    """

    FILENAME = 'out/settings.json'

    def __init__(self):
        self.architecture = 'smi13'
        self.dataset = 'ccr'
        self.loss = 'rmse'
        self.optimizer = 'sgd1'
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


def main(directory: Url, algorithm: ClusterStrategy, algorithm2: ModelSplit) -> None:
    """
    Does all the work.
    """
    images = ImageDirectory(directory).jpeg(False)
    if len(images) == 0:
        return list()
    clusters = algorithm.run(images)
    rates = algorithm2.predict(images).human_readable()
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
            directory = flask.request.get_json()['url']
            settings = Settings()
            if not settings.exists():
                settings.save()
            else:
                settings.load()
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
            return results
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
            if settings['phase'] == 'training':
                results = split.predict_training_set(False).get_dict()
            elif settings['phase'] == 'validation':
                results = split.predict_validation_set(False).get_dict()
            elif settings['phase'] == 'test':
                results = split.predict_test_set(False).get_dict()
            else:
                response = flask.Response()
                response.status_code = 400
                response.status = 'Error: Incorrect phase'
                return response
            return results
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
            results = cluster.run(images).urls()
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

    app.run(port=8080, threaded=False)
