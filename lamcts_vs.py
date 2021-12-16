import torch
import botorch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import random
from benchmark import synthetic_function_problem
from MCTS import MCTS
from utils import save_results


parser = argparse.ArgumentParser()
parser.add_argument('--func', default='hartmann6_50', type=str)
parser.add_argument('--max_samples', default=1000, type=int)
parser.add_argument('--turbo_max_evals', default=50, type=int)
parser.add_argument('--Cp', default=0.1, type=float)
parser.add_argument('--ipt_solver', default='bo', type=str)
parser.add_argument('--uipt_solver', default='bestk', type=str)
parser.add_argument('--root_dir', default='simple_logs', type=str)
parser.add_argument('--postfix', default=None, type=str)
parser.add_argument('--seed', default=42, type=int)
args = parser.parse_args()

print(args)

random.seed(args.seed)
np.random.seed(args.seed)
botorch.manual_seed(args.seed)
torch.manual_seed(args.seed)
f = synthetic_function_problem[args.func]

agent = MCTS(
    func=f,
    dims=f.dims,
    lb=f.lb,
    ub=f.ub,
    Cp=args.Cp,
    min_num_variables=3, 
    select_right_threshold=5, 
    split_type='mean',
    ipt_solver=args.ipt_solver, 
    uipt_solver=args.uipt_solver,
    turbo_max_evals=50,
)

agent.search(max_samples=args.max_samples, verbose=False)

print('best f(x):', agent.value_trace[-1][1])
df_data = pd.DataFrame(agent.value_trace, columns=['x', 'y'])
algo_name = 'lamcts_vs_{}'.format(args.ipt_solver)
if args.postfix is not None:
    algo_name += ('_' + args.postfix)
save_results(args.root_dir, algo_name, args.func, args.seed, df_data)