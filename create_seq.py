import numpy as np
import random

def transform_pitch(notes, pitchnames):
    print('Transforming pitches')
    success_transform = True
    new_notes = []
    for elem in notes:
        if not elem in pitchnames:
            pitchnames_str = ' '.join(pitchnames).split(' ')
            elem_str = ''.join(elem).split(' ')
            
            if elem_str[0] in set(pitchnames_str):
               
                index = pitchnames_str.index(elem_str[0])
                new_notes.append(''.join(elem_str[0])+" "+''.join(pitchnames_str[index+1]))
                #new_notes.append(pitchnames_str[index+1])
                print(index)
            else:
                if len(new_notes)>0:

                    new_notes.append(new_notes[-1])
                else:
                    new_notes.append(pitchnames[random.randint(0,len(set(pitchnames)))])
                
                       
        else:
            #print('Good')
            new_notes.append(elem)
        
        

    return new_notes, success_transform

def check_pitches(notes, pitchnames):
    print('Checking pitches...')
    wrong_pitch = False
    pitches_notes = set(notes)
    for elem in notes:
        
        if not elem in pitchnames:
            wrong_pitch = True
    return wrong_pitch


def prepare_sequences_output(notes, pitchnames, n_vocab):
    
    
    note_to_int = dict((note, number) for number, note in enumerate(pitchnames))

    sequence_length = 100
    network_input = []
    output = []
    for i in range(0, len(notes) - sequence_length, 1):
        sequence_in = notes[i:i + sequence_length]
        sequence_out = notes[i + sequence_length]
        network_input.append([note_to_int[char] for char in sequence_in])
        output.append(note_to_int[sequence_out])

    n_patterns = len(network_input)

    
    normalized_input = np.reshape(network_input, (n_patterns, sequence_length, 1))
    # normalize input
    normalized_input = normalized_input / float(n_vocab)

    return (network_input, normalized_input)
