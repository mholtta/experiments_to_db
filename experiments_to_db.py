import sqlite3
import glob
from config import folder_experiments
import warnings
from collections import defaultdict

# Folders containing experiments 
folders = glob.glob(folder_experiments)
# Connecting to db and creating cursor
connection = sqlite3.connect("experiments.db")
cur = connection.cursor()

# Going through each experiment and gathering data
for folder in folders:
    # Finding out-file for gathering experiment details
    out_file = glob.glob("".join([folder, "*.out"]))

    if len(out_file) > 1:
        warnings.warn("Folder {} has several out-files, file not processed.".format(folder))
    else:
        out_file = out_file[0]

        with open(out_file, "r") as f:
            name_space = f.readline()
            # Dropping "Namespace(" from beginnning and ")\n" from end
            name_space = name_space[10:][:-2]
            # To list
            name_space = name_space.split(',')
            print(name_space)
            # From list to dictionary with hyperparameter names as keys
            experiment_description = {item.split('=')[0] : item.split('=')[1] for item in name_space}
            # COnverting to defaultdict for easy default value
            experiment_description = defaultdict(lambda: None, experiment_description)

            cur.execute("""INSERT OR IGNORE INTO Experiments(FolderName, Data, ICDCodeSet,
             Version, MaxLength, BertMaxLength, JobID, Model, FilterSize, NumFilterMaps, NumEpochs,
             Dropout, Patience, BatchSize, LearningRate, Optimizer, WeightDecay, Criterion, UseLrScheduler,
             WarmUp, UseLrLayerDecay, LrLayerDecay, TuneWordEmbedding, RandomSeed, UseExternalEmbedding, 
             NumWorkers, ElmoTune, ElmoDropOut, ElmoGamma, UseElmo, PreTrainedModel, Date, Time, EpochsRun, 
             BestModelAtEpoch) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
             ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", # TODO add list here)
            print(experiment_description)


    print(out_file)

# connection.close()