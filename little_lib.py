from music21 import *

from mido import MidiFile


""" Маленькая библиотека с функциями для работы с MIDI файлами """

def remove_instruments_with_few_notes(midi_stream, min_notes_threshold):

    """Убирает инструменты с количеством нот в партии меньше min_notes_treshold """

    all_instruments = instrument.partitionByInstrument(midi_stream)
    new_stream = stream.Stream()
    for part in all_instruments:
      
        notes_count = sum(1 for _ in part.flat.notes)
        if notes_count >= min_notes_threshold:
            new_stream.append(part)
    #new_stream.write('midi', fp='output1.mid')
    return new_stream


def remove_percussion(midi_stream):
    """ Удаляет перкусионные инструменты """
    new_stream = stream.Stream()
    all_instruments = instrument.partitionByInstrument(midi_stream)
    percussion_instruments = [
    'Percussion',
    'BassDrum',
    'SnareDrum',
    'TomTom',
    'HiHat',
    'Cymbal',
    'Triangle',
    'WoodBlock',
    'Cowbell',
    'Tambourine',
    'Gong',
    'Drums',
    'Bongo',
    'Maracas'
]



    for part in all_instruments:
        
        if not part.partName in set(percussion_instruments) :
           
            new_stream.append(part)

    return new_stream


def keep_one_instrument(midi_stream, instrument_name):
    """ Оставляет интрумент по названию """
    ### Название должно соответсвовать названиям music21
    # Если такого интрумента нет выведет пустой трек

    all_instruments = instrument.partitionByInstrument(midi_stream)
    new_stream = stream.Stream()

    for part in all_instruments:
      
        if part.partName == instrument_name:
            new_stream.append(part)
    #new_stream.write('midi', fp='output.mid')
    
    return new_stream

def keep_loudest_instrument(midi_stream):
    """ Оставляет самый громкий инструмент """
    all_instruments = instrument.partitionByInstrument(midi_stream)

    loudest_instrument = None
    loudest_volume = -float('inf')

    for part in all_instruments:
       
        volume = sum(n.volume.velocity for n in part.notesAndRests if isinstance(n, note.Note))

        if volume > loudest_volume:
            loudest_instrument = part
            loudest_volume = volume

   
    new_stream = stream.Stream()
    new_stream.append(loudest_instrument)
    #new_stream.write('midi', fp='output.mid')
    return new_stream
    
    
def remove_instrument(midi_stream, instrument_name):
    """ Убирает инструмент по названию """
   
    all_instruments = instrument.partitionByInstrument(midi_stream)

    new_stream = stream.Stream()

    for part in all_instruments:
       
        if part.partName != instrument_name:
            new_stream.append(part)

    return new_stream

def keep_most_notes_instrument(midi_stream):
    """ Возвращает инструмент с наибольшим количеством нот в партии"""
    all_instruments = instrument.partitionByInstrument(midi_stream)

    most_notes_instrument = None
    max_notes_count = 0


    
   
    for part in all_instruments:
        
        notes_count = len(set(n.pitches for n in part.flat.notes))

        if notes_count > max_notes_count:
            most_notes_instrument = part
            max_notes_count = notes_count

    new_stream = stream.Stream()
    new_stream.append(most_notes_instrument)
    
    # Сохраняем MIDI-файл только с инструментом, имеющим наибольшее количество нот
    #new_stream.write('midi', fp='output.mid')
    return new_stream

