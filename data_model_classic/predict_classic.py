import numpy as np
import matplotlib.pyplot as plt
import os

#!pip install keras_self_attention
import glob
import pickle
from music21 import converter, instrument, stream, note, chord
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM, Activation, Bidirectional, Flatten
from keras import utils
from keras.callbacks import ModelCheckpoint, CSVLogger
from keras_self_attention import SeqSelfAttention
from keras.layers import BatchNormalization as BatchNorm
import logging
import io
import time


def prepare_sequences_output(notes, pitchnames, n_vocab):

    note_to_int = dict((note, number) for number, note in enumerate(pitchnames))

    sequence_length = 100
    network_input = []
    output = []
    count = 0
    for i in range(0, len(notes) - sequence_length, 1):
        try:
            sequence_in = notes[i : i + sequence_length]
            sequence_out = notes[i + sequence_length]

            network_input.append([note_to_int[char] for char in sequence_in])
            output.append(note_to_int[sequence_out])
            count += 1
        except:
            continue

    n_patterns = len(network_input)

    normalized_input = np.reshape(network_input, (n_patterns, sequence_length, 1))
    # normalize input
    normalized_input = normalized_input / float(n_vocab)

    return (network_input, normalized_input)


def create_network(network_input, n_vocab):
    """Создание модели сети"""

    model = Sequential()

    model.add(
        Bidirectional(
            LSTM(256, return_sequences=True),
            input_shape=(network_input.shape[1], network_input.shape[2]),
        )
    )
    model.add(SeqSelfAttention(attention_activation="sigmoid"))

    model.add(Dropout(0.4))

    model.add(
        LSTM(
            128,
            input_shape=(network_input.shape[1], network_input.shape[2]),
            return_sequences=True,
        )
    )

    model.add(Dropout(0.4))

    model.add(Flatten())
    model.add(Dense(n_vocab))
    model.add(Activation("softmax"))
    model.compile(loss="categorical_crossentropy", optimizer="rmsprop")

    return model


def generate_notes(model, network_input, pitchnames, n_vocab, start_random, output_len):
    print("generating")

    # pick a random seq from the input as a start
    if start_random:
        start = np.random.randint(0, len(network_input) - 1)
    else:
        start = 0
    int_to_note = dict((number, note) for number, note in enumerate(pitchnames))

    pattern = network_input[start]
    prediction_output = []

    # generate n notes
    for note_index in range(output_len):
        prediction_input = np.reshape(pattern, (1, len(pattern), 1))
        prediction_input = prediction_input / float(n_vocab)

        prediction = model.predict(prediction_input, verbose=0)

        index = np.argmax(prediction)
        result = int_to_note[index]
        prediction_output.append(result)

        pattern.append(index)
        pattern = pattern[1 : len(pattern)]
    # time_gen = time_start - time.time()
    print("generating complete")

    return prediction_output
