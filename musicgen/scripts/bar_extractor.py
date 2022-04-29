from miditok import *
from miditoolkit import MidiFile
import os
import pickle

# ---------------------------------------------------------------------------- #
# This script takes the MIDI files from musicgen/samples/bar_sources, splits
# each of them into bars (which are saved in their own plaintext files), and
# also combines them all into a serialized file musicgen/samples/bars/combined.txt
# ---------------------------------------------------------------------------- #


def tokens_to_bars(tokens):
    """Splits a list of tokens into a 2d list of individual bars"""
    bars = []
    i1 = 0
    for i2 in range(1, len(tokens)):
        if (tokens[i2] == 1 or i2 == len(tokens) - 1):  # New bar or end of last
            bar = []
            for i in range(i1, i2):
                bar.append(tokens[i])
            if i2 == len(tokens) - 1:
                bar.append(tokens[-1])
            else:
                i1 = i2
            bars.append(bar)
    return bars


# Our parameters
_pitch_range = range(0, 127)
_beat_res = {(0, 4): 8, (4, 12): 4}
_nb_velocities = 127
_additional_tokens = {'Chord': False, 'Rest': False, 'Tempo': False, 'Program': False,
                      'TimeSignature': False}

# Creates the tokenizer and loads a MIDI
TOKENIZER = REMI(_pitch_range, _beat_res,
                 _nb_velocities, _additional_tokens)

combined = []

for midi_name in os.listdir('musicgen/samples/bar_sources'):

    print('Extracting bars from ' + midi_name)
    midi = MidiFile('musicgen/samples/bar_sources/' + midi_name)
    if (midi_name == "pitch_test.mid"):
        print(TOKENIZER.midi_to_tokens(midi))
    tokens = TOKENIZER.midi_to_tokens(midi)[0]

    # Save bars to individual file and combined list in memory
    with open('musicgen/samples/bars/' + midi_name + '_bars.txt', 'w') as filehandle:
        bars = tokens_to_bars(tokens)
        for bar in bars:
            filehandle.write('%s\n' % bar)
            combined.append(bar)

    print('Successfully extracted bars from ' + midi_name + '! \n')

with open("musicgen/samples/bars/combined.txt", "wb") as combined_file:
    pickle.dump(combined, combined_file)
