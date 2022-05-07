from miditok import *
import pickle


def export_midi(tokens, midi_name):
    """Exports tokens as a MIDI file names midi_name"""

    # This code is duplicated in bar_extractor.py, should be put in common place
    # but idk how.
    _pitch_range = range(21, 109)
    _beat_res = {(0, 4): 8, (4, 12): 4}
    _nb_velocities = 32
    _additional_tokens = {'Chord': False, 'Rest': False, 'Tempo': False, 'Program': False,
                          'TimeSignature': False}

    TOKENIZER = REMI(_pitch_range, _beat_res,
                     _nb_velocities, _additional_tokens)

    converted_back_midi = TOKENIZER.tokens_to_midi(tokens)
    converted_back_midi.dump('generated/MIDI/' + midi_name + '.mid')
    print("Success!")


def bars_to_tokens(bars):
    """Converts lists of bars into valid tokens object"""
    res = [[]]
    for bar in bars:
        for n in bar:
            res[0].append(n)
    return res


def all_bars():
    """Returns all generated bars as 3d list (song, bar number, index)"""
    with open("samples/bars/combined.txt", "rb") as combined_file:
        return pickle.load(combined_file)
