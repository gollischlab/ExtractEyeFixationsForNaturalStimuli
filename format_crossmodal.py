#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Format the fixations of the Cross Modal study and saves it to disk.
"""

import formatdata as ft


dataset = 'Cross Modal'
imagefiles = range(1, 128+1)  # Exclude white noise
frozenimages = [37, 76, 99, 111, 118, 126]
num_stimuli = 3  # Parts to divide running part into
postfix = 'crossmodal1'

# Extract fixations
running, frozen = ft.getfixationsfromdata(dataset, imagefiles, frozenimages)

# Split and save running fixations into several files
ft.saveparts(running, num_stimuli, postfix=postfix, frozen=frozen,
             frozenimages=frozenimages,
             meta=['SUBJECTINDEX', 'condition', 'trial'])
