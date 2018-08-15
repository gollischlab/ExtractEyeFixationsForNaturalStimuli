#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Loads a dataset from the Osnabrueck-Hamburg eye tracking database.

Example:
    >>> import fixmat
    >>> baseline, meta = fixmat.load('etdb_v1.0.hdf5', 'Baseline')

"""

import pandas as pd
import h5py

def load(dbname, dataset):
    """
    dbname is the path to the database hdf file, dataset is the dataset name.

    returns a pandas dataframe and a dictionary with meta data for the dataset.
    """
    attrs = None
    with h5py.File(dbname) as f:
        if dataset not in f.keys():
            raise ValueError('Can\'t find dataset. Available keys are: '
                             + str(list(f.keys())))
        try:
            df = pd.DataFrame(dict((k, f[dataset][k][:].ravel())
                                   for k in f[dataset].keys()))
        except ValueError:
            raise RuntimeError('Not all fields have the same length:' +
                str(dict((k, f[dataset][k][:].ravel().shape)
                         for k in f[dataset].keys())))
        if len(f[dataset].attrs.keys())>0:
            attrs = dict((k, f[dataset].attrs[k])
                         for k in  f[dataset].attrs.keys())
    return df, attrs
