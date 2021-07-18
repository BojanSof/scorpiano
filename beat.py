#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  8 21:56:00 2021
Musical notes beat detection
@author: bojan
"""

from tempo import get_tempo
from onset import get_onsets, local_energy
import numpy as np

def get_beats(x, fs, min_beat = 0.25):
    '''
    Computes notes beats

    Parameters
    ----------
    x : numpy.ndarray
        Input audio signal
    fs : int
        Sampling frequency in Hz
    min_beat : float
        Minimum beat duration (1 = quarter note)
    Returns
    -------
    beats : numpy.ndarray
        Notes beats
    tempo : float
        Tempo of the audio (bpm)

    '''
    tempo_m = get_tempo(x, fs)
    tempo = tempo_m / 60
    onsets = get_onsets(x, fs)
    # for last note
    last_note = x[int(fs*onsets[-1]):]
    last_note = last_note[::-1]
    last_note_energy = local_energy(last_note)
    last_note_energy = last_note_energy / np.amax(np.abs(last_note_energy))
    last_note_dur = 0
    last_note_th = 1e-3
    while(last_note_energy[last_note_dur] < last_note_th):
        last_note_dur += 1
    last_note_dur = last_note_energy.size - last_note_dur
        
    beats = np.diff(onsets)
    beats = np.concatenate((beats, [last_note_dur / fs]))
    min_beat = 1/min_beat
    beats = np.round(beats * tempo * min_beat) / min_beat
    return beats, tempo_m[0]