from naslib.search_spaces import (
    NasBench101SearchSpace,
    NasBench201SearchSpace,
    DartsSearchSpace,
    NasBenchNLPSearchSpace,
    NasBenchASRSearchSpace,
    TransBench101SearchSpaceMacro,
    TransBench101SearchSpaceMicro
)
from naslib.utils import get_dataset_api
from naslib.search_spaces.core.query_metrics import Metric
import numpy as np


search_spaces = {
    'nasbench101': NasBench101SearchSpace,
    'nasbench201': NasBench201SearchSpace,
    'nlp': NasBenchNLPSearchSpace,
    'asr': NasBenchASRSearchSpace,
    'transbench101_micro': TransBench101SearchSpaceMicro,
    'transbench101_macro': TransBench101SearchSpaceMacro,
}

tasks = {
    'nasbench101': ['cifar10'],
    'nasbench201': ['cifar100', 'ImageNet16-120'],
    'darts': ['cifar10'],
    'nlp': ['treebank'],
    'asr': ['timit'],
    'transbench101_micro': [
        'class_scene',
        'class_object',
        'jigsaw',
        'room_layout',
        'segmentsemantic',
        'normal',
        'autoencoder'
    ],
    'transbench101_macro': [
        'class_scene',
        'class_object',
        'jigsaw',
        'room_layout',
        'segmentsemantic',
        'normal',
        'autoencoder'
    ]
}


class NASLibBench:
    def __init__(self, name, task=None, seed=None):
        if name == 'nasbench201':
            self.dims = 30
            self.n_category = [5, 5, 5, 5, 5, 5]
        elif name == 'transbench101_micro':
            self.dims = 24
            self.n_category = [4, 4, 4, 4, 4, 4]
        else:
            assert 0
        assert sum(self.n_category) == self.dims
        self.graph = search_spaces[name]()
        self.dataset = tasks[name][0]
        self.dataset_api = get_dataset_api(search_space=name, dataset=self.dataset)
        
        self.lb = np.zeros(self.dims)
        self.ub = np.ones(self.dims)
        self.opt_val = 1.0
        
    def __call__(self, x):
        assert len(x) == self.dims
        assert x.ndim == 1
        assert np.all(x <= self.ub) and np.all(x >= self.lb)
        op_indices = []
        i = 0
        for idx, j in enumerate(self.n_category):
            choice = np.argmax(x[i: i+j])
            op_indices.append(choice)
            i += j
        op_indices = np.array(op_indices)
        graph = self.graph.clone()
        graph.set_op_indices(op_indices)
        # print(op_indices)
        # print(self.graph.get_op_indices())
        result = graph.query(Metric.VAL_ACCURACY, dataset=self.dataset, dataset_api=self.dataset_api)
        return result / 100
    
    
if __name__ == '__main__':
    nas_problem = NASLibBench('transbench101_micro')
    result = nas_problem(np.random.uniform(0, 1, nas_problem.dims))
    print(result)
    result = nas_problem(np.random.uniform(0, 1, nas_problem.dims))
    print(result)
