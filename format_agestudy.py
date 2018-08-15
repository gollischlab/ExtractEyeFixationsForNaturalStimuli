#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Format the fixations of the age study and saves it to disk.
"""

import formatdata as ft


dataset = 'Age study'
categories = [7, 8]
imagefiles = 'all'
cases = ['color', 'bw']
frozenimages = {'color': [4, 15, 21, 34, 62, 117, 123],
                'bw': [15, 21, 30, 95, 107, 126]}
postfix = {'color': 'agestudy_color', 'bw': 'agestudy_bw'}
num_stimuli = {'color': 3, 'bw': 3}

# Extract fixations
data_all = ft.getfixationsfromdata(dataset, imagefiles)

# Filter categories
data = dict()
for i, cat in enumerate(categories):
    data[cat] = data_all[data_all['category'] == cat]
del data_all

# Increase filenumbers (pandas is stupid: it only works in separate loop)
for i, cat in enumerate(categories):
    # Increase filenumbers
    if i > 0:
        last_cat = categories[i-1]
        data[cat].filenumber += data[last_cat].filenumber.max() + 1

# Get fixation blocks
data_blocks = dict()
for cat in categories:
    print(f'Getting blocks of {cat}')
    data_blocks[cat] = ft.extractblocks(data[cat])

# Combine categories by alternating blocks
data = []
for j in range(max([len(i) for i in data_blocks.values()])):
    for cat in categories:
        if len(data_blocks[cat]) < j:
            continue
        data.append(data_blocks[cat][j])
data = ft.stitchblocks(data)

# Save to file parts
for c in cases:
    print(f'Generating and saving case \'{c}\'')
    running, frozen = ft.dividerunningfrozen(data, frozenimages[c])
    ft.saveparts(running, num_stimuli[c], postfix=postfix[c], frozen=frozen,
                 frozenimages=frozenimages[c],
                 meta=['SUBJECTINDEX', 'age', 'answer', 'category'])
