#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 16:36:01 2021
Notes recognition from piano track

Utilities for audio processing
@author: bojan
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy import fftpack as fp
import scipy.signal as sig

def load_wav(wav_path):
    """
    Loading wav file given its path and normalising it
    Also converts stereo audio to mono

    Parameters
    ----------
    wav_path : string
        Path to the wav file

    Returns
    -------
    fs : int
        Sampling rate of the wav file.
    wav : np.ndarray
        The data read from the wav file
    """
    fs, wav = wavfile.read(wav_path)
    if wav.ndim == 2:
        wav = np.mean(wav, axis = 1)
    return fs, wav/np.power(2, 15)

def normalise_wav(wav, level):
    '''
    Normalise the wav signal to the given level

    Parameters
    ----------
    wav : numpy.ndarray
        The wav signal.
    level : float
        The normalisation level in dB

    Returns
    -------
    wav_norm : numpy.ndarray
        The normalised wav signal

    '''
    new_amp = np.power(10, level/20)
    return new_amp / np.max(np.abs(wav)) * wav

def get_spectrum(wav, fs, n_fft = None, plot = False, dB = True):
    '''
    Calculates the amplitude and phase spectrum of given signal

    Parameters
    ----------
    wav : numpy.ndarray
        Values representing the amplitude of wav audio
    fs : int
        Sampling frequency, in Hertz
    n_fft : int, optional
        Number of points for calculating fft. The default is None.
    plot : bool, optional
        Plot the spectrums. The default is False.
    dB : bool, optional
        Calculate the amplitude spectrum in decibels. The default is True
    Returns
    -------
    f : numpy.ndarray
        Array containing the frequencies for which the spectrums are
        calculated
    wav_amp : numpy.ndarray
        The amplitude spectrum
    wav_ph : numpy.ndarray
        The phase spectrum

    '''
    if n_fft == None:
        n_fft = np.int(np.power(2, np.ceil(np.log2(wav.size))))
        
    wav_fft = fp.fft(wav, n_fft)
    n_keep = n_fft // 2 + 1
    wav_fft = wav_fft[0 : n_keep] / wav.size
    wav_fft[1 : -1] = 2 * wav_fft[1 : -1]
    
    wav_amp = np.abs(wav_fft)
    if dB:
        wav_amp[wav_amp < np.finfo(np.float).eps] = np.finfo(np.float).eps
        wav_amp = 20 * np.log10(wav_amp)
    
    wav_ph = np.unwrap(np.angle(wav_fft))
    
    f = np.linspace(0, fs/2, n_keep)
    
    if plot:
        plt.figure(figsize = (15, 10))
        plt.subplot(2, 1, 1)
        plt.plot(f, wav_amp)
        plt.ylabel(r'$|H(f)|$ [dB]')
        plt.grid()
        plt.subplot(2, 1, 2)
        plt.plot(f, wav_ph)
        plt.xlabel('f [Hz]')
        plt.ylabel(r'$\angle{H(f)}$ [rad]')
        plt.grid()
        
    return f, wav_amp, wav_ph

def get_spectrogram(wav, fs, 
                    n_win = 2048, n_hop = None, win_type = 'hann', 
                    plot = False):
    '''
    Calculates the spectrogram of a signal

    Parameters
    ----------
    wav : numpy.ndarray
        Values representing the amplitude of wav audio
    fs : int
        Sampling frequency, in Hertz
    n_win : int, optional
        Window size. The default is 2048.
    n_hop : TYPE, optional
        Hop size. The default is None.
    win_type : TYPE, optional
        Window type. The default is 'hann'.
    plot : bool, optional
        Plot the spectrogram. The default is False.

    Returns
    -------
    t_frames : numpy.ndarray
        Time axis of the spectrogram
    f_frame : numpy.ndarray
        Frequency axis of the spectrogram
    spectrogram : numpy.ndarray
        2D array containing each frame spectrum at seperate column

    '''
    if n_hop == None:
        n_hop = n_win // 2
    pad = np.zeros(n_win // 2)
    wav_pad = np.concatenate((pad, wav, pad))
    win = sig.get_window(win_type, n_win)
    
    pos = 0
    while pos < wav_pad.size - n_win:
        frame = wav_pad[pos : pos + n_win] * win
        f_frame, frame_amp, frame_ph = get_spectrum(frame, fs, n_win, plot = False)
        frame_amp = frame_amp[:, np.newaxis]
        if pos == 0:
            spectrogram = frame_amp
        else:
            spectrogram = np.concatenate((spectrogram, frame_amp), axis = 1)
        pos += n_hop
        
    t_frames = np.arange(spectrogram.shape[1]) * n_hop / fs
    
    if plot:
        plot_spectrogram(t_frames, f_frame, spectrogram)
        
    return t_frames, f_frame, spectrogram

def plot_spectrogram(t_frames, f_frame, spectrogram, f_max = None, 
                     save_path = None, title = None):
    '''
    Plots the spectrogram

    Parameters
    ----------
     t_frames : numpy.ndarray
        Time axis of the spectrogram
    f_frame : numpy.ndarray
        Frequency axis of the spectrogram
    spectrogram : numpy.ndarray
        2D array containing each frame spectrum at seperate column
    f_max : int, optional
        Maximum frequency for frequency axis. The default is None.

    Returns
    -------
    None.

    '''
    if f_max is None:
        f_max = f_frame[-1]
    plt.figure(figsize=(10, 8))
    plt.imshow(
        spectrogram,
        aspect='auto',
        origin='lower',
        extent=[0, t_frames[-1], 0, f_max],
        vmin = -100, vmax = 0
        )
    cbar = plt.colorbar()
    plt.xlabel(r'$t$ [s]')
    plt.ylabel(r'$f$ [Hz]')
    cbar.ax.set_ylabel('dB')
    plt.axis([0, t_frames[-1], 0, f_max])
    plt.title(title)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)

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

A4 = 440
C0 = A4 * np.power(2, -4.75)
note_name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
def pitch(note_freq):
    '''
    Generates the pitch notation of note, given its frequency

    Parameters
    ----------
    note_freq : float
        Note frequency in Hertz

    Returns
    -------
    string
        Pitch notation of the note

    '''
    h = int(np.round(12*np.log2(note_freq/C0)))
    octave = h // 12
    n = h % 12
    return note_name[n] + str(octave)        