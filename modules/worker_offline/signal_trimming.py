#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 17:32:23 2018

@author: rbaraglia
"""
import sys
import os
from pydub import AudioSegment


def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=100):
    '''
    sound is a pydub.AudioSegment
    silence_threshold in dB
    chunk_size in ms

    iterate over chunks until you find the first one with sound
    '''
    trim_ms = 0 # ms

    assert chunk_size > 0 # to avoid infinite loop
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size
    return trim_ms

def average_power_level(sound, chunk_size=100):
    trim_ms = 0 # ms
    nb_chunk = 0
    avg_power = 0.0
    assert chunk_size >0
    while trim_ms < len(sound):
        trim_ms += chunk_size
        if (sound[trim_ms:trim_ms+chunk_size].dBFS != -float('Inf')):
            avg_power += sound[trim_ms:trim_ms+chunk_size].dBFS
            nb_chunk += 1
    avg_power = avg_power/nb_chunk
    return avg_power

    '''
    trim_silence_segments remove silence (or background noise) from an audio wav file.
    It working by trimming signal at the beginning and the end that is below the overall power level
    input_file is a .wav file path
    output_file is a .wav file path
    chunk_size in ms
    threshold_factor ]0,1]
    side_effect_accomodation is a number of chunk that will be kept at the beginning and end despite being below the threshold
    return the silence segment
    
    '''
def trim_silence_segments(input_file,output_file, chunk_size=100, threshold_factor=0.85, side_effect_accomodation=0):
    #sound = AudioSegment.from_file("/home/rbaraglia/data/SG/audio-18_01_18/rec---2018-01-18_081957.wav", format="wav")
    sound = AudioSegment.from_file(input_file, format="wav")
    avg_power = average_power_level(sound)
    start_trim = detect_leading_silence(sound,silence_threshold= threshold_factor * avg_power)
    end_trim = detect_leading_silence(sound.reverse(), silence_threshold= threshold_factor * avg_power)
    
    duration = len(sound)
    trimmed_sound = sound[start_trim if start_trim - chunk_size*side_effect_accomodation < 0 else start_trim - chunk_size*side_effect_accomodation : duration-end_trim if end_trim + chunk_size*side_effect_accomodation > duration else duration-end_trim + chunk_size*side_effect_accomodation]
    trimmed_sound.export(output_file, format="wav")
    return (sound[0 : start_trim], sound[len(sound) - end_trim : -1])

if __name__ == '__main__':
    [silence1, silence2] = trim_silence_segments(sys.argv[1], sys.argv[2])
    # If you want to retrieve silence segment put a path as a third argument .../folder/
    if len(sys.argv) == 4:
        silence1.export(sys.argv[3] + os.path.basename(sys.argv[1]).split('.')[0] + "beg_sil.wav", format="wav")
        silence2.export(sys.argv[3] + os.path.basename(sys.argv[1]).split('.')[0] + "end_sil.wav", format="wav")