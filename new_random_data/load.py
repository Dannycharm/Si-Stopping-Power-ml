#!/usr/bin/env python
# coding=utf-8
import numpy as np
import h5py

h5f = h5py.File("./random_v0.5.h5")
kl = list(h5f.keys())

for k in kl:
    E = h5f[f'{k}/E'][:] # Energy
    pos = h5f[f'{k}/pos'][:] # position
    disp = h5f[f'{k}/disp'][:] # displacement
    vel = h5f[f'{k}/vel'][:] # velocity
    force = h5f[f'{k}/sp'][:] # stopping force

    file_id = [k]*E.shape[0]

