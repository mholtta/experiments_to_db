import sqlite3
import glob
from config import folder_experiments, db_location
import warnings
from file_processing import metrics_file_processing, out_file_processing
from typing import List, Union, Optional

def main(db_name: str, folder_for_experiments: str):
    # Folders containing experiments 
    folders = glob.glob(folder_for_experiments + "*/")
    # Connecting to db and creating cursor
    connection = sqlite3.connect(db_name)
    cur = connection.cursor()

    # Creating tables, if not exists already
    prepare_database(connection, cur, "DB_preparation.sql")
    
    # Going through each experiment and gathering data
    for folder in folders:
        try:
            # Finding out-file for gathering experiment details
            out_files = glob.glob("".join([folder, "*.out"]))

            if len(out_files) > 1:
                warnings.warn("Folder {} has several out-files, file not processed.".format(folder))
            else:
                out_file = out_files[0]
                metrics_file = "".join([folder, "metrics.json"])

                with open(out_file, "r") as out_f, open(metrics_file) as m:
                    
                    # First process *.out-file, obtain experiment description. Model_criterion needed to obtain best_model_at_epoch from metrics file.
                    experiment, model_criteria = out_file_processing(folder, out_f)

                    # Then get training and test statistics from metrics.json. And also additional experiment info
                    num_epochs, best_model_at_epoch, training_statistics, test_statistics = metrics_file_processing(folder, m, model_criteria)

                    # Appending num_epochs and best_model_at_epoch gotten from metrics.json to experiment desciption
                    experiment.append(num_epochs)
                    experiment.append(best_model_at_epoch)

                    # Storing data to database
                    experiment_to_db(cur, experiment)
                    test_statistics_to_db(cur, test_statistics)
                    training_statistics_to_db(cur, training_statistics)
                                        
                    # Ending the implicit transaction only after all inserts done for one experiment to improve performance
                    connection.commit()
        except (AssertionError, FileNotFoundError) as error:
            print(error)



    connection.close()

def experiment_to_db(cur: sqlite3.Cursor, experiment: List[str]):
    """
    A helper function for storing the experiment information to the database.

    The input experiment needs to be in the order of columns specified within this function.

    """
    cur.execute("""INSERT OR IGNORE INTO Experiments(FolderName, Data, ICDCodeSet,
                    Version, MaxLength, BertMaxLength, JobID, Model, FilterSize, NumFilterMaps, NumEpochs,
                    Dropout, Patience, BatchSizeTrain, BatchSizeTest, LearningRate, Optimizer, WeightDecay, Criterion, UseLrScheduler,
                    WarmUp, UseLrLayerDecay, LrLayerDecay, TuneWordEmbedding, RandomSeed, UseExternalEmbedding, 
                    NumWorkers, ElmoTune, ElmoDropOut, ElmoGamma, UseElmo, PreTrainedModel, Date, Time, EpochsRun, 
                    BestModelAtEpoch) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", experiment)

def test_statistics_to_db(cur: sqlite3.Cursor, test_statistics: List[Union[str, int, float]]):
    """
    A helper function for storing the test statistics to the database.

    The input test_statistics needs to be in the order of columns specified in this function.

    """
    cur.execute("""INSERT OR IGNORE INTO TestStatistics(FolderName, MacroAccuracy, 
                                MacroPrecision, MacroRecall, MacroF1, MacroAUC, MicroAccuracy, MicroPrecision,
                                MicroRecall, MicroF1, MicroAUC, RecallAt5, PrecisionAt5, F1At5, RecallAt8,
                                PrecisionAt8, F1At8, RecallAt15, PrecisionAt15, F1At15, LossTest)
                                VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", test_statistics)

def training_statistics_to_db(cur: sqlite3.Cursor, training_statistics: List[List[Union[str, int, float]]]):
    """
    A helper function for storing the training statistics to the database.

    The input training_statistics needs to be in the order of columns specified in this function.

    """
    for row in training_statistics:
                        cur.execute("""INSERT OR IGNORE INTO TrainingStatistics(FolderName, Epoch, MacroAccuracy, 
                                    MacroPrecision, MacroRecall, MacroF1, MacroAUC, MicroAccuracy, MicroPrecision,
                                    MicroRecall, MicroF1, MicroAUC, RecallAt5, PrecisionAt5, F1At5, RecallAt8,
                                    PrecisionAt8, F1At8, RecallAt15, PrecisionAt15, F1At15, LossValidation, LossTraining)
                                    VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", row)

def prepare_database(connection: sqlite3.Connection, cur: sqlite3.Cursor, sql_file: str):
    """
    A helper function for preparing the database, i.e. running the SQL-script in the given file.

    """
    # Creating tables, if not exists already
    with open(sql_file, "r") as sql_script:
        scripts = sql_script.read().split(";")
        for script in scripts:
            cur.execute(script)
            connection.commit()


if __name__ == "__main__":
    main(db_location, folder_experiments)