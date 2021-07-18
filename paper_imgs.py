#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  4 20:23:24 2021
Onset detection for simple monophonic piano track
Using energy novelty function

@author: bojan
"""

import os
from utilities import *
import numpy as np
from scipy.io import wavfile
from scipy import signal as sig
import matplotlib.pyplot as plt
import librosa
from scipy.ndimage import filters
from onset import *
import yin

def noise_filter(wav, fs, fl = 8000):
    h = sig.firwin(511, fl, pass_zero = True, fs = fs)
    wav_f = sig.lfilter(h, 1, wav)
    return wav_f

sample_path = 'samples/MuseScore/twinkle_star.wav'

fs, wav = wavfile.read(sample_path)
wav = np.mean(wav, axis = 1)
wav = np.concatenate((np.zeros(2048), wav))
wav = wav / 2**15
#%% wav plotting for envelope
wav_note = wav[int(3.6 * fs) : int(5) * fs]
wav_note[:int(0.05 * fs)] = 0
wav_note[int(1*fs) : ] = 0
wav_note = wav_note[:int(fs):2]
plt.figure(figsize = (10, 8))
plt.plot(np.arange(wav_note.size)/fs, wav_note)
# #wav = normalise_wav(wav, 0)
#%% onset plot
wav_crop = wav[int(fs*4.8) : int(fs*15)]
e = local_energy(wav_crop)
en = energy_novelty(wav_crop, log = True, norm = True)
t = np.arange(0, wav_crop.size) / fs
plt.figure(figsize = (8, 8))
plt.subplot(2,1,1)
plt.plot(t, e, lw=1.5)
plt.title('Local energy function')
plt.subplot(2,1,2)
plt.plot(t, en, lw=1.5)
plt.title('Energy novelty function')
min_distance = int((0.1) * fs) # 0.1 s
peaks = find_peaks(en, threshold = 0.1, min_distance = min_distance)
plt.plot(t[peaks], en[peaks], 'x')
plt.xlabel('time [s]')
plt.tight_layout()
#%% spectogram pitch detection plot
fs, wav_a4 = wavfile.read('samples/A4_piano.wav')
wav_a4 = wav_a4 / 2**15
wav_a4 = np.mean(wav_a4, axis = 1)
n_win = 3000
f_pitch = yin.get_pitch(wav_a4, fs, n_win = n_win)
t, f, spectrogram = get_spectrogram(wav_a4, fs, n_win = n_win, win_type = 'hann')
f_max = f[-1]
plt.figure(figsize=(10, 8))
plt.imshow(
    spectrogram,
    aspect='auto',
    origin='lower',
    extent=[0, t[-1], 0, f_max],
    vmin = -80, vmax = 0
)
cbar = plt.colorbar()
plt.xlabel(r'$t$ [s]')
plt.ylabel(r'$f$ [Hz]')
cbar.ax.set_ylabel('dB')
plt.axis([t[1], t[-5], 0, 3000])
plt.plot(t, f_pitch, lw = 4.5, color='black', alpha=0.9)
#plt.title("Spectogram of A4 note played on piano, ploted with YIN pitch contour")
plt.tight_layout()
#%% spectogram pitch detection on melody
# important: uncomment return pitch in yin.py
sample_path = 'samples/MuseScore/silent_night.wav'

fs, wav = wavfile.read(sample_path)
wav = np.mean(wav, axis = 1)
wav = np.concatenate((np.zeros(2048), wav))
wav = wav / 2**15
wav_crop = wav[int(fs*0) : int(fs*10)]
n_win = 3000
f_pitch = yin.get_pitch(wav_crop, fs, n_win = n_win)
t, f, spectrogram = get_spectrogram(wav_crop, fs, n_win = n_win, win_type = 'hann')
f_max = f[-1]
plt.figure(figsize=(10, 8))
plt.imshow(
    spectrogram,
    aspect='auto',
    origin='lower',
    extent=[0, t[-1], 0, f_max],
    vmin = -80, vmax = 0
)
cbar = plt.colorbar()
plt.xlabel(r'$t$ [s]')
plt.ylabel(r'$f$ [Hz]')
cbar.ax.set_ylabel('dB')
plt.axis([t[0], t[-1], 0, 2000])
plt.plot(t, f_pitch, lw = 4.5, color='black', alpha=0.9)
plt.tight_layout()