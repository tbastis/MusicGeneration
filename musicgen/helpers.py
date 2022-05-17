import random
import pickle
from miditok import *


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


def phrases_to_measures(phrases):
    """Converts array of phrases to array of measures"""
    result = []
    for phrase in phrases:
        for measure in phrase:
            result.append(measure)
    return result


def all_measures():
    """Returns all generated measures as 3d list (song, measure number, index)"""
    with open("samples/bars/combined.txt", "rb") as combined_file:
        return pickle.load(combined_file)


def is_chord_note(measure, i):
    """
    Given a measure and an index i (which must be a pitch index), returns whether
    the note is part of a chord or not.
    """
    if (len(measure) < i+4):
        return measure[i-1] < 320 # if token before is not a position token
    return 2 <= measure[i+3] and measure[i+3] <= 128


def get_pitch_indices(measure, include_chords):
    """ 
    Returns all pitch indices of the measure, optionally ignoring notes which 
    are part of a chord. 
    """
    pitch_indices = []
    for i in range(len(measure)):
        if (2 <= measure[i] and measure[i] <= 128):
            if (not include_chords and is_chord_note(measure, i)):
                continue
            pitch_indices.append(i) 
    return pitch_indices


def get_position_indices(measure):
    """ Returns all position indices of the measure"""
    position_indices = []
    for i in range(len(measure)):
        if (320 <= measure[i] and measure[i] <= 351):
            position_indices.append(i) 
    return position_indices


def get_velocity_indices(measure):
    """ Returns all velocity indices of the measure"""
    velocity_indices = []
    for i in range(len(measure)):
        if (129 <= measure[i] and measure[i] <= 255):
            velocity_indices.append(i) 
    return velocity_indices


def get_duration_indices(measure):
    """ Returns all duration indices of the measure"""
    duration_indices = []
    for i in range(len(measure)):
        if (255 <= measure[i] and measure[i] <= 287): # assumes 4/4 time 
            duration_indices.append(i) 
    return duration_indices


def best_phrases(phrases, scores, output_len): 
    """
    Find index of output_len highest values in scores and return array of 
    phrases coordinating with those indices.
    """
    result = []
    for _ in range(output_len):
        max_value = max(scores)
        max_index = scores.index(max_value)
        result.append(phrases[max_index])
        scores[max_index] = -1
    return result


def get_target_phrase():
    """
    Returns an example of a "good phrase", for now hard-coded as the first 
    phrase of bach suite no 1. To switch to different phrase, can copy first 4 
    bars from song in samples/bars.
    TODO: Automate this loading
    """
    return [[1, 320, 52, 195, 271, 322, 71, 197, 257, 324, 80, 223, 257, 326, 78, 202, 257, 328, 80, 207, 257, 330, 71, 189, 257, 332, 80, 217, 257, 334, 71, 190, 257, 336, 40, 191, 271, 338, 71, 191, 257, 340, 80, 216, 257, 342, 78, 201, 257, 344, 80, 211, 257, 346, 71, 187, 257, 348, 80, 214, 257, 350, 71, 190, 257],
            [1, 320, 52, 211, 271, 322, 73, 198, 257, 324, 81, 218, 257, 326, 80, 206, 257, 328, 81, 210, 257, 330, 73, 191, 257, 332, 81, 222, 257, 334, 73, 191, 257, 336, 40, 200, 271, 338, 73, 194, 257, 340, 81, 221, 257, 342, 80, 199, 257, 344, 81, 210, 257, 346, 73, 188, 257, 348, 81, 218, 257, 350, 73, 194, 257],
            [1, 320, 52, 211, 271, 322, 75, 199, 257, 324, 81, 215, 257, 326, 80, 197, 257, 328, 81, 204, 257, 330, 75, 194, 257, 332, 81, 212, 257, 334, 75, 193, 257, 336, 40, 198, 271, 338, 75, 197, 257, 340, 81, 214, 257, 342, 80, 201, 257, 344, 81, 206, 257, 346, 75, 195, 257, 348, 81, 217, 257, 350, 75, 193, 257],
            [1, 320, 52, 212, 271, 322, 76, 195, 257, 324, 80, 208, 257, 326, 78, 196, 257, 328, 80, 209, 257, 330, 76, 200, 257, 332, 80, 213, 257, 334, 76, 199, 257, 336, 40, 195, 271, 338, 76, 193, 257, 340, 80, 219, 257, 342, 78, 199, 257, 344, 80, 213, 257, 346, 76, 198, 257, 348, 80, 213, 257, 350, 75, 195, 257]]


def random_measures(n):
    """Generates n random measures of music"""
    all_measures = all_measures()
    res = []
    for _ in range(n):
        res.append(all_measures[random.randint(0, len(all_measures) - 1)])
    return res


def random_midi(length, filename):
    """Exports a midi with random measures, useful for baseline testing"""
    export_midi(measures_to_tokens(random_measures(length)), filename)