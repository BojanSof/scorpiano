#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  8 21:55:08 2021
Tempo detection

@author: bojan
"""

import librosa

def get_tempo(x, fs):
    return librosa.beat.tempo(x, fs)