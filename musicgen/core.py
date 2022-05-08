from cmath import inf
import helpers
import random
import sys
import math
import numpy as np

# Default parameter values
iters = 4  # number of generations to run through
# chance that two parents make children (rather than persisting to the next gen)
cross_rate = 50
muta_rate = 10  # update later -- 1/#measures
phrase_len = 4  # number of measures per phrase
output_len = 4 # number of measures you want output to be
output_name = 'default'


def random_measures(n):
    """Generates n random measures of music"""
    all_measures = helpers.all_measures()
    res = []
    for _ in range(n):
        res.append(all_measures[random.randint(0, len(all_measures) - 1)])
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
        assert 0 <= int(temp_cross_rate) and int(temp_cross_rate) <= 100
        global cross_rate
        cross_rate = int(temp_cross_rate)
        print('Value set to ' + str(cross_rate))
    except:
        print('Invalid input, defaulting to ' + str(cross_rate))

    temp_muta_rate = input('\nEnter mutation rate:')
    try:
        assert 0 <= int(temp_muta_rate) and int(temp_muta_rate) <= 100
        global muta_rate
        muta_rate = int(temp_muta_rate)
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
    return [relation_fitness(phrase, measures) + direction_fitness(phrase, measures) 
    + end_fitness(phrase, measures) for phrase in phrases]
    # return [random.randint(0, 100) for _ in range(len(phrases))]

def relation_fitness(phrase, measures):
    """
    Returns the note relationship fitness score for each phrase defined as follows:
    Notes that are closer together sound better. 
    Fitness score is higher if notes are closer together.
    """
    score = 0
    total_notes = 0
    prev_note = 0
    for i in phrase:
        for j in measures[i]:
            if j < 128:
                total_notes += 1
                if prev_note > 0:
                    if abs(j - prev_note) == 0:
                        score += 90
                    elif abs(j - prev_note) <= 4:
                        score += 100
                    elif abs(j - prev_note) <= 6:
                        score += 80
                    elif abs(j - prev_note) <= 8:
                        score += 70
                    else:
                        score += 50
                prev_note = j
    return score / (total_notes - 1)

def direction_fitness(phrases, measures):
    """
    Returns the contour fitness score for each phrase defined as follows:
    Notes that form a rising melody or falling melody score highest
    Stable melodies score high
    Unstable melodies score low
    """
    score = 0
    total_notes = 0
    prev_note1 = 0
    prev_note2 = 0
    for i in phrases:
        for j in measures[i]:
            if j < 128:
                total_notes += 1
                if j < prev_note1 & prev_note1 < prev_note2:
                    score += 100
                elif j > prev_note1 & prev_note1 > prev_note2:
                    score += 100
                elif j == prev_note1 & prev_note1 == prev_note2:
                    score += 90
                else:
                    score += 70
                prev_note2 = prev_note1
                prev_note1 = j
    return score / (total_notes - 2)

def end_fitness(phrase, measures):
    """
    Returns the end note fitness score of the phrase.
    Phrase scores high if the end note is the same as the start note.
    Phrase scores lower if the end note is different than the start note.
    """
    for i in measures[phrase[0]]:
        if i < 128:
            first_note = i
            break
    
    for i in measures[phrase[len(phrase) - 1]]:
        if i < 128:
            last_note = i
    
    if last_note == first_note:
        return 100
    else:
        return 70


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

def mutate(phrase, measures, muta_rate):
    """
    returns mutated measures within the given phrase with a probability of `muta_rate`.
    """
    if random.randint(0, 100) < muta_rate:

        phrase_index = random.randint(0, phrase_len - 1)
        pitch_indices = helpers.get_pitch_indices(measures[phrase[phrase_index]], False)

        match random.randint(0, 6):
            case 0:
                # reverse pitches of notes within the phrase
                i = 0
                j = len(pitch_indices) - 1
                while (i < j):
                    temp = measures[phrase[phrase_index]][pitch_indices[i]] 
                    measures[phrase[phrase_index]][pitch_indices[i]] = measures[phrase[phrase_index]][pitch_indices[j]] 
                    measures[phrase[phrase_index]][pitch_indices[j]] = temp
                    i+=1
                    j-=1

            case 1|2: 
                #transposition: raise or lower pitch of all notes  in phrase by same amount
                change = int(np.random.normal(0, 10, 1)[0])
                for i in range(len(pitch_indices)):
                    measures[phrase[phrase_index]][pitch_indices[i]] += change

            case 3|4:
                # raise or lower pitch of 1 note
                change = int(np.random.normal(0, 10, 1)[0])
                note_index = random.randint(0, len(pitch_indices) - 1)
                for i in range(len(pitch_indices)):
                    measures[phrase[phrase_index]][pitch_indices[note_index]] += change

            case 5|6:
                #One note randomly matches the pitch of another note
                note1_index = random.randint(0, len(pitch_indices) - 1)
                note2_index = random.randint(0, len(pitch_indices) - 1)
                measures[phrase[phrase_index]][pitch_indices[note1_index]] = measures[phrase[phrase_index]][pitch_indices[note2_index]] 

    return measures
     

def crossover_rand(p1, p2, cross_rate):
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

def crossover_min_dist(p1, p2, cross_rate, measures):
    """
    Crossover two parents with some probability to create 
    new children. Otherwise, the parents are carried through
    to the next generation.

    Crossover point is determined by the index at which the starting and 
    ending notes between the two phrases (that would be consecutive if we crossed
    over at this point) differ the least in pitch.

    Returns two children in an array [child1, child2]
    """
    c1, c2 = p1.copy(), p2.copy()
    if random.randint(0, 100) <= cross_rate:
        cross_point = 0
        least_dist = math.inf
        for i in range(phrase_len):
            if i == 0: continue #skip comparing first one 

            end_c1n = measures[c1[i-1]][-3] #pitch of final note in child 1 measure before
            start_c2n = measures[c2[i]][1] #pitch of first note in child 2 current measure

            end_c2n = measures[c2[i-1]][-3] #pitch of final note in child 2 measure before
            start_c1n = measures[c2[i]][1] #pitch of first note in child 1 current measure

            dist = abs(end_c1n - start_c2n) + abs(end_c2n + start_c1n)
            
            if (dist < least_dist):
                cross_point = i
                least_dist = dist

            #possible problem: ignores duration --> simultaneous notes?

        c1 = p1[:cross_point:] + p2[cross_point:]
        c2 = p2[:cross_point:] + p1[cross_point:]
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

    data = helpers.all_measures()
    phrases, measures = generate_pop(data)
    pop_size = len(phrases)

    #begin genetic stuff
    for curr_gen in range(iters):
        scores = fitness(phrases, measures)

        fitness_threshold = np.median(scores)
        print(">gen%d, new median score = %.3f" % (curr_gen, fitness_threshold))

        # fitness_threshold = 200

        parents = []
        for i in range(len(phrases)):
            if scores[i] > fitness_threshold:
                parents.append(phrases[i])

        # # find best child
        # for i in range(len(phrases)):
        #     if scores[i] > best_score:
        #         best_child, best_score = phrases[i], scores[i]
        #         print(">gen%d, new best %s = %.3f" %
        #               (curr_gen,  best_child, best_score))

        # find parents
        # parents = [select_parents(phrases, scores, 3) for _ in range(pop_size)]
        

        # create next generation
        children = []
        for j in range(0, pop_size, 2):
            # skip iteration if single parent
            if j >= len(parents) - 2:
                continue

            p1, p2 = parents[j], parents[j+1]

            for c in crossover_min_dist(p1, p2, cross_rate, measures):
                measures = mutate(c, measures, muta_rate)
                children.append(c)

        phrases = children
        
    
    scores = fitness(phrases, measures)
    best_phrases = helpers.best_phrases(phrases, scores, output_len)
    best_measures = helpers.phrases_to_measures(best_phrases, measures)
    tokens = helpers.measures_to_tokens(best_measures)
    print(tokens)
    helpers.export_midi(tokens, output_name)

if __name__ == "__main__":
    main()

# Generate random MIDI file
# Caution: will overwrite files!
# helpers.export_midi(helpers.measures_to_tokens(random_measures(10)), 'random_test_4')

def random_midi():
    helpers.export_midi(helpers.measures_to_tokens(
        random_measures(10)), 'random_test_4')
