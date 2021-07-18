#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 16 22:34:19 2021

@author: bojan
"""

from scipy.io import wavfile
import numpy as np
import sys
import os
import transcription

if __name__ == "main":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input melody wav path> (time signature for the score)")
        sys.exit(1)
    fs, wav = wavfile.read(sys.argv[1])
    if wav.ndim == 2:
        wav = np.mean(wav, axis = 1)
    wav = np.concatenate((np.zeros(2048), wav))
    wav = wav / 2**15
    print('opened the wav file')
    if len(sys.argv) == 3:
        ts = sys.argv[2]
    else:
        ts = '4/4'
    score_path = os.path.splitext(sys.argv[1])[0]
    print('transcribing')
    transcription.generate_score(wav, fs, score_path, ts)
    print('end')
    