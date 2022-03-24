from miditok import REMI, get_midi_programs
from miditoolkit import MidiFile
import isobar as iso

# Our parameters
pitch_range = range(21, 109)
beat_res = {(0, 4): 8, (4, 12): 4}
nb_velocities = 32
additional_tokens = {'Chord': True, 'Rest': True, 'Tempo': True, 'Program': False, 'TimeSignature': False,
                     'rest_range': (2, 8),  # (half, 8 beats)
                     'nb_tempos': 32,  # nb of tempo bins
                     'tempo_range': (40, 250)}  # (min, max)

# Creates the tokenizer and loads a MIDI
tokenizer = REMI(pitch_range, beat_res, nb_velocities, additional_tokens)
midi = MidiFile('musicgen/samples/elise.mid')

# Converts MIDI to tokens, and back to a MIDI
tokens = tokenizer.midi_to_tokens(midi)
converted_back_midi = tokenizer.tokens_to_midi(tokens, get_midi_programs(midi))
converted_back_midi.dump('musicgen/generated/test.mid')
