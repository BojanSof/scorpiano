#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 18 14:59:27 2021
Convert pitch and beat duration to midi
@author: bojan
"""

from midiutil import MIDIFile

def get_midi_number(pitch_notation):
    '''
    Returns the midi number of the note, given its pitch notation

    Parameters
    ----------
    pitch_notation : string
        Pitch notation of the note

    Returns
    -------
    midi_number : int
        midi number of the note (0 <= midi_number <= 127)

    '''
    note_name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    note_number = note_name.index(pitch_notation[:-1])
    note_octave = int(pitch_notation[-1])
    midi_number = (note_octave + 1) * len(note_name) + note_number
    return midi_number

def generate_midi(notes, beats, tempo, midi_path):
    '''
    Convert wav file to midi

    Parameters
    ----------
    notes : numpy.ndarray
        pitch of the notes
    beats: numpy.ndarray
        beat durations of the notes
    tempo : float
        tempo of the melody, in bpm
    midi_path : string
        output path for midi file

    Returns
    -------
    None.

    '''
    track    = 0
    channel  = 0
    time     = 0   # In beats
    volume   = 100 # 0-127, as per the MIDI standard
    
    MyMIDI = MIDIFile(1) # One track, defaults to format 1 (tempo track
                         # automatically created)
    MyMIDI.addTempo(track,time, tempo)
    
    for pitch, duration in zip(notes, beats):
        midi_number = get_midi_number(pitch)
        MyMIDI.addNote(track, channel, midi_number, time, duration, volume)
        time += duration
    
    with open(midi_path, "wb") as output_file:
        MyMIDI.writeFile(output_file)