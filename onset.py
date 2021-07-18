#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  8 19:47:01 2021
Onset detection for simple monophonic piano track

@author: bojan
"""

import numpy as np
from scipy import signal as sig

def local_energy(x, n_win = 2048, win_type = 'hann'):
    '''
    Computes the local energy of the signal
    E = convolution(x**2, w**2) 

    Parameters
    ----------
    x : numpy.ndarray
        The signal
    n_win : int, optional
        Window length. The default is 2048.
    win_type : string, optional
        Window type. The default is 'hann'.

    Returns
    -------
    E : numpy.ndarray
        The local energy of x

    '''
    win = sig.get_window(win_type, n_win)
    return np.convolve(np.power(x, 2), np.power(win, 2), 'same')

def energy_novelty(x, n_win = 2048, win_type = 'hann', log = False, l = 10,
                   norm = True):
    '''
    Computes the energy-based novelty function for the signal
    (half-wave rectification of the derivative of the local energy)
    Parameters
    ----------
    x : numpy.ndarray
        The signal
    n_win : int, optional
        Window length. The default is 2048.
    win_type : string, optional
        Window type. The default is 'hann'.
    log : bool. The default is False.
        If True, take log of the local energy before computing novelty
        function (log(1 + l * E))
    l : int. The default is 10
        If log is True, the l factor in the log function
    norm : bool. The default is True
        Normalise the novelty function
    Returns
    -------
    EN : numpy.ndarray
        Energy-based novelty function for the signal

    '''
    E = local_energy(x, n_win, win_type)
    if log:
        E = np.log1p(l * E)
    EN = np.concatenate((np.diff(E), [0]))
    EN[EN < 0] = 0
    if norm:
        EN = EN / np.amax(EN)
    return EN

def find_peaks(x, min_distance, threshold):
    '''
    Simple peak finding algorithm, based on minimum threshold and
    minimum distance between peaks

    Parameters
    ----------
    x : numpy.ndarray
        Input array
    min_distance : int
        Minimum distance between peaks
    threshold : float
        Minimum value threshold

    Returns
    -------
    peaks : numpy.array
        Indices of the peaks

    '''
    peaks = []
    i_prev = -min_distance
    if threshold is None:
        threshold = np.min(x) - 1
    for i in range(1, x.shape[0] - 1):
        if x[i - 1] < x[i] and x[i] > x[i + 1]:
            if x[i] >= threshold and i > i_prev + min_distance:
                peaks.append(i)
                i_prev = i
    peaks = np.array(peaks)
    return peaks

def get_onsets(x, fs, min_distance = 0.1, threshold = 0.1, seconds = True):
    '''
    Compute the onsets for audio signal x

    Parameters
    ----------
    x : numpy.ndarray
        Input audio signal
    fs : int
        Sampling frequency
    min_distance : float
        Minimum distance between peaks for the peak finding
    threshold : float
        Minimum value threshold for the peak finding
    seconds : bool
        If true, return the onsets positions in seconds. The default is True.
    Returns
    -------
    peaks : numpy.ndarray
        the onsets positions

    '''
    en = energy_novelty(x, log = True)
    peaks = find_peaks(en, threshold = 0.1, min_distance = int(min_distance*fs))
    if seconds:
        peaks = peaks / fs
    return peaks
