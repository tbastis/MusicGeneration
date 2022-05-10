from cmath import inf
import helpers
import random
import sys
import math
import numpy as np

# Default parameter values
iters = 25  # number of generations to run through
# chance that two parents make children (rather than persisting to the next gen)
cross_rate = 70
muta_rate = 100  # update later -- 1/#measures
phrase_len = 4  # number of measures per phrase
output_len = 16 # number of measures you want output to be
file_name = 'default'


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

    temp_file_name = input('\nEnter output filename: ')
    try:
        assert len(str(temp_file_name)) >= 1
        global file_name
        file_name = str(temp_file_name)
        print('Value set to ' + file_name)
    except:
        print('Invalid input, defaulting to ' + file_name)

    temp_iters = input('\nEnter number of generations: ')
    try:
        assert int(temp_iters) > 0
        global iters
        iters = int(temp_iters)
        print('Value set to ' + str(iters))
    except:
        print('Invalid input, defaulting to ' + str(iters))

    temp_cross_rate = input('\nEnter cross rate: ')
    try:
        assert 0 <= int(temp_cross_rate) and int(temp_cross_rate) <= 100
        global cross_rate
        cross_rate = int(temp_cross_rate)
        print('Value set to ' + str(cross_rate))
    except:
        print('Invalid input, defaulting to ' + str(cross_rate))

    temp_muta_rate = input('\nEnter mutation rate: ')
    try:
        assert 0 <= int(temp_muta_rate) and int(temp_muta_rate) <= 100
        global muta_rate
        muta_rate = int(temp_muta_rate)
        print('Value set to ' + str(muta_rate))
    except:
        print('Invalid input, defaulting to ' + str(muta_rate))

    temp_phrase_len = input('\nEnter phrase length: ')
    try:
        assert int(temp_phrase_len) > 0
        global phrase_len
        phrase_len = int(temp_phrase_len)
        print('Value set to ' + str(phrase_len))
    except:
        print('Invalid input, defaulting to ' + str(phrase_len))

    temp_output_len = input('\nEnter desired output length (in measures): ')
    try:
        assert int(temp_output_len) >= phrase_len
        global output_len
        output_len = int(temp_output_len)
        print('Value set to ' + str(output_len))
    except:
        print('Invalid input, defaulting to ' + str(output_len))


def fitness(phrases):
    """
    Returns a fitness score for each phrase

    - Trivial implementation at the moment
    """

    # TODO: modify mutation rate as we get further on in generations/fitness scores
    return [(relation_fitness(phrase) + direction_fitness(phrase) 
    + end_fitness(phrase))/3 for phrase in phrases]

def relation_fitness(phrase):
    """
    Returns the note relationship fitness score for each phrase defined as follows:
    Notes that are closer together sound better. 
    Fitness score is higher if notes are closer together.
    """
    score = 0
    total_notes = 0
    prev_note = 0
    for measure in phrase:
        for token in measure:
            if (2 <= token and token <= 128):
                note = token
                total_notes += 1
                if prev_note > 0:
                    if abs(note - prev_note) == 0:
                        score += 90
                    elif abs(note - prev_note) <= 4:
                        score += 100
                    elif abs(note - prev_note) <= 6:
                        score += 90
                    elif abs(note - prev_note) <= 8:
                        score += 80
                    else:
                        score += 70
                prev_note = note
    return score / (total_notes - 1)

def direction_fitness(phrase):
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
    for measure in phrase:
        for token in measure:
            if (2 <= token and token <= 128):
                note = token
                total_notes += 1
                if note < prev_note1 & prev_note1 < prev_note2:
                    score += 100
                elif note > prev_note1 & prev_note1 > prev_note2:
                    score += 100
                elif note == prev_note1 & prev_note1 == prev_note2:
                    score += 90
                else:
                    score += 80
                prev_note2 = prev_note1
                prev_note1 = note
    return score / (total_notes - 2)

def end_fitness(phrase):
    """
    Returns the end note fitness score of the phrase.
    Phrase scores high if the end note is the same as the start note.
    Phrase scores lower if the end note is different than the start note.
    """
    # for i in measures[phrase[0]]:
    #     if i < 128:
    #         first_note = i
    #         break
    
    # for i in measures[phrase[len(phrase) - 1]]:
    #     if i < 128:
    #         last_note = i
    
    if phrase[0][2] == phrase[-1][-3]:
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

def mutate(phrase, muta_rate):
    """
    Mutates the given phrase in some way with with a probability of `muta_rate`.
    """
    if random.randint(0, 100) < muta_rate:

        measure = random.randint(0, phrase_len - 1)
        pitch_indices = helpers.get_pitch_indices(phrase[measure], include_chords=False)

        match random.randint(0, 6):
            case 0:
                # reverse pitches of notes within the measure
                i = 0
                j = len(pitch_indices) - 1
                while (i < j):
                    temp = phrase[measure][pitch_indices[i]] 
                    phrase[measure][pitch_indices[i]] = phrase[measure][pitch_indices[j]] 
                    phrase[measure][pitch_indices[i]] = temp
                    i+=1
                    j-=1

            case 1|2: 
                #transposition: raise or lower pitch of all notes in measure by same amount
                change = int(np.random.normal(0, 8, 1)[0])
                if (change < -20):
                    change = -20
                if (change > 20):
                    change = 20
                for i in range(len(pitch_indices)):
                    pitch = phrase[measure][pitch_indices[i]] + change
                    if (pitch < 2 or 128 < pitch):
                        phrase[measure][pitch_indices[i]] -= change
                    else:
                        phrase[measure][pitch_indices[i]] += change
                    

            case 3|4:
                # raise or lower pitch of 1 note in measure
                change = int(np.random.normal(0, 8, 1)[0])
                if (change < -20):
                    change = -20
                if (change > 20):
                    change = 20
                note_index = random.randint(0, len(pitch_indices) - 1)
                pitch = phrase[measure][pitch_indices[note_index]] + change
                if (pitch < 2 or 128 < pitch):
                    phrase[measure][pitch_indices[note_index]] -= change
                else:
                    phrase[measure][pitch_indices[note_index]] += change

            case 5|6:
                # One note randomly changes to match the pitch of another note
                note1_index = random.randint(0, len(pitch_indices) - 1)
                note2_index = random.randint(0, len(pitch_indices) - 1)
                phrase[measure][pitch_indices[note1_index]] = phrase[measure][pitch_indices[note2_index]] 
     

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

def crossover_min_dist(parent1, parent2, cross_rate):
    """
    Crossover two parents with some probability to create 
    new children. Otherwise, the parents are carried through
    to the next generation.

    Crossover point is determined by the index at which the starting and 
    ending notes between the two phrases (that would be consecutive if we crossed
    over at this point) differ the least in pitch.

    Returns two children in an array [child1, child2]
    """

    child1, child2 = parent1.copy(), parent2.copy()

    if random.randint(0, 100) <= cross_rate:
        cross_point = 0
        least_dist = math.inf
        for i in range(phrase_len):
            if i == 0: continue #skip comparing first one 

            end_p1n = parent1[i-1][-3] #pitch of final note in parent 1 measure before
            start_p2n = parent2[i][2] #pitch of first note in parent 2 current measure

            end_p2n = parent2[i-1][-3] #pitch of final note in parent 2 measure before
            start_p1n = parent1[i][2] #pitch of first note in parent 1 current measure

            dist = abs(end_p1n - start_p2n) + abs(end_p2n + start_p1n)
            
            if (dist < least_dist):
                cross_point = i
                least_dist = dist

        child1 = parent1[:cross_point:] + parent2[cross_point:]
        child2 = parent2[:cross_point:] + parent1[cross_point:]

    return [child1, child2]


def generate_pop(measures):
    """
    Chops measures into phrases of length set by phrase_len
    """
    phrases = []

    curr_len = 0  # tracks number of measures in current phrase
    temp_phrase = []

    for i in range(len(measures)):  # For each song
        for j in range(len(measures[i])):

            temp_phrase.append(measures[i][j])

            # append to phrases if current phrase is long enough
            curr_len = (curr_len + 1) % phrase_len
            if curr_len == 0:
                phrases.append(temp_phrase)
                temp_phrase = []

        # drop the last phrase if it's too short (doesn't contain enough measures)
        temp_phrase = []
        curr_len = 0

    return phrases


def main():
    setParameters()

    phrases = generate_pop(helpers.all_measures())

    for curr_gen in range(iters):

        # Score current generation
        print(len(phrases))
        scores = fitness(phrases)
        filter_percentile = 10
        fitness_threshold = np.percentile(scores, filter_percentile)
        
        top_percentile = np.percentile(scores, 99)
        print(">gen %d, new 99th percentile score = %.3f" % (curr_gen+1, top_percentile))

        # Select most fit parents
        parents = []
        for i in range(len(phrases)):
            if scores[i] >= fitness_threshold:
                parents.append(phrases[i])

        # create next generation
        children = []


        for j in range(0, len(parents), 2):

            # skip iteration if single parent
            if j >= len(parents) - 2:
                continue

            parent1, parent2 = parents[j], parents[j+1]

            for child in crossover_min_dist(parent1, parent2, cross_rate):
                mutate(child, muta_rate)
                children.append(child)

        phrases = children
        
    scores = fitness(phrases)
    best_phrases = helpers.best_phrases(phrases, scores, output_len // phrase_len)
    res_phrases = []
    res_scores = fitness(best_phrases)
    for i in range(len(best_phrases)):
        res_phrases.append(best_phrases[i])

    print("Final score: " + str(round(np.mean(res_scores), 3)))

    res_measures = helpers.phrases_to_measures(res_phrases)
    tokens = helpers.measures_to_tokens(res_measures)
    helpers.export_midi(tokens, file_name)

def random_midi():
    helpers.export_midi(helpers.measures_to_tokens(
        random_measures(10)), 'random_test_4')

if __name__ == "__main__":
    main()
