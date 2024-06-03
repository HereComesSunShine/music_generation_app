import glob
import pickle
import numpy
from music21 import *
import time
from mido import MidiFile
from io import BytesIO


FP = "generated/"
MOD = "generated_music"


def create_midi(prediction_output, chosen_instrument, fp, folder):

    print("start midi transform")

    offset = 0
    output_notes = []
    if chosen_instrument == "guitar":
        output_notes.append(instrument.ElectricGuitar())
    elif chosen_instrument == "violin":
        output_notes.append(instrument.Violin())
    elif chosen_instrument == "flute":
        output_notes.append(instrument.Flute())
    elif chosen_instrument == "bagpipes":
        output_notes.append(instrument.Bagpipes())
    elif chosen_instrument == "tenor_vocal":
        output_notes.append(instrument.Tenor())
    elif chosen_instrument == "organ":
        output_notes.append(instrument.Organ())
    else:

        output_notes.append(instrument.Piano())

    for pattern in prediction_output:
        pattern = pattern.split()
        temp = pattern[0]
        duration = pattern[1]
        pattern = temp
        # pattern is a chord
        if ("." in pattern) or pattern.isdigit():
            notes_in_chord = pattern.split(".")
            notes = []
            for current_note in notes_in_chord:
                # Создаем объект ноты для каждой высоты в аккорде
                new_note = note.Note(current_note)
                new_note.instrument = instrument.Flute()
                notes.append(new_note)
            new_chord = chord.Chord(notes)
            new_chord.offset = offset
            new_chord.quarterLength = convert_to_float(duration)
            output_notes.append(new_chord)
        # pattern is a rest
        elif "rest" in pattern:
            new_rest = note.Rest()
            new_rest.offset = offset
            new_rest.quarterLength = convert_to_float(duration)
            output_notes.append(new_rest)
        # pattern is a note
        else:
            new_note = note.Note(pattern)
            new_note.offset = offset
            new_note.instrument = instrument.Flute()
            new_note.quarterLength = convert_to_float(duration)
            output_notes.append(new_note)

        offset += convert_to_float(duration)
    # Создаем MIDI-поток на основе списка output_notes
    midi_stream = stream.Stream(output_notes)
    print("Writing midi")
    # Записываем MIDI-поток в файл

    midi_stream.write("midi", fp=folder + "/" + fp)
    print("Done")
    return midi_stream


def convert_to_float(frac_str):
    try:
        return float(frac_str)
    except ValueError:
        num, denom = frac_str.split("/")
        try:
            leading, num = num.split(" ")
            whole = float(leading)
        except ValueError:
            whole = 0
        frac = float(num) / float(denom)
        return whole - frac if whole < 0 else whole + frac
