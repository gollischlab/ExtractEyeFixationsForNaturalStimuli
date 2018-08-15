#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functions to create formatted txt files for the OpenGL stimulator to read.
"""

import datetime
import fixmat
import os
import pandas as pd


def dividerunningfrozen(data, frozenimages):
    """
    Divide fixations into frozen and running part.

    Parameters
    ----------
    data: DataFrame
        All data.
    frozenimages: list
        Image file numbers to take as frozen fixations.

    Returns
    -------
    running: DataFrame
        Formatted fixations (running part).
    frozen: DataFrame
        Formatted fixations (frozen part).
    """
    # Divide into running and frozen fixations
    running = data
    frozen = None

    for k, v in enumerate(frozenimages):
        block, indices = getfixationblock(running, colname='filenumber', val=v)
        running = running[~running.index.isin(indices)]
        if frozen is None:
            frozen = block
        else:
            frozen = frozen.append(block, ignore_index=False)

    return running, frozen


def getfixationsfromdata(dataset, imagefiles='all', frozenimages=None):
    """
    Preprocess data common to all datasets.

    Parameters
    ----------
    dataset: str
        Name of data set
    imagesfiles: list or range (optional)
        Image file numbers to include, 'all' for all. Default is 'all'.
    frozenimages: list (optional)
        Image file numbers to take as frozen fixations.

    Returns
    -------
    data: DataFrame
        Formatted fixations, if frozenimages == None.
    running: DataFrame
        Formatted fixations (running part), if frozenimages != None.
    frozen: DataFrame
        Formatted fixations (frozen part), if frozenimages != None.
    """
    # Load data set
    data, mdata = fixmat.load(os.path.join('data', 'etdb_v1.0.hdf5'), dataset)
    screen_x, screen_y = tuple(map(
        int, mdata['Display resolution (pixels)'].split('x')))

    # Process properties

    # Remove invalid images
    if imagefiles != 'all':
        data = data[data['filenumber'].isin(imagefiles)]

    # Adjust file number offset
    data[:]['filenumber'] -= data[:]['filenumber'].min()

    # Round coordinates to integers. Pandas indexing is stupid
    data[:][['x', 'y']] = data[:][['x', 'y']].round()
    data = data.astype({'x': 'int', 'y': 'int'})

    # Squash start and end to duration
    # data = data.assign(duration=data['end'] - data['start'])
    # del data['end'], data['start']

    # "Invert" coordinate origin (from top-left to bottom-left: OpenGL)
    # Not used any more.
    # data[:]['y'] = screen_y - data['y']

    if frozenimages is None:
        return data
    else:
        return dividerunningfrozen(data, frozenimages)


def estimateruntime(data):
    """
    Estimate the total runtime of the fixations.

    Parameters
    ----------
    data: DataFrame
        Fixation data.

    Returns
    -------
    time: str
        Human readable time.
    """
    total_time = 0
    for idx, row in data.iterrows():
        total_time += row['end'] - row['start']
    return str(datetime.timedelta(milliseconds=total_time))


def getfixationblock(data, k=1, colname='', val=None):
    """
    Get a block of fixations.

    Parameters
    ----------
    data: DataFrame
        Fixation data.
    k: int (optional)
        Get k-th block of fixations. Default is 1.
    colname: str (optional)
        Column name to check for. Default is ''.
    val: object (optional)
        Value to check for in column 'colname'. Default is None.

    Returns
    -------
    block: DataFrame
        Selected block.
    indices: ndarray
        Indices.

    Raises
    ------
    KeyError:
        If 'val' is not found in 'data' in column 'colname'.
    """
    # Get indices of matching rows
    if colname != '':
        indices = data[data[colname] == val].index.tolist()
        if indices == []:
            raise KeyError(f'Column "{colname}" does not take value {val}.')
    else:
        indices = data.index.tolist()
    matched = data.reindex(indices)

    # Counter variables
    start_idx = end_idx = None
    block = 1
    last_fix = 0

    # Iterate over all indices
    for idx, row in matched.iterrows():
        # Lower fixation number indicates new block
        if row['fix'] <= last_fix:
            block += 1
        last_fix = row['fix']

        # Record block indices
        if block == k:
            if start_idx is None:
                start_idx = idx
                end_idx = idx
            else:
                end_idx = idx
        elif block == k+1:
            break

    indices = range(start_idx, end_idx+1)
    return data.loc[indices, :], indices


def extractblocks(data):
    """
    Separate fixation into individual blocks.

    Parameters
    ----------
    data: DataFrame
        Fixation data.

    Returns
    -------
    blocks: list of DataFrames
        Blocks of fixations.
    """
    blocks = []
    while data.shape[0] > 0:
        block, indices = getfixationblock(data)
        blocks.append(block)
        data = data[~data.index.isin(indices)]
    return blocks


def stitchblocks(blocks, **kwargs):
    """
    Combine list of DataFrames to one DataFrame.

    Parameters
    ----------
    blocks: list of DataFrames
        Fixation blocks.
    kwargs:
        Additional arguments for pandas.concat.

    Returns
    -------
    df: DataFrame
        Concatenated DataFrame.
    """
    return pd.concat(blocks, **kwargs)


def makefilepath(postfix=''):
    """
    Generate file path for fixation text file.

    Parameters
    ----------
    postfix: str (optional)
        Postfix for the filename.

    Returns
    -------
    path: str
        Generated file path.
    """
    if len(postfix) > 0:
        postfix = '_' + postfix
    return os.path.join('formatted', f'fixations{postfix}.txt')


def savetofile(data, postfix='', writemode='w', header=False):
    """
    Save the passed data into a txt file.

    Parameters
    ----------
    data: DataFrame
        Data to save space separated.
    postfix: str (optional)
        Postfix for the filename. Default is ''.
    """
    fout = makefilepath(postfix)
    with open(fout, writemode) as f:
        data.to_csv(f, sep=' ', line_terminator='\r\n', header=header,
                    index=False)


def savefixations(running, frozen=None, postfix='', frozenimages=[],
                  meta=None):
    """
    Save fixations to txt file. Wrapper for savetofile.

    Parameters
    ----------
    running: DataFrame
        Running fixations.
    frozen: DataFrame (optional)
        Frozen fixations. Default is None.
    postfix: str (optional)
        Postfix for the filename. Default is ''.
    frozenimages: list (optional)
        Image file numbers to take as frozen fixations. Default is [].
    meta: list (optional)
        DataFrame column names to write to meta file. Default is None.
    """
    if frozen is not None:
        data = frozen.append(running, ignore_index=False)
        frozen_fix = frozen.shape[0]
        frozentime = estimateruntime(frozen)
    else:
        data = running
        frozen_fix = 0
        frozentime = None

    fixations = data[['filenumber', 'start', 'end', 'x', 'y']]
    savetofile(fixations, postfix)

    runningtime = estimateruntime(running)
    fout = makefilepath(postfix + '_meta')
    with open(fout, 'w') as f:
        f.write(f'Number of running fixations: {running.shape[0]}\r\n'
                f'Number of frozen fixations: {frozen_fix}\r\n'
                f'Frozen images: {frozenimages}\r\n'
                f'Estimated time for running fixations (excluding frozen '
                f'repetitions): {runningtime}\r\n'
                f'Estimated time for frozen fixations: {frozentime}\r\n'
                '\r\n')

    if meta is not None:
        metadata = data[meta]
        savetofile(metadata, postfix + '_meta', writemode='a', header=True)


def saveparts(running, num_parts, postfix='', **kwargs):
    """
    Save fixations into several files.
    """
    if type(running) is pd.core.frame.DataFrame:
        running = extractblocks(running)

    part_len = len(running) // num_parts
    for p in range(num_parts-1):
        running_part = stitchblocks(running[:part_len], ignore_index=False)
        savefixations(running_part, postfix=postfix + f'_part{p+1}', **kwargs)
        running = running[part_len:]

    # Save remaining
    running_part = stitchblocks(running, ignore_index=False)
    savefixations(running_part, postfix=postfix + f'_part{num_parts}',
                  **kwargs)
