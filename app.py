from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_from_directory,
    send_file,
    abort,
)
import os
import gen_midi
import pickle
import numpy as np
from werkzeug.utils import secure_filename
from data_model_classic import predict_classic as classic
from data_model_irish import predict_irish as irish
from data_model_max import predict_combo as combo

import create_seq
import parser
from flask_cors import CORS
import uuid
import io
import warnings
from silence_tensorflow import silence_tensorflow
silence_tensorflow()
warnings.filterwarnings("ignore")

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
GENERATED_FOLDER = "generated"
app.config["GENERATED_FOLDER"] = GENERATED_FOLDER

## Загружаем ноты
print("uploading notes")
with open("data_model_classic/notes_classic", "rb") as fp_c:
    notes_classic = pickle.load(fp_c)

pitchnames_classic = sorted(set(item for item in notes_classic))
n_vocab_classic = len(set(notes_classic))

with open("data_model_irish/notes_irish", "rb") as fp_i:
    notes_irish = pickle.load(fp_i)

pitchnames_irish = sorted(set(item for item in notes_irish))
n_vocab_irish = len(set(notes_irish))

with open("data_model_max/notes_combo", "rb") as fp_m:
    notes_combo = pickle.load(fp_m)
pitchnames_combo = sorted(set(item for item in notes_combo))
n_vocab_combo = len(set(notes_combo))
print("upload complete")


print("Creating starting sequences")

network_input_classic, normalized_input_classic = classic.prepare_sequences_output(
    notes_classic, pitchnames_classic, n_vocab_classic
)
network_input_irish, normalized_input_irish = irish.prepare_sequences_output(
    notes_irish, pitchnames_irish, n_vocab_irish
)
network_input_combo, normalized_input_combo = combo.prepare_sequences_output(
    notes_combo, pitchnames_combo, n_vocab_combo
)

print("Creating network...")

model_classic = classic.create_network(normalized_input_classic, n_vocab_classic)
model_irish = irish.create_network(normalized_input_irish, n_vocab_irish)
model_combo = combo.create_network(normalized_input_combo, n_vocab_combo)

print("Adding weights...")

model_classic.load_weights("weights/classic/weights-model_classic-300-0.8220.hdf5")
model_irish.load_weights("weights/irish/weights-model_irish-300-0.5301.hdf5")
model_combo.load_weights("weights/combo/weights-model_combo-400-0.4020.hdf5")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/generate_music", methods=["POST"])
def generate_music():
    no_file = False

    if "midiFile" not in request.files:
        no_file = True
    else:
        midi_file = request.files["midiFile"]
        # Проверяем, что файл был выбран
        if midi_file.filename == "" or midi_file.filename == "No file chosen":
            no_file = True
        else:
            midi_file.save(
                os.path.join(app.config["UPLOAD_FOLDER"], midi_file.filename)
            )

    instrument = request.form.get("instrument")
    style = request.form.get("style")
    composition_length = request.form.get("compositionLength")
    random = request.form.get("random")

    generated_filename = str(uuid.uuid4()) + ".mid"

    if style == "classical":
        ## генерируем по классической модели
        if not no_file:
            print("Parsing user file")
            notes = parser.get_notes(
                os.path.join(app.config["UPLOAD_FOLDER"], midi_file.filename)
            )
            try:
                print("Prepearing sequences...")
                wrong_pitch = create_seq.check_pitches(notes, pitchnames_classic)
                if wrong_pitch:
                    print("Wrong pitch")
                    notes, success_transform = create_seq.transform_pitch(
                        notes, pitchnames_classic
                    )

                network_input_classic, normalized_input_classic = (
                    create_seq.prepare_sequences_output(
                        notes, pitchnames_classic, n_vocab_classic
                    )
                )
            except Exception:
                return abort(
                    400, {"error": "Cannot generate based on the uploaded file."}
                )
        else:
            print("Prepearing sequences...")
            network_input_classic, normalized_input_classic = (
                create_seq.prepare_sequences_output(
                    notes_classic, pitchnames_classic, n_vocab_classic
                )
            )

        try:

            prediction_output = classic.generate_notes(
                model_classic,
                network_input_classic,
                pitchnames_classic,
                n_vocab_classic,
                random,
                int(composition_length),
            )

            gen_midi.create_midi(
                prediction_output, instrument, generated_filename, GENERATED_FOLDER
            )
        except Exception:
            return abort(400, {"error": "Cannot generate based on the uploaded file."})

    elif style == "irish":
        ##генрируем по ирландской модели
        if not no_file:
            print("Parsing user file")
            notes = parser.get_notes(
                os.path.join(app.config["UPLOAD_FOLDER"], midi_file.filename)
            )
            print("Prepearing sequences...")

            wrong_pitch = create_seq.check_pitches(notes, pitchnames_irish)
            if wrong_pitch:
                print("Wrong pitch")
                notes, success_transform = create_seq.transform_pitch(
                    notes, pitchnames_irish
                )

            network_input_irish, normalized_input_irish = (
                create_seq.prepare_sequences_output(
                    notes, pitchnames_irish, n_vocab_irish
                )
            )
        else:
            print("Prepearing sequences...")

            network_input_irish, normalized_input_irish = (
                create_seq.prepare_sequences_output(
                    notes_irish, pitchnames_irish, n_vocab_irish
                )
            )

        prediction_output = irish.generate_notes(
            model_irish,
            network_input_irish,
            pitchnames_irish,
            n_vocab_irish,
            random,
            int(composition_length),
        )
        gen_midi.create_midi(
            prediction_output, instrument, generated_filename, GENERATED_FOLDER
        )

    else:
        ##генерируем по компбинированной модели
        if not no_file:
            print("Parsing user file")
            notes = parser.get_notes(
                os.path.join(app.config["UPLOAD_FOLDER"], midi_file.filename)
            )
            try:
                print("Prepearing sequences...")
                wrong_pitch = create_seq.check_pitches(notes, pitchnames_combo)
                if wrong_pitch:
                    print("Wrong pitch")
                    notes, success_transform = create_seq.transform_pitch(
                        notes, pitchnames_combo
                    )

                network_input_combo, normalized_input_combo = (
                    create_seq.prepare_sequences_output(
                        notes, pitchnames_combo, n_vocab_combo
                    )
                )
            except Exception:
                return abort(
                    400, {"error": "Cannot generate based on the uploaded file."}
                )
        else:
            print("Prepearing sequences...")
            network_input_combo, normalized_input_combo = (
                combo.prepare_sequences_output(
                    notes_combo, pitchnames_combo, n_vocab_combo
                )
            )

        try:

            prediction_output = combo.generate_notes(
                model_combo,
                network_input_combo,
                pitchnames_combo,
                n_vocab_combo,
                random,
                int(composition_length),
            )

            gen_midi.create_midi(
                prediction_output, instrument, generated_filename, GENERATED_FOLDER
            )
        except Exception:
            return abort(400, {"error": "Cannot generate based on the uploaded file."})

    return jsonify({"success": "success", "filename": generated_filename})


@app.route("/generated/<path:filename>")
def serve_static(filename):
    return send_from_directory(app.config["GENERATED_FOLDER"], filename)


@app.route("/download_generated/<filename>", methods=["GET"])
def download_generated(filename):
    return send_file(
        os.path.join(app.config["GENERATED_FOLDER"], filename), as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)
