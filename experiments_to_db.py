import sqlite3
import glob
from config import folder_experiments
import warnings
from file_processing import metrics_file_processing, out_file_processing

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

        with open(out_file, "r") as out_f, open(metrics_file) as m:
            
            # First process *.out-file, obtain experiment description. Model_criterion needed to obtain best_model_at_epoch from metrics file.
            experiment, model_criteria = out_file_processing(folder, out_f)

            # Then get training and test statistics from metrics.json. And also additional experiment info
            num_epochs, best_model_at_epoch, training_statistics, test_statistics = metrics_file_processing(folder, m, model_criteria)

            # Appending num_epochs and best_model_at_epoch gotten from metrics.json to experiment desciption
            experiment.append(num_epochs, best_model_at_epoch)

            cur.execute("""INSERT OR IGNORE INTO Experiments(FolderName, Data, ICDCodeSet,
             Version, MaxLength, BertMaxLength, JobID, Model, FilterSize, NumFilterMaps, NumEpochs,
             Dropout, Patience, BatchSize, LearningRate, Optimizer, WeightDecay, Criterion, UseLrScheduler,
             WarmUp, UseLrLayerDecay, LrLayerDecay, TuneWordEmbedding, RandomSeed, UseExternalEmbedding, 
             NumWorkers, ElmoTune, ElmoDropOut, ElmoGamma, UseElmo, PreTrainedModel, Date, Time, EpochsRun, 
             BestModelAtEpoch) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
             ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", experiment)
            
            cur.execute("""INSERT OR IGNORE INTO TestStatistics(FolderName, MacroAccuracy, 
                        MacroPrecision, MacroRecall, MacroF1, MacroAUC, MicroAccuracy, MicroPrecision,
                        MicroRecall, MicroF1, MicroAUC, RecallAt5, PrecisionAt5, F1At5, RecallAt8,
                        PrecisionAt8, F1At8, RecallAt15, PrecisionAt15, F1At15)
                        VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", test_statistics)
            
            for row in training_statistics:
                cur.execute("""INSERT OR IGNORE INTO TestStatistics(FolderName, Epoch, MacroAccuracy, 
                            MacroPrecision, MacroRecall, MacroF1, MacroAUC, MicroAccuracy, MicroPrecision,
                            MicroRecall, MicroF1, MicroAUC, RecallAt5, PrecisionAt5, F1At5, RecallAt8,
                            PrecisionAt8, F1At8, RecallAt15, PrecisionAt15, F1At15, LossValidation, LossTraining)
                            VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", row)
            
            # Ending the implicit transaction only after all inserts done for one experiment to improve performance
            connection.commit()
            



    

connection.close()