from copy import deepcopy
from json import dump
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
            dump(self._results, f, indent=4)

    def json(self) -> List[List[Dict[str, Any]]]:
        return deepcopy(self._results)


class Settings(object):
    """
    """

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
    # print('Saving results....')
    # cr.save_results(directory)
    return cr.json()


if __name__ == '__main__':
    app = flask.Flask(__name__)

    @app.route('/run', methods=['POST'])
    def run():
        try:
            if not flask.request.is_json:
                return {
                    'status': 1,
                    'message': 'Error: Not JSON',
                    'data': None,
                }
            directory = flask.request.get_json()['url']
            settings = Settings()
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
            return {
                'status': 0,
                'message': 'OK',
                'data': results,
            }
        except BadModelSettings:
            return {
                'status': 2,
                'message': 'Error: Incompatible architecture/dataset',
                'data': None,
            }
        except ClusterRegistryNameError:
            return {
                'status': 3,
                'message': 'Error: Bad cluster name',
                'data': None,
            }
        except:
            print_exc()
            return {
                'status': 100,
                'message': 'Error: Unknown error',
                'data': None,
            }

    @app.route('/run', methods=['GET'])
    def run2():
        return {
            'status': 0,
            'message': 'OK',
            'data': None,
        }

    app.run(port=8080, threaded=False)
