#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  8 22:22:05 2021

@author: bojan
"""
import numpy as np

note_name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def get_pitch_notation(note_freq):
    '''
    Generates the pitch notation of note, given its frequency

    Parameters
    ----------
    note_freq : float
        Note frequency in Hz

    Returns
    -------
    string
        Pitch notation of the note

    '''
    A4 = 440
    C0 = A4 * np.power(2, -4.75)
    
    h = int(np.round(12*np.log2(note_freq/C0)))
    octave = h // 12
    n = h % 12
    
    return note_name[n] + str(octave)