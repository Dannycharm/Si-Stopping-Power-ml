#!/usr/bin/env python
# coding=utf-8

import sys
from glob import glob
from ase.io import qbox, cube
from ase.visualize import view
from matplotlib import pyplot as plt
from tqdm import tqdm_notebook as tqdm
from stopping_power_ml.io import load_directory, get_charge_density_interpolator
import pandas as pd
import numpy as np
import pickle as pkl
import os
import time
import gzip

import functools
print = functools.partial(print, flush=True)

#dirs = [os.path.dirname(x) for x in glob("data_silicon/silicon_data/2_Electronic_Stopping/H_Si/LDA_H*/v*/Si*.out", recursive=True)] + [os.path.dirname(x) for x in #glob("data_silicon/silicon_data/2_Electronic_Stopping/H_Si/12epp/LDA_H_off_channel_12ePP/v*/", recursive=True)]

dirs = list(set([os.path.dirname(x) for x in glob("data_silicon/silicon_data/2_Electronic_Stopping/H_Si/LDA_H*/v*/Si*.out", recursive=True)] + [os.path.dirname(x) for x in glob("data_silicon/silicon_data/2_Electronic_Stopping/H_Si/12epp/LDA_H_off_channel_12ePP/v*/", recursive=True)]))

print(dirs, len(dirs))

data = []
for file in tqdm(dirs, desc='Directory'):
    print(file)
    frame = load_directory(file, prefix="Si*")
    data.append(frame)
data = pd.concat(data)
print('Read in %d training points'%len(data))

data.reset_index(drop=True, inplace=True)

data.drop('atoms', axis = 'columns').to_pickle(gzip.open('data_1.pkl.gz', 'wb'))
