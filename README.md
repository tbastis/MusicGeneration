# MusicGeneration

 An application which generates piano pieces using a genetic algorithm.

## Set-up

Run the following commands to install needed packages.

>pip3 install miditok

## MidiTok Explanation

MidiTok is weird. This section aims to clear up *some* of the weirdness, at least that which is relevant to our implementation of the library.

### REMI Token Structure

We use MidiTok to encode MIDI files using the REMI encoding scheme. This encoding is a list of integers with the following structure:

[**BAR, POSITION, PITCH, VELOCITY, DURATION**, ...] 

The meaning of the integer that follows depends on a couple characteristics of the next note. 
- If the next note begins in the following bar, then the next number will be another **BAR** number, so the continuation would be [**... BAR, POSITION, PITCH, VELOCITY, DURATION...**].
- If the next note begins in the same bar, but begins at a different position than the previous note, then the next number will be a **POSITION** number, so the continuation would be [**... POSITION, PITCH, VELOCITY, DURATION...**]
- Else, the next note begins in the same bar and begins at the same position as the previous note (indicating a chord). In this case, the next number will be a **PITCH** number, and the continuation would be [**... PITCH, VELOCITY, DURATION...**]

### Token meanings and value ranges

Below is a description of each type of token, and the values it can take on according to our set parameters in the code. 

**BAR**: Indicates bar number...but really doesn't. It's value is always equal to 1.

**POSITION**: The position of the start time of a note within the given bar. It's value is in the range [320, 351] and can be calculated as 320 + (number of 8th notes after beginning of bar). For example, if a note begins at the same time its bar begins, the position value would be 320.

**PITCH**: The pitch of the note. It's value is in the range [2, 128] because we set it to be between 0 and 127 (joke)

**VELOCITY**: How hard the key was struck when the note was played, which corresponds to the note's loudness. It's value is in the range [129, 255]

**DURATION**: The length of the note. It's value can be calculated as 255 + (the number of 8th notes long the note is). For example, a quarter note has value 257. While I'm not sure there's technically a cap to this value, we can safely assume it is < 320. 

Note that none of the above ranges overlap.
