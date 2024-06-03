from music21 import *
import little_lib


def get_notes(fp):

    notes = []
    durations = []
    midi = converter.parse(fp)
    midi = little_lib.remove_percussion(midi)
    midi = little_lib.remove_instruments_with_few_notes(midi, 100)
    midi = little_lib.keep_loudest_instrument(midi)
    
    notes_to_parse = midi.flat.notes
    objects_in_song = 0
    for element in notes_to_parse:
        if isinstance(element, note.Note):
            notes.append(str(element.pitch) + " " + str(element.quarterLength))
            objects_in_song += 1
        elif isinstance(element, chord.Chord):
            # Получаем все высоты нот в аккорде и объединяем их в строку
            chord_pitches = ".".join(str(n.pitch) for n in element.notes)
            notes.append(chord_pitches + " " + str(element.quarterLength))
            objects_in_song += 1
        elif isinstance(element, note.Rest):
            notes.append(str(element.name) + " " + str(element.quarterLength))
            objects_in_song += 1
        

    return notes
