#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Load meta data.
"""

import os
import pandas as pd


# Read meta data
metapath = os.path.join('metadata', 'meta.csv')
meta = pd.read_csv(metapath, delimiter=';', skipinitialspace=True)
del metapath

# Fix categories to lists
meta['Categories'] = meta['Categories'].apply(lambda x:
                                              [int(i) for i in x.split(',')])
