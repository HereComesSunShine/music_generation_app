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


def generate_notes(
    model, network_input, pitchnames, n_vocab, start_random, output_len
):  ##
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
