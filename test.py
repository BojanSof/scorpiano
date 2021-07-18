#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 12 22:06:11 2021
Simple test script
@author: bojan
"""
import transcription
from scipy.io import wavfile
import numpy as np
# MuseScore samples
# sample_path = 'samples/MuseScore/'
# names = {
#             'alphabet' : '4/4',
#             'auld_lang_syne' : '4/4',
#             'canon_in_D' : '4/4',
#             'happy_birthday' : '3/4',
#             'jingle_bells' : '4/4',
#             'london_bridge' : '4/4',
#             'mary_lamb' : '4/4',
#             'ode_to_joy' : '4/4',
#             'silent_night' : '3/4',
#             'twinkle_star' : '4/4'
#           }
# score_base_path = 'samples/generated_scores/MuseScore/'

# electronic piano samples
# sample_path = 'samples/Piano/'
# names = {
#                'alphabet' : '4/4',
#                'auld_lang_syne' : '4/4',
#                'canon_in_D' : '4/4',
#                'happy_birthday' : '3/4',
#                'jingle_bells' : '4/4',
#                'london_bridge' : '4/4',
#                'mary_lamb' : '4/4',
#                'ode_to_joy' : '4/4',
#                'silent_night' : '3/4',
#                'twinkle_star' : '4/4'
#         }
# score_base_path = 'samples/generated_scores/Piano/'
# tempo effect
sample_path = 'samples/Piano_tempo/'
names = {
               'jingle_bells_80' : '4/4',
               'jingle_bells_100' : '4/4',
               'jingle_bells_120' : '4/4',
               'twinkle_star_80' : '4/4',
               'twinkle_star_100' : '4/4',
               'twinkle_star_120' : '4/4'
        }
score_base_path = 'samples/generated_scores/Piano_tempo/'
for name, ts in names.items():
    wav_name = name + '.wav'
    fs, wav = wavfile.read(sample_path + wav_name)
    wav = np.mean(wav, axis = 1)
    wav = np.concatenate((np.zeros(2048), wav))
    wav = wav / 2**15
    score_path = score_base_path + name
    transcription.generate_score(wav, fs, score_path, ts)