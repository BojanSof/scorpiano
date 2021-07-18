#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 14:59:46 2021
Create MusicXML file
@author: bojan
"""

import music21 as m21

def midi2musicXML(midi_path, xml_path):
    """
    Create musicXML file from MIDI file

    Parameters
    ----------
    midi_path : str
        Path to MIDI file
    xml_path : str
        Output path for XML file

    Returns
    -------
    None.

    """
    score = m21.converter.parse(midi_path)
    score.write('mxl', xml_path)