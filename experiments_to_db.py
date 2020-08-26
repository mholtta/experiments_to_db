import sqlite3
import glob
from config import folder_experiments
import warnings
from collections import defaultdict
import json


def list_wrap_remove(var):
    """
    Helper function for removing list wrapping for a single item that might be wrapped into a list

    """

    if type(var) != list:    
        # If not a list, return the input
        return var
    elif len(var) > 1:
        # If an actual list, return the list
        return var
    elif len(var) == 1:
        return var[0]
    else:
        return var

def metrics_file_processing(folder, metrics_file):
    """
    Helper function for processing metrics file

    """

    # Reading in metrics
    metrics_raw = metrics_file.read()
    metrics = json.loads(metrics_raw)

    # Removing list wrapping from single items
    metrics = { key: list_wrap_remove(value) for key, value in metrics.items()}

    # Converting to defaultdict for easy default value
    metrics = defaultdict(lambda: None, metrics)

    test_statistics = get_test_statistics(folder ,metrics)

    return test_statistics

def get_test_statistics(folder, metrics_dict):
    """
    Helper function for obtaining test statistics from metrics dictionary.

    """

    return [folder, metrics_dict["acc_macro_te"], metrics_dict["prec_macro_te"], metrics_dict["rec_macro_te"], 
    metrics_dict["f1_macro_te"], metrics_dict["auc_macro_te"], metrics_dict["acc_micro_te"], metrics_dict["prec_micro_te"],
    metrics_dict["rec_micro_te"], metrics_dict["f1_micro_te"], metrics_dict["auc_micro_te"], metrics_dict["rec_at_5_te"],
    metrics_dict["prec_at_5_te"], metrics_dict["f1_at_5_te"], metrics_dict["rec_at_8_te"],
    metrics_dict["prec_at_8_te"], metrics_dict["f1_at_8_te"], metrics_dict["rec_at_15_te"],
    metrics_dict["prec_at_15_te"], metrics_dict["f1_at_15_te"]]




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
        metrics_file = "".join([folder, "metrics.json"])

        with open(out_file, "r") as f, open(metrics_file) as m:
            name_space = f.readline()
            # Dropping "Namespace(" from beginnning and ")\n" from end
            name_space = name_space[10:][:-2]
            # To list
            name_space = name_space.split(',')
            print(name_space)
            # From list to dictionary with hyperparameter names as keys
            experiment_description = {item.split('=')[0] : item.split('=')[1] for item in name_space}
            # Converting to defaultdict for easy default value
            experiment_description = defaultdict(lambda: None, experiment_description)

            # Reading in metrics
            metrics_raw = m.read()
            metrics = json.loads(metrics_raw)
            # Converting to defaultdict for easy default value
            metrics = defaultdict(lambda: None, metrics)

            test_statistics = [folder, list_wrap_remove(metrics)]

            # TODO need to get the best model by looking at which creteria used and then look at metrics, which has the largest value
            # TODO need to parse date and time from folder name
            # TODO need to parse metrics to list of lists or pandas df or something else
            # TODO need to create the list from which data loaded

            cur.execute("""INSERT OR IGNORE INTO Experiments(FolderName, Data, ICDCodeSet,
             Version, MaxLength, BertMaxLength, JobID, Model, FilterSize, NumFilterMaps, NumEpochs,
             Dropout, Patience, BatchSize, LearningRate, Optimizer, WeightDecay, Criterion, UseLrScheduler,
             WarmUp, UseLrLayerDecay, LrLayerDecay, TuneWordEmbedding, RandomSeed, UseExternalEmbedding, 
             NumWorkers, ElmoTune, ElmoDropOut, ElmoGamma, UseElmo, PreTrainedModel, Date, Time, EpochsRun, 
             BestModelAtEpoch) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
             ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", )# TODO add list here
            print(experiment_description)


    print(out_file)

# connection.close()