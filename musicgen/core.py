import helpers
import random


def random_bars(n):
    """Generates n random bars of music"""
    all_bars = helpers.all_bars()
    res = []
    for i in range(n):
        res.append(all_bars[random.randint(0, len(all_bars))])
    return res


# Generate random MIDI file
# Caution: will overwrite files!
helpers.export_midi(helpers.bars_to_tokens(random_bars(10)), 'random_test_4')
