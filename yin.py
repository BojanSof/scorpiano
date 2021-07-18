#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 18:06:41 2021
Implementation of the YIN pitch detection algorithm
Based on :
De Cheveigné, A., & Kawahara, H. (2002). YIN, a fundamental frequency estimator for speech and music. 
The Journal of the Acoustical Society of America, 111(4), 1917-1930.
Credits: Patrice Guyot. (2018, April 19). Fast Python implementation of the Yin algorithm 
(Version v1.1.1). Zenodo. http://doi.org/10.5281/zenodo.1220947
@author: bojan
"""

import numpy as np
import scipy.signal as sig

def difference_function(x, W, tp_max):
    '''
    Computes the difference function (df)

    Parameters
    ----------
    x : numpy.ndarray
        audio signal
    W : int
        window size
    tp_max:
        maximum period (in samples)

    Returns
    -------
    the difference function
    
    '''
    df = np.zeros((tp_max,))
    for tau in range(1, tp_max):
        for j in range(0, W - tp_max):
            df[tau] += np.power(x[j] - x[j + tau], 2)
    return df

def difference_function_fast(x, N, tp_max):
    '''
    Computes the difference function (df), using autocorrelation calculated
    with FFT (Wiener-Khinchin theorem)
    
    Parameters
    ----------
    x : numpy.ndarray
        audio signal
    W : int
        window size
    tp_max:
        maximum period (in samples)

    Returns
    -------
    the difference function
    
    '''

    N = x.size
    tp_max = min(tp_max, N)
    x_cumsum = np.concatenate((np.array([0.]), (x * x).cumsum()))
    size = N + tp_max
    p2 = (size // 32).bit_length()
    nice_numbers = (16, 18, 20, 24, 25, 27, 30, 32)
    size_pad = min(x * 2 ** p2 for x in nice_numbers if x * 2 ** p2 >= size)
    fc = np.fft.rfft(x, size_pad)
    conv = np.fft.irfft(fc * fc.conjugate())[:tp_max]
    return x_cumsum[N:N - tp_max:-1] + x_cumsum[N] - x_cumsum[:tp_max] - 2 * conv

def cumulative_mean_normalized_difference_function(df):
    '''
    Computes the cumulative mean normalized difference function (cmndf)

    Parameters
    ----------
    df : numpy.ndarray
        difference function

    Returns
    -------
    the cumulative mean normalized difference function

    '''
    cmndf = df[1:] * np.arange(1, df.size) / np.cumsum(df[1:])
    return np.concatenate(([0], cmndf))

def get_pitch_period(cmndf, tp_min, tp_max, threshold = 0.1):
    '''
    Computes the pitch period of the signal, based on the cumulative mean
    normalized difference function

    Parameters
    ----------
    cmndf : np.ndarray
        the cumulative mean normalized difference function
    tp_min : int
        minimum period of the signal
    tp_max : int
        maximum period of the signal
    threshold : float, optional
        threshold value, to compute pitch period. The default is 0.1.

    Returns
    -------
    the pitch period

    '''
    tau = tp_min
    while tau < tp_max:
        if cmndf[tau] < threshold:
            while tau + 1 < tp_max and cmndf[tau + 1] < cmndf[tau]:
                tau += 1
            return tau
        tau += 1
    return 0

def get_pitch(wav, fs, n_win = 3000, n_hop = None, w_type = 'hann',
              f_min = 16.35, f_max = 7902.13, 
              threshold = 0.1):
    '''
    Compute the pitch frequency of the signal    

    Parameters
    ----------
    wav : numpy.ndarray
        the audio signal
    fs : int
        sampling frequency
    n_win : int, optional
        window size. The default is 3000.
    n_hop : int, optional
        window hop. The default is None.
    w_type : string, optional
        window type. The default is hann.
    f_min : float, optional
        minimum possible signal frequency. The default is 16.35.
    f_max : float, optional
        maximum possible signal frequency. The default is 7902.13.
    threshold : float, optional
        threshold value, to compute pitch period. The default is 0.1.

    Returns
    -------
    the pitch frequency

    '''
    if n_hop == None:
        n_hop = n_win // 2
    tp_min = int(fs / f_max)
    tp_max = int(fs / f_min)
    pitch = []
    wav = np.concatenate((np.zeros(n_hop), wav, np.zeros(n_hop)))
    win = sig.get_window(w_type, n_win)
    pos = 0
    while pos <= wav.size - n_win:
        frame = (wav[pos : pos + n_win]) * win
        df = difference_function_fast(frame, n_win, tp_max)
        cmndf = cumulative_mean_normalized_difference_function(df)
        p = get_pitch_period(cmndf, tp_min, tp_max, threshold)
        if p != 0:
            pitch.append(fs / p)
        pos += n_hop

    #return np.average(pitch)
    #return pitch
    return np.median(pitch)
