import helpers
import random
import sys
import math
import numpy as np
import textdistance as td

# Default parameter values
iters = 25  # number of generations to run through
# chance that two parents make children (rather than persisting to the next gen)
cross_rate = 70
muta_rate = 100  # What percentage of children should be mutated per iteration
phrase_len = 4  # number of measures per phrase
output_len = 16 # number of measures you want output to be
file_name = 'default'

    
def setParameters():
    """Allow the setting of custom parameters for program"""
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
    """Returns a fitness score between 0 and 100 for each phrase"""
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


def random_fitness(phrases):
    """
    Returns a random fitness score between 0 and 100 for each phrase. Useful for
    baseline testing.
    """
    return [random.randint(0, 100) for _ in phrases]


def relation_fitness_only(phrases):
    """
    Returns a fitness score for each phrase using only the relation fitness heuristic. 
    Useful for comparative testing
    """
    return [relation_fitness(phrase) for phrase in phrases]


def direction_fitness_only(phrases):
    """
    Returns a fitness score for each phrase using only the direction fitness heuristic. 
    Useful for comparative testing
    """
    return [direction_fitness(phrase) for phrase in phrases]


def ending_fitness_only(phrases):
    """
    Returns a fitness score for each phrase using only the ending fitness heuristic. 
    Useful for comparative testing
    """
    return [end_fitness(phrase) for phrase in phrases]


def distance_fitness(phrases):
    """
    Returns the normalized compression distance similarities between each phrase 
    and the target phrase.
    """
    target_phrase = helpers.get_target_phrase()

    # return [td.LZMANCD.normalized_similarity(target_phrase, phrase) * 100 for phrase in phrases]
    # return [td.ZLIBNCD.normalized_similarity(target_phrase, phrase) * 100 for phrase in phrases]
    return [td.BZ2NCD.normalized_similarity(target_phrase, phrase) * 100 for phrase in phrases]


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
    selector = random.randint(0, 3)
    selector = 0 # Change this to test different effects, or comment out for random
    match selector:
        case 0:
            return mutate_pitch(phrase, muta_rate)
        case 1:
            return mutate_position(phrase, muta_rate)
        case 2:
            return mutate_velocity(phrase, muta_rate)
        case 3:
            return mutate_position(phrase, muta_rate)


def mutate_pitch(phrase, muta_rate):
    """
    Mutates the pitch of notes in the given phrase in some way with with a 
    probability of `muta_rate`.
    """
    if random.randint(0, 100) < muta_rate:

        measure = random.randint(0, phrase_len - 1)
        pitch_indices = helpers.get_pitch_indices(phrase[measure], include_chords=True)

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

                # Limit maximum change
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

            case 3: 
                # raise or lower pitch of 3 notes in measure  
                for _ in range(3):
                    change = int(np.random.normal(0, 8, 1)[0])

                    # Limit maximum change
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

            case 4:
                # raise or lower pitch of 1 note in measure
                change = int(np.random.normal(0, 8, 1)[0])

                # Limit maximum change
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
    
    return phrase


def mutate_position(phrase, muta_rate):
    """
    Mutates the position of notes in the given phrase in some way with with a 
    probability of `muta_rate`.
    """
    if random.randint(0, 100) < muta_rate:

        measure = random.randint(0, phrase_len - 1)
        position_indices = helpers.get_position_indices(phrase[measure])

        match random.randint(0, 5):

            case 0|1:
                # Randomly alter position of 1 note
                change = int(np.random.normal(0, 2, 1)[0])

                # Limit maximum change
                if (change < -4):
                    change = -4
                if (change > 4):
                    change = 4

                note_index = random.randint(0, len(position_indices) - 1)
                position = phrase[measure][position_indices[note_index]] + change
                if (position < 320 or 351 < position):
                    phrase[measure][position_indices[note_index]] -= change
                else:
                    phrase[measure][position_indices[note_index]] += change

            case 2|3|4:
                # Swap positions of 2 notes
                note_indices = random.sample(range(0, len(position_indices)-1), 2)
                pos1 = phrase[measure][note_indices[0]]
                pos2 = phrase[measure][note_indices[1]]
                phrase[measure][note_indices[0]] = pos2
                phrase[measure][note_indices[1]] = pos1

            case 5:
                # Reverse position of notes in measure
                i = 0
                j = len(position_indices) - 1
                while (i < j):
                    temp = phrase[measure][position_indices[i]] 
                    phrase[measure][position_indices[i]] = phrase[measure][position_indices[j]] 
                    phrase[measure][position_indices[i]] = temp
                    i+=1
                    j-=1

    return phrase


def mutate_velocity(phrase, muta_rate):
    """
    Mutates the velocity of notes within the given phrase in some way with with 
    a probability of `muta_rate`.
    """
    if random.randint(0, 100) < muta_rate:

        measure = random.randint(0, phrase_len - 1)
        velocity_indices = helpers.get_velocity_indices(phrase[measure])

        match random.randint(0, 5):

            case 0:
                # Randomly alter velocity of 1 note
                change = int(np.random.normal(0, 4, 1)[0])

                # Limit maximum change
                if (change < -12):
                    change = -12
                if (change > 12):
                    change = 12

                note_index = random.randint(0, len(velocity_indices) - 1)
                velocity = phrase[measure][velocity_indices[note_index]] + change
                if (velocity < 129 or 255 < velocity):
                    phrase[measure][velocity_indices[note_index]] -= change
                else:
                    phrase[measure][velocity_indices[note_index]] += change

            case 1|2|3:
                # Swap positions of 2 notes
                note_indices = random.sample(range(0, len(velocity_indices)-1), 2)
                vel1 = phrase[measure][note_indices[0]]
                vel2 = phrase[measure][note_indices[1]]
                phrase[measure][note_indices[0]] = vel2
                phrase[measure][note_indices[1]] = vel1

            case 4|5:
                # Reverse position of notes in measure
                i = 0
                j = len(velocity_indices) - 1
                while (i < j):
                    temp = phrase[measure][velocity_indices[i]] 
                    phrase[measure][velocity_indices[i]] = phrase[measure][velocity_indices[j]] 
                    phrase[measure][velocity_indices[i]] = temp
                    i+=1
                    j-=1    
                      
    return phrase  


def mutate_duration(phrase, muta_rate):
    """
    Mutates the duration of notes within the given phrase in some way with with 
    a probability of `muta_rate`.
    """
    if random.randint(0, 100) < muta_rate:

        measure = random.randint(0, phrase_len - 1)
        duration_indices = helpers.get_duration_indices(phrase[measure])

        match random.randint(0, 5):

            case 0:
                # Randomly alter duration of 1 note
                change = random.sample([-2, -1, 1, 2], 1)[0]

                note_index = random.randint(0, len(duration_indices) - 1)
                duration = phrase[measure][duration_indices[note_index]] + change
                if (duration < 256 or 287 < duration):
                    phrase[measure][duration_indices[note_index]] -= change
                else:
                    phrase[measure][duration_indices[note_index]] += change

            case 1|2|3:
                # Swap durations of 2 notes
                note_indices = random.sample(range(0, len(duration_indices)-1), 2)
                dur1 = phrase[measure][note_indices[0]]
                dur2 = phrase[measure][note_indices[1]]
                phrase[measure][note_indices[0]] = dur2
                phrase[measure][note_indices[1]] = dur1

            case 4|5:
                # Reverse durations of notes in measure
                i = 0
                j = len(duration_indices) - 1
                while (i < j):
                    temp = phrase[measure][duration_indices[i]] 
                    phrase[measure][duration_indices[i]] = phrase[measure][duration_indices[j]] 
                    phrase[measure][duration_indices[i]] = temp
                    i+=1
                    j-=1    
                      
    return phrase  
     

def crossover_rand(p1, p2, cross_rate):
    """
    Crossover two parents at random point with some probability to create 
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
    over at this point).

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


def crossover_min_pos(parent1, parent2, cross_rate):
    """
    Crossover two parents with some probability to create 
    new children. Otherwise, the parents are carried through
    to the next generation.

    Crossover point is determined by the posotion of the starting and ending notes 
    between the two phrases (that would be consecutive if we crossed over at 
    this point).

    Returns two children in an array [child1, child2]
    """
    child1, child2 = parent1.copy(), parent2.copy()

    if random.randint(0, 100) <= cross_rate:
        cross_point = 0
        least_dist = math.inf

        for i in range(phrase_len):
            if i == 0: continue #skip comparing first one 

            end_p1p_measure = parent1[i-1]
            end_p1p_position_indices = helpers.get_position_indices(end_p1p_measure)
            end_p1p = end_p1p_measure[end_p1p_position_indices[-1]] # last position token parent 1 last measure

            start_p2p_measure = parent2[i] 
            start_p2p_position_indices = helpers.get_position_indices(start_p2p_measure)
            start_p2p = start_p2p_measure[start_p2p_position_indices[0]] # first position token parent 2 current measure

            end_p2p_measure = parent2[i-1] 
            end_p2p_position_indices = helpers.get_position_indices(end_p2p_measure)
            end_p2p = end_p2p_measure[end_p2p_position_indices[-1]] # last position token parent 2 last measure

            start_p1p_measure = parent1[i]  #position of first note in parent 1 current measure
            start_p1p_measure_indices = helpers.get_position_indices(start_p1p_measure)
            start_p1p = start_p1p_measure[start_p1p_measure_indices[0]] #first position token parent 1 current measure

            dist = abs(end_p1p - start_p2p) + abs(end_p2p + start_p1p)
            
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
                child = mutate(child, muta_rate)
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


if __name__ == "__main__":
    main()
