import pickle

with open("D:/Uni/Diplom/final model/data_model_classic/notes_classic","rb") as fpc:
    notes_classic = pickle.load(fpc)

with open("D:/Uni/Diplom/final model/data_model_irish/notes_irish","rb") as fpi:
    notes_irish = pickle.load(fpi)


notes_combo = notes_classic + notes_irish

with open("notes_combo", "wb") as fp:
    pickle.dump(notes_combo,fp)
