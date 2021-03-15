from copy import deepcopy
from json import dump
from typing import Any, Dict, List
from urllib.parse import quote

import flask

import aaa
import architecture.smi13
import architecture.vgg16
import cluster.histogram
import cluster.hybridcluster
import cluster.sift
import coption.custom
import coption.keras
import coption.keras2
import core.modelbuilder
import dataset.anifood
import dataset.cc
import dataset.lamem
from core import modelbuilder
from core.cluster import ClusterRegistry, ClusterResults, ClusterStrategy
from core.model import ModelSplit
from core.modelbuilder import ModelBuilder
from jl import ImageDirectory, Url


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


def main(directory: Url, algorithm: ClusterStrategy, algorithm2: ModelSplit) -> None:
    """
    Does all the work.
    """
    images = ImageDirectory(directory).jpeg(False)
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
        if not flask.request.is_json:
            return {
                'status': 1,
                'message': 'Error: Not JSON',
                'data': None,
            }
        settings = flask.request.get_json()
        cluster = ClusterRegistry.get(settings['cluster'])
        model_settings = settings['model']
        try:
            model = ModelBuilder.create(
                model_settings['architecture'],
                model_settings['dataset'],
                model_settings['loss'],
                model_settings['optimizer'],
                model_settings['metrics'],
                model_settings['epochs'],
                model_settings['patience'],
            )
            results = main(settings['url'], cluster, model)
            return {
                'status': 0,
                'message': 'OK',
                'data': results,
            }
        except ValueError:
            return {
                'status': 2,
                'message': 'Error: Incompatible architecture/Dataset',
                'data': None,
            }


    @app.route('/run', methods=['GET'])
    def run2():
        return {
            'status': 0,
            'message': 'OK',
            'data': None,
        }

    app.run(port=8080)
