import sqlite3
import glob
from config import folder_experiments
import warnings
from collections import defaultdict
import json
import numpy as np
import datetime


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

def out_file_processing(folder, out_file):
    """
    Helper function for reading the experiment hyperparameters from first line of .out file.

    Returns experiment, model_criteria.

    """
    namespace = out_file.readline()
    # Dropping "Namespace(" from beginnning and ")\n" from end
    namespace = namespace[10:][:-2]
    # To list
    namespace = namespace.split(',')
    print(namespace)
    # From list to dictionary with hyperparameter names as keys
    experiment_description = {item.split('=')[0] : item.split('=')[1] for item in namespace}
    # Converting to defaultdict for easy default value
    experiment_description = defaultdict(lambda: None, experiment_description)

    # Model from experiment_description
    model = experiment_description["model"]
    # Getting date and time
    date, time = date_time_parser(folder, model)

    # Extracting model criteria separately to use it in metrics file processing
    model_criteria = experiment_description["criterion"]

    # List to be returned in the order of the database schema
    experiment = [folder, experiment_description["data_path"], experiment_description["Y"], experiment_description["version"],
                 experiment_description["MAX_LENGTH"], experiment_description["BERT_MAX_LENGTH"], experiment_description["job_id"],
                 experiment_description["model"], experiment_description["filter_size"], experiment_description["num_filter_maps"],
                 experiment_description["n_epochs"], experiment_description["dropout"], experiment_description["patience"],
                 experiment_description["batch_size"], experiment_description["lr"], experiment_description["optimizer"],
                 experiment_description["weight_decay"], experiment_description["criterion"], experiment_description["use_lr_scheduler"],
                 experiment_description["warm_up"], experiment_description["use_lr_layer_decay"], experiment_description["lr_layer_decay"],
                 experiment_description["tune_wordemb"], experiment_description["random_seed"], experiment_description["use_ext_emb"],
                 experiment_description["num_workers"], experiment_description["elmo_tune"], experiment_description["elmo_dropout"],
                 experiment_description["elmo_gamma"], experiment_description["use_elmo"], experiment_description["pretrained_model"], date, time]

    return experiment, model_criteria


def date_time_parser(folder_path, model):
    """
    Helper function for parsing date and time from folder path name.

    """
    folder = folder_path.split("\\")[-1]

    # Removing model and "_" from folder name
    len_model = len(model) + 1
    folder = folder[len_model:]

    # Splitting to pieces and taking first 5 items from list
    date_time_raw = folder.split["_"][0:4]

    # Dictionary for converting month into a number
    mth_conversion = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06","Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12"}

    mth_num = mth_conversion[date_time_raw[0]]
    current_year = datetime.datetime.now().year
    # Date in string format
    date = "-".join([str(current_year), mth_num, date_time_raw[1]])
    time = ":".join(date_time_raw[2:4])

    return date, time

def metrics_file_processing(folder, metrics_file, model_criteria):
    """
    Helper function for processing metrics file.

    Returns num_epochs, best_model_at_epoch, training_statistics, test_statistics.

    """

    # Reading in metrics
    metrics_raw = metrics_file.read()
    metrics = json.loads(metrics_raw)

    # Removing list wrapping from single items
    metrics = { key: list_wrap_remove(value) for key, value in metrics.items()}

    # Converting to defaultdict for easy default value
    metrics = defaultdict(lambda: None, metrics)

    num_epochs, best_model_at_epoch, training_statistics = get_training_statistics(folder, metrics, model_criteria)

    test_statistics = get_test_statistics(folder, metrics)

    return num_epochs, best_model_at_epoch, training_statistics, test_statistics

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

def get_training_statistics(folder, metrics_dict, model_criteria):
    """
    A helper function for obtaining training statistics from metrics dictionary.

    Returns num_epochs, best_model_at_epoch, training_stats.

    """
    # If training has early stopped, then one extra validation result with the best model has been added
    # Checking if this is the case, and if yes, removing last validation result
    if len(metrics_dict["loss_dev"]) != len(metrics_dict["loss_tr"]):
        training_measures = ["acc_macro", "prec_macro", "rec_macro", "f1_macro", "auc_macro", "acc_micro", "prec_micro",
                            "rec_micro", "f1_micro", "auc_micro", "rec_at_5", "rec_at_5", "f1_at_5", "rec_at_8",
                            "prec_at_8", "f1_at_8", "rec_at_15", "prec_at_15", "f1_at_15", "loss_dev", "loss_tr"]
        
        # Looping through the dictionary and removing last validation result
        result_dict = {}
        for (key, value) in metrics_dict.items():
            if key in training_measures:
                if key == "loss_tr":
                    result_dict[key] = value
                else:
                    result_dict[key] = value[:-1]
        
        # Assigning result back to metrics dict
        metrics_dict = defaultdict(lambda: None, result_dict)

    # All measures printen once per epoch, picking one
    num_epochs = len(metrics_dict["loss_tr"])

    # Finding which epoch yielded the best model
    # Model criteria in format 'prec_at_8', 'prec_at_15', 'f1_macro', 'f1_micro', 'prec_at_5' or 'loss_dev', matches dictionary keys
    criteria_list = metrics_dict[model_criteria]
    best_model_at_epoch = criteria_list.index(max(criteria_list))


    # Gathering all measures to one list
    training_stats = [[folder * num_epochs], [range(1, num_epochs)],metrics_dict["acc_macro"], metrics_dict["prec_macro"], metrics_dict["rec_macro"], 
                    metrics_dict["f1_macro"], metrics_dict["auc_macro"], metrics_dict["acc_micro"], metrics_dict["prec_micro"],
                    metrics_dict["rec_micro"], metrics_dict["f1_micro"], metrics_dict["auc_micro"], metrics_dict["rec_at_5"],
                    metrics_dict["prec_at_5"], metrics_dict["f1_at_5"], metrics_dict["rec_at_8"],
                    metrics_dict["prec_at_8"], metrics_dict["f1_at_8"], metrics_dict["rec_at_15"],
                    metrics_dict["prec_at_15"], metrics_dict["f1_at_15"], metrics_dict["loss_dev"], metrics_dict["loss_tr"]]
    
    # Tranposing to have one line of measures per epoch
    training_stats = np.array(training_stats).T.tolist()


    return num_epochs, best_model_at_epoch, training_stats
