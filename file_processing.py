import sqlite3
import glob
from config import folder_experiments
import warnings
from collections import defaultdict
import json
import numpy as np
import datetime
import re




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
    # From list to dictionary with hyperparameter names as keys. Keys contain spaces needing to be removed.
    # Values contain extra single or double quotes needing to be removed
    experiment_description = {item.split('=')[0].strip() : quote_remover( item.split('=')[1] ) for item in namespace}

    # Checking if key "batch_size_train" exists in dictionary, if not renaming keys
    # Logic added due to allowing separately to set batch size for training and testing. Prior to change test batch size was 1.
    if not "batch_size_train" in experiment_description:
        experiment_description["batch_size_train"] = experiment_description.pop("batch_size")
        experiment_description["batch_size_test"] = '1' # As string following other values in dict

    # Converting to defaultdict for easy default value
    experiment_description = defaultdict(lambda: None, experiment_description)

    # Model from experiment_description
    model = experiment_description["model"]
    # Getting date and time
    date, time = date_time_parser(folder, model)

    # Transforming folder full path to folder name
    folder = get_folder_name(folder)

    # Extracting model criteria separately to use it in metrics file processing
    model_criteria = experiment_description["criterion"]

    # List to be returned in the order of the database schema
    experiment = [folder, experiment_description["data_path"], experiment_description["Y"], experiment_description["version"],
                 experiment_description["MAX_LENGTH"], experiment_description["BERT_MAX_LENGTH"], experiment_description["job_id"],
                 experiment_description["model"], experiment_description["filter_size"], experiment_description["num_filter_maps"],
                 experiment_description["n_epochs"], experiment_description["dropout"], experiment_description["patience"],
                 experiment_description["batch_size_train"], experiment_description["batch_size_test"], experiment_description["lr"],
                 experiment_description["optimizer"], experiment_description["weight_decay"], experiment_description["criterion"],
                 experiment_description["use_lr_scheduler"], experiment_description["warm_up"], experiment_description["use_lr_layer_decay"],
                 experiment_description["lr_layer_decay"], experiment_description["tune_wordemb"], experiment_description["random_seed"], 
                 experiment_description["use_ext_emb"], experiment_description["num_workers"], experiment_description["elmo_tune"], 
                 experiment_description["elmo_dropout"], experiment_description["elmo_gamma"], experiment_description["use_elmo"],
                 experiment_description["pretrained_model"], date, time]

    # Converting true to 1 and false to 0, as SQlite doesn't have boolean data type. Booleans stored as int
    experiment = list(map(true_false_converter, experiment))

    return experiment, model_criteria


def date_time_parser(folder_path, model):
    """
    Helper function for parsing date and time from folder path name.

    """
    folder = folder_path.split("\\")[-2]

    # Removing model and "_" from folder name
    len_model = len(model) + 1
    folder = folder[len_model:]

    # Splitting to pieces and taking first 5 items from list
    date_time_raw = folder.split("_")[0:4]

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
    metrics = { dict_key_editer(key): list_wrap_remove(value) for key, value in metrics.items()}

    # Converting to defaultdict for easy default value
    metrics = defaultdict(lambda: None, metrics)

    # Transforming folder full path to folder name
    folder = get_folder_name(folder)

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
            metrics_dict["prec_at_15_te"], metrics_dict["f1_at_15_te"], metrics_dict["loss_test_te"]]

def get_training_statistics(folder, metrics_dict, model_criteria):
    """
    A helper function for obtaining training statistics from metrics dictionary.

    Returns num_epochs, best_model_at_epoch, training_stats.

    """
    # If training has early stopped, then one extra validation result with the best model has been added
    # Checking if this is the case, and if yes, removing last validation result
    if len_float_or_list(metrics_dict["loss_dev"]) != len_float_or_list(metrics_dict["loss_tr"]):
        training_measures = ["acc_macro", "prec_macro", "rec_macro", "f1_macro", "auc_macro", "acc_micro", "prec_micro",
                            "rec_micro", "f1_micro", "auc_micro", "prec_at_5", "rec_at_5", "rec_at_5", "f1_at_5", "rec_at_8",
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
    num_epochs = len_float_or_list(metrics_dict["loss_tr"])

    # Finding which epoch yielded the best model
    # Model criteria in format 'prec_at_8', 'prec_at_15', 'f1_macro', 'f1_micro', 'prec_at_5' or 'loss_dev', matches dictionary keys
    criteria_list = metrics_dict[model_criteria]
    best_model_at_epoch = criteria_list.index(max(criteria_list)) + 1 if type(criteria_list) == list else 1

    # Gathering all measures to one list
    training_stats = [[folder] * num_epochs, list(range(1, num_epochs + 1)),metrics_dict["acc_macro"], metrics_dict["prec_macro"], metrics_dict["rec_macro"], 
                    metrics_dict["f1_macro"], metrics_dict["auc_macro"], metrics_dict["acc_micro"], metrics_dict["prec_micro"],
                    metrics_dict["rec_micro"], metrics_dict["f1_micro"], metrics_dict["auc_micro"], metrics_dict["rec_at_5"],
                    metrics_dict["prec_at_5"], metrics_dict["f1_at_5"], metrics_dict["rec_at_8"],
                    metrics_dict["prec_at_8"], metrics_dict["f1_at_8"], metrics_dict["rec_at_15"],
                    metrics_dict["prec_at_15"], metrics_dict["f1_at_15"], metrics_dict["loss_dev"], metrics_dict["loss_tr"]]
    
    # Not all metrics exist for one experiment, some None returned from dict. Converting None to [None] * num_epochs
    training_stats = list(map(lambda x: [None] * num_epochs if x == None else x, training_stats ))

    # When only one epoch has been exceptionally run, metrics are floats, not lists.
    # Wrapping floats to lists
    training_stats = list(map(lambda x: [x] if type(x) == float else x, training_stats)) 

    # All lists should be of equal length, testing for it
    lenght_of_lists = list(map(lambda x: len(x), training_stats))
    assert len(set(lenght_of_lists)) == 1, "metrics.json in folder {} may be corrupt, please check file".format(folder)


    # Transposing to have one line of measures per epoch
    training_stats = np.asarray(training_stats)
    training_stats = training_stats.T
    training_stats = training_stats.tolist()

    return num_epochs, best_model_at_epoch, training_stats

def list_wrap_remove(var):
    """
    Helper function for removing list wrapping for a single item that might be wrapped into a list

    """
    if type(var) == list and len(var) > 1:
        # If an actual list, return the list
        return var
    elif type(var) == list and len(var) == 1:
        # If a list of one item, unpack
        return var[0]
    else:
        return var

def quote_remover(var):
    """ 
    Helper function for removing extra quotes from a variable in case it's a string.
    
    """
    if type(var) == str:
        # If string, replace quotes, strip spaces
        return var.replace("'", "").replace('"','').strip()
    else:
        # If not string, return input
        return

def dict_key_editer(var):
    """
    Helper function for changing MIMIC-II specific measures to align with MIMIC-III.

    MIMIC-II has no validation set, hence test losses produced during training.
    """
    if var == "loss_test":
        return "loss_dev"
    else:
        return var

def len_float_or_list(var):
    """
    Helper function for handling cases where only one epoch was run. 
    
    These abnormal cases result in a float instead of a list, hence len() would create an exception.
    """
    if type(var) == list:
        return len(var)
    elif type(var) == float:
        return 1
    else:
        return len(var)

def get_folder_name(full_path):
    """
    Helper function for retrieving folder name from folder full path.

    """
    # Use regex from https://stackoverflow.com/questions/29901266/regular-expression-to-find-last-folder-in-a-path
    # to clean folder name
    pattern = re.compile(".*\\\\([^\\\\]+)\\\\")
    match = pattern.search(full_path)
    folder = match.group(1)

    return folder

def true_false_converter(value):
    """
    Helper function to convert booleans into 0/1 as SQlite doesn't have a boolean data type.

    Converting to strings to follow formatting of other values in the input. Relying on later part of pipeline to change to int.

    """
    if value == "True":
        return '1'
    elif value == "False":
        return '0'
    else:
        return value
