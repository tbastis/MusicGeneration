from unittest import result
from miditok import *
import pickle


def export_midi(tokens, midi_name):
    """Exports tokens as a MIDI file names midi_name"""

    # Our parameters
    _pitch_range = range(0, 127)
    _beat_res = {(0, 4): 8, (4, 12): 4}
    _nb_velocities = 127
    _additional_tokens = {'Chord': False, 'Rest': False, 'Tempo': False, 'Program': False,
                        'TimeSignature': False}

    TOKENIZER = REMI(_pitch_range, _beat_res,
                     _nb_velocities, _additional_tokens)

    converted_back_midi = TOKENIZER.tokens_to_midi(tokens)
    converted_back_midi.dump('generated/MIDI/' + midi_name + '.mid')
    print("Success!")

def measures_to_tokens(measures):
    """Converts lists of measures into valid tokens object"""
    res = [[]]
    for measure in measures:
        for i in measure:
            res[0].append(i)
    return res

def phrases_to_measures(phrases, measures):
    """Converts array of phrases to array of measures"""
    result = []
    for phrase_index in range(len(phrases)):
        for i in phrases[phrase_index]:
            measure = measures[i]
            measure.insert(0,1)
            result.append(measure)
    return result

def all_measures():
    """Returns all generated measures as 3d list (song, measure number, index)"""
    with open("samples/bars/combined.txt", "rb") as combined_file:
        return pickle.load(combined_file)

def get_pitch_indices(measure, include_chords):
    """ Returns all pitch indices of the measure, optionally ignoring notes which 
        are part of a chord. """
    pitch_indices = []
    for i in range(len(measure)):
        if (2 <= measure[i] and measure[i] <= 128):
            if (not include_chords and measure[i-1] < 320): # no position before this token indicates chord
                continue
            pitch_indices.append(i) 
    return pitch_indices

def best_phrases(phrases, scores, output_len): 
    """Find index of output_len highest values in scores and return array of 
        phrases coordinating with those indices."""
    result = []
    for _ in range(output_len):
        max_value = max(scores)
        max_index = scores.index(max_value)
        result.append(phrases[max_index])
        scores[max_index] = -1
    return result
