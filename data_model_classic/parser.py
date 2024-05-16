import glob
import pickle
import numpy
from music21 import *
import time
from mido import MidiFile
import logging
import sys
sys.path.append('d:/Uni/Diplom/final model/') 
import little_lib


FP = 'classci'
MOD = '2'
logger = logging.getLogger(__name__)
logging.basicConfig(filename='parser_classic.log', level=logging.INFO)
logger.info('Started')


def get_notes():
    
    main_watch = time.time()
    notes = []
    durations = []

    for file in glob.glob("data/*.mid"): ##*.mid
       
        time_start = time.time()

        midi = converter.parse(file)
       
        midi = little_lib.keep_most_notes_instrument(midi)
       

        print("Parsing %s" % file)
        logger.info("Parsing %s" % file)

        notes_to_parse = None

       
        notes_to_parse = midi.flat.notes

        objects_in_song = 0

        for element in notes_to_parse:
            if isinstance(element, note.Note):
                notes.append(str(element.pitch) + " " + str(element.quarterLength))
                objects_in_song+=1
            elif isinstance(element, chord.Chord):
                # Получаем все высоты нот в аккорде и объединяем их в строку
                chord_pitches = '.'.join(str(n.pitch) for n in element.notes)
                notes.append(chord_pitches + " " + str(element.quarterLength))
                objects_in_song+=1
            elif isinstance(element, note.Rest):
                notes.append(str(element.name) + " " + str(element.quarterLength))
                objects_in_song+=1
        logger.info("Total Objects in song = %d" % objects_in_song)
        time_end = time.time()
        logger.info("Time: " + str(time_end-time_start))   
    with open('notes_classic_1', 'wb') as filepath:
        pickle.dump(notes, filepath)
    main_watch_end = time.time()
    logger.info("Parsing is done. Time: " + str(main_watch_end-main_watch))
    return notes






notes = get_notes()


n_vocab = len(set(notes))
logger.info("Total objects number = " + str(n_vocab))
print(n_vocab)
#print(notes)    