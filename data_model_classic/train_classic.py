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

logger = logging.getLogger(__name__)
logging.basicConfig(filename='train_classic.log', level=logging.INFO)
logger.info('Started')


def train_network(notes, n_vocab):
    network_input, network_output = prepare_sequences(notes, n_vocab)
    model = create_network(network_input, n_vocab)
    train(model, network_input, network_output)




def prepare_sequences(notes, n_vocab):
    """ Подготовка последовательностей на вход нейронной сети """
    time_start = time.time()
    # Размер последовательности
    sequence_length = 100
    # Создание словаря для алфавита модели
    note_to_int = dict((note, number) for number, note in enumerate(pitchnames))

    network_input = []
    network_output = []

    # создание входной последвательности и выходной ноты
    for i in range(0, len(notes) - sequence_length, 1):
        try:
            sequence_in = notes[i:i + sequence_length]
            sequence_out = notes[i + sequence_length]
            network_input.append([note_to_int[char] for char in sequence_in])
            network_output.append(note_to_int[sequence_out])
        except:
            break

    n_patterns = len(network_input)

    network_input = np.reshape(network_input, (n_patterns, sequence_length, 1))

    network_input = network_input / float(n_vocab)
    network_output = utils.to_categorical(network_output)
    time_end = time.time()
    return (network_input, network_output)

def create_network(network_input, n_vocab):
    """ Создание модели сети """
    logger.info('Creating model...')
    model = Sequential()
    
    model.add(Bidirectional(LSTM(256, return_sequences=True),
                           input_shape=(network_input.shape[1], network_input.shape[2]))) 
    model.add(SeqSelfAttention(attention_activation = 'sigmoid'))

    model.add(Dropout(0.4))

    model.add(LSTM(128,
        input_shape=(network_input.shape[1], network_input.shape[2]), 
        return_sequences=True))
    
    model.add(Dropout(0.4))
            
    model.add(Flatten()) 
    model.add(Dense(n_vocab))
    model.add(Activation('softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

    ##logger
    buffer = io.StringIO()
    model.summary(print_fn=lambda x: buffer.write(x + '\n'))
    model_summary = buffer.getvalue()
    logger.info(model_summary)

    return model

def train(model, network_input, network_output):
    """ train the neural network """
    logger.info("Starting traning...")
    time_start = time.time()
    filepath = os.path.abspath("weights-model_classic-{epoch:03d}-{loss:.4f}.hdf5")
    csvlog_filepath = os.path.abspath("training_log.csv")
    checkpoint = ModelCheckpoint(
        filepath,
        period=10, #Every 10 epochs
        monitor='loss',
        verbose=1,
        save_best_only=False,
        mode='min'
    )
    csv_logger = CSVLogger(csvlog_filepath, append=True)
    callbacks_list = [checkpoint]
    history = model.fit(network_input, network_output, epochs=100, batch_size=256, callbacks=callbacks_list)
    time_end = time.time()
    logger.info("Time ellapse: " + str(time_end - time_start))
    # Построение графика потерь относительно эпохи
    plt.plot(history.history['loss'])
    plt.title('Model Loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train'], loc='upper left')
    plt.show()
 

