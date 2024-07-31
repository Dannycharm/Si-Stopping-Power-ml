#!/usr/bin/env python
# coding=utf-8

import logging
from tqdm import tqdm
from glob import glob
import numpy as np
import argparse
import os
import sys
sys.path.append(f"/scratch/users/pdanie20/yifan/")
import pickle as pkl
import pandas as pd

from stopping_power_ml.stop_distance import StoppingDistanceComputer
from stopping_power_ml.integrator import TrajectoryIntegrator
import keras

import os
import time
import functools
from datetime import datetime
print = functools.partial(print, flush=True)

# Set up the root logger to INFO to suppress DEBUG messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Make an argument parser
parser = argparse.ArgumentParser(description="Run a stopping distance simulation in a single direction")
parser.add_argument('--direction', nargs = 3, type = int, default=[1, 0, 0], help='Direction vector')
parser.add_argument('--random-dir', action = 'store_true', help = 'Projectiles move in a random direction')
parser.add_argument('--random-seed', default = 1, type = int)
parser.add_argument('--mass-scaler', default = 1, type = float, help = "scaled the mass of the projectile")
parser.add_argument('--max-step-size', default = 10, type = float, help = "max time step size of ODE solver")
parser.add_argument('--rtol', default = 1e-4, type = float, help = "rtol of ODE solver")
parser.add_argument('--atol', default = 1e-6, type = float, help = "atol of ODE solver")
parser.add_argument('--stepper', default = "rk45", type = str, help = "ODE stepper, need to be in scipy.integrate or velocity_verlet")
parser.add_argument('--model', default = "../model-random-and-channel.h5", type = str, help = "machine learned model")
parser.add_argument('velocity', help='Starting velocity magnitude', type=float)
parser.add_argument('n_samples', help='Number of trajectories to sample', type=int)

# Parse the arguments
args = parser.parse_args()
logging.info("Arguments received:")
for arg in vars(args):
    logging.info(f"{arg}: {getattr(args, arg)}")

stepper = args.stepper.lower()

mpath = args.model
model = keras.models.load_model(mpath)

with open(os.path.join('..', 'featurizer.pkl'), 'rb') as fp:
    featurizers = pkl.load(fp)

start_frame = pkl.load(open(os.path.join('..', '..', 'al_starting_frame.pkl'), 'rb'))
traj_int = TrajectoryIntegrator(start_frame, model, featurizers)

computer = StoppingDistanceComputer(traj_int)

computer.max_step = args.max_step_size
computer.proj_mass *= args.mass_scaler
computer.rtol = args.rtol
computer.atol = args.atol
computer.stepper = stepper

print("mass of projectile", computer.proj_mass)

step_size = args.max_step_size
scaler = args.mass_scaler
jobid = os.getenv('SLURM_JOBID', '')

output_dir = f'all_traj/{jobid}'

# Generate random starting points and directions on the unit sphere
rng = np.random.RandomState(args.random_seed)
if not args.random_dir:
    velocity = np.array(args.direction, dtype=float)
    velocity *= args.velocity / np.linalg.norm(velocity)
    velocities = np.tile(velocity, (args.n_samples, 1))
else:
    u = rng.uniform(-1, 1, size=(args.n_samples, 1))
    v = rng.uniform(0, 2 * np.pi, size=(args.n_samples, 1))
    velocities = np.hstack((
        np.sqrt(1 - u ** 2) * np.cos(v),
        np.sqrt(1 - u ** 2) * np.sin(v),
        u
    )) * args.velocity
#positions = rng.uniform(size=(args.n_samples, 3))

positions = np.atleast_2d([0., 0.75, 0.75])
#positions = np.atleast_2d([0.4359949, 0.02592623, 0.54966248])

# Prepare the output directory and determine starting number
result_file = os.path.join(output_dir, 'stop_dists.csv')
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)
    with open(result_file, 'w') as fp:
        print('run,stopping_dist', file=fp)

logging.info(f"starting the compute loop")

for run_id, (u, v) in enumerate(zip(positions, velocities)):
    start = time.time()
    
    logging.info(f"starting position {u} starting velocity {v}")

    var =  os.getenv('VAR', '')
    key = f"traj_{run_id}" if var == '' else f"traj_{var}_{run_id}"
    
    distance, traj = computer.compute_stopping_distance(u, v, max_time = 1e5, output = 1)
 
    with open(result_file, 'a') as fp:
        print(f'{run_id},{distance}', file=fp)

    with pd.HDFStore(f'{output_dir}/traj.h5', mode = 'a', complib = 'zlib', complevel = 4) as store: 
        store.put(key, traj)

        # Add attributes
        info = {'start_pos': u, 
                'start_vel': v, 
                'rtol': computer.rtol, 
                'atol': computer.atol, 
                'stepper': computer.stepper, 
                "max_time_step": computer.max_step, 
                "proj_mass": computer.proj_mass, 
                "model": mpath, 
                "timestamp": datetime.now().isoformat()}

        store.get_storer(key).attrs.traj_info = info
        store.flush()  # Commit data to disk explicitly

    logging.info(f"finished the iteration {run_id}, with {time.time() - start} s")
