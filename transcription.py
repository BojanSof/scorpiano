#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 10 22:47:21 2021

Notes transcription function and music score generator
1. Find onsets
2. Find pitch frequency within each onset
3. Find beats
4. Generate the music score
@author: bojan
"""
import onset
import beat
import yin
import note
import numpy as np
import music21 as m21
import os

time_signatures = ['2/4', '3/4', '4/4']

def transcribe(wav, fs, min_beat_dur = 0.25, min_distance_notes = 0.1):
    '''
    Computes the pitches of the notes, their beat duration,
    the tempo of the melody and the time signature

    Parameters
    ----------
    wav : numpy.ndarray
        the audio signal
    fs : int
        sampling frequency
    min_beat_dur : float
        minimum beat duration of the notes
    min_distance_notes : float
        minimum distance between two subsequent notes

    Returns
    -------
    notes : numpy.ndarray
        pitches of the notes
    beats : numpy.ndarray
        beat duration of the notes
    tempo : float
        tempo of the melody
    '''
    # onset detection
    onsets = onset.get_onsets(wav, fs, min_distance = min_distance_notes, seconds = False)
    # pitch detection
    freqs = []
    for i in range(onsets.size):
        if i == onsets.size - 1:
            n = wav[onsets[i] :]
        else:        
            n = wav[onsets[i] : onsets[i + 1]]
        freqs.append(yin.get_pitch(n, fs))
    
    notes = []
    for f in freqs:
        notes.append(note.get_pitch_notation(f))
        
    beats, tempo = beat.get_beats(wav, fs, min_beat = min_beat_dur)
    z = np.where(beats == 0)
    notes = np.delete(notes, z)
    beats = np.delete(beats, z)
    
    return notes, beats, tempo

def generate_score(notes, beats, tempo, path, 
                   time_sig = '4/4',
                   clean_up = True,
                   ):
    '''
    Generate PNG image for the music score of the audio file

    Parameters
    ----------
    notes : numpy.ndarray
        pitch of the notes
    beats: numpy.ndarray
        beat durations of the notes
    tempo : float
        tempo of the melody, in bpm
    path : string
        destination path for the image
    time_sig : string
        time signature of the melody
    clean_up : bool
        remove temp files from lilypond        
    Returns
    -------
    None.

    '''
    
    ts = m21.meter.TimeSignature(time_sig)
    ts.symbol = 'common'
    n_measure = ts.denominator
    b_measure = ts.numerator
    
    staves = []
    current_staff = 0
    current_measure = 0
    b_cur = 0
    staves.append(m21.stream.Part())
    m = m21.stream.Measure()
    m.append(ts)
    
    for i, (n, b) in enumerate(zip(notes, beats)):
        b_cur += b
        current_measure += b
        if current_measure > b_measure:
            staves[current_staff].append(m)
            m = m21.stream.Measure()
            current_measure = b
        if b_cur > n_measure * b_measure:
            #if i != len(notes) - 1:
            current_staff += 1
            staves.append(m21.stream.Part())
            b_cur = b
        m.append(m21.note.Note(n, quarterLength = b))
    staves[current_staff].append(m)
    
    score = m21.stream.Score(staves)
    #score.show('lily.png')
    score.write('lily.png', fp=path)
    # clean-up
    if clean_up:
        os.remove(path)
        os.remove(path + '-1.eps')
        os.remove(path + '-systems.count')
        os.remove(path + '-systems.tex')
        os.remove(path + '-systems.texi')
