import helpers
import random
import sys

# Default parameter values
iters = 5  # number of generations to run through
# chance that two parents make children (rather than persisting to the next gen)
cross_rate = 0.9
muta_rate = 1  # update later -- 1/#measures
phrase_len = 4  # number of measures per phrase


def random_bars(n):
    """Generates n random bars of music"""
    all_bars = helpers.all_bars()
    res = []
    for _ in range(n):
        res.append(all_bars[random.randint(0, len(all_bars))])
    return res
    

def setParameters():
    if (len(sys.argv) != 2):
        return
    if (sys.argv[1] != '-c'):
        return

    temp_iters = input('\nEnter number of generations:')
    try:
        assert int(temp_iters) > 0
        global iters
        iters = int(temp_iters)
        print('Value set to ' + str(iters))
    except:
        print('Invalid input, defaulting to ' + str(iters))

    temp_cross_rate = input('\nEnter cross rate:')
    try:
        assert 0 <= float(temp_cross_rate) and float(temp_cross_rate) <= 1
        global cross_rate
        cross_rate = float(temp_cross_rate)
        print('Value set to ' + str(cross_rate))
    except:
        print('Invalid input, defaulting to ' + str(cross_rate))

    temp_muta_rate = input('\nEnter mutation rate:')
    try:
        assert 0 <= float(temp_muta_rate) and float(temp_muta_rate) <= 1
        global muta_rate
        muta_rate = float(temp_muta_rate)
        print('Value set to ' + str(muta_rate))
    except:
        print('Invalid input, defaulting to ' + str(muta_rate))

    temp_phrase_len = input('\nEnter phrase length:')
    try:
        assert int(temp_phrase_len) > 0
        global phrase_len
        phrase_len = int(temp_phrase_len)
        print('Value set to ' + str(phrase_len))
    except:
        print('Invalid input, defaulting to ' + str(phrase_len))


def fitness(phrases, measures):
    """
    Returns a fitness score for each phrase

    - Trivial implementation at the moment
    """

    # TODO: modify mutation rate as we get further on in generations/fitness scores
    random.seed()
    return [random.randint(0, 100) for _ in range(len(phrases))]


def select_parents(parents, scores, num):
    """
    Given an array of parents and scores, returns the index of the best
    parent out of a random selection of `num` parents
    """
    best_parent = random.randint(0, len(parents)-1)  # random initialization

    random_parents = random.sample(range(0, len(parents)-1), num-1)
    for i in random_parents:
        if scores[i] < scores[best_parent]:
            best_parent = i 
        
    return best_parent

def mutation(c, muta_rate):
    """
    Returns the a mutated phrase, with mutation happening
    with a probability of `muta_rate`.
    """
    if random.randint(0, 100) < muta_rate:
        case = random.randint(0, 5)
        match case:
            case 1:
                #retrograde: prime in reverse order (last to first, first to last)
                c = c[::-1]

            case 2: 
                #inversion 
                pass

            case 3: 
                pass
            #transposition

            case 4:
                pass
            #sequencing
        pass
    
    return c
     

def crossover(p1, p2, cross_rate):
    """
    Crossover two parents with some probability to create 
    new children. Otherwise, the parents are carried through
    to the next generation.

    Returns two children in an array [child1, child2]
    """
    c1, c2 = p1.copy(), p2.copy()
    if random.randint(0, 100) <= cross_rate:
        cross_point = random.randint(1, len(p1)-2)

        c1 = p1[cross_point:] + p2[:cross_point]
        c2 = p2[cross_point:] + p1[:cross_point]

    #compare 4x4xmeasure_len ~ 4x4x4

    return [c1, c2]

def crossover_genjam(p1, p2, cross_rate, measures):
    """
    Crossover two parents with some probability to create 
    new children. Otherwise, the parents are carried through
    to the next generation.

    Crossover point is determined by the index at which the starting and 
    ending notes between the two phrases differ the least.

    Returns two children in an array [child1, child2]
    """
    c1, c2 = p1.copy(), p2.copy()
    if random.randint(0, 100) <= cross_rate:
        cross_point = 0
        for i in range(phrase_len):
            if i == 0: continue #skip comparing first one 

            end_c1n = measures[c1[i]][:-1][1] #child1's ending note
            start_c2n = measures[c2[i]][0][1] #child2's starting note

            old_best = measures[c2[cross_point]][0][1] - measures[c1[cross_point]][:-1][1]
            if start_c2n - end_c1n <= old_best:
                cross_point = i
            #possible problem: ignores duration --> simultaneous notes

        c1 = p1[cross_point:] + p2[:cross_point]
        c2 = p2[cross_point:] + p1[:cross_point]
    return [c1, c2]


def generate_pop(data):
    """
    Returns a tuple containing an array of phrases, measures.

    Each phrase is an index of the measures array, indicating
    which measures compose that phrase.
    """
    phrases = []
    measures = []

    curr_len = 0  # tracks number of measures in current phrase
    temp_phrase = []
    index = 0
    for i in range(len(data)):  # For each song
        for j in range(len(data[i])):
            measure = data[i][j][1:]  # chop off the 1
            measures.append(measure)

            temp_phrase += [index]
            index += 1

            # append to phrases if current phrase is long enough
            curr_len = (curr_len+1) % phrase_len
            if curr_len == 0:
                phrases += [temp_phrase]
                temp_phrase = []

        # drop the last phrase if it's too short (doesn't contain enough measures)
        temp_phrase = []
        curr_len = 0

    # for i in range(100):
    #     print(measures[i])
    #     print("\n")

    # print(phrases)

    return phrases, measures


def main():
    setParameters()

    data = helpers.all_bars()
    phrases, measures = generate_pop(data)
    pop_size = len(phrases)

    #begin genetic stuff
    best_child, best_score = 0, 0
    for curr_gen in range(iters):
        scores = fitness(phrases, measures)

        # find best child
        for i in range(len(phrases)):
            if scores[i] > best_score:
                best_child, best_score = phrases[i], scores[i]
                print(">gen%d, new best %s = %.3f" %
                      (curr_gen,  best_child, best_score))

        # find parents
        parents = [select_parents(phrases, scores, 3) for _ in range(pop_size)]

        # create next generation
        children = []
        for j in range(0, pop_size, 2):
            # skip iteration if single parent
            if j >= len(parents) - 2:
                continue

            p1, p2 = phrases[parents[j]], phrases[parents[j+1]]

            for c in crossover(p1, p2, cross_rate):
                child = mutation(c, muta_rate)
                children.append(child)

        phrases = children

    return [best_child, best_score]


if __name__ == "__main__":
    main()

# Generate random MIDI file
# Caution: will overwrite files!
# helpers.export_midi(helpers.bars_to_tokens(random_bars(10)), 'random_test_4')


def random_midi():
    helpers.export_midi(helpers.bars_to_tokens(
        random_bars(10)), 'random_test_4')
