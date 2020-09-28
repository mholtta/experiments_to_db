import unittest
from file_processing import out_file_processing, metrics_file_processing
from experiments_to_db import main, prepare_database, training_statistics_to_db
import os
import sqlite3

class TestFileProcessing(unittest.TestCase):

    def test_out_file_processing1(self):
        accepted_output_experiment = ["bert_Jul_29_16_00_31_test1", "/test", "50", "3",
                            "2500", "512", None, "bert", "3", "25", "8", "0.2", "10",
                            "16", "1","0.0001", "AdamW", "0.1", "f1_macro", "1", "0.1", "1", "0.95", "0",
                            "12", "1", "10", "0", "0", "0.1", "0",
                            "emilyalsentzer/Bio_ClinicalBERT", "2020-07-29", "16:00"]

        accepted_model_criteria = "f1_macro"

        folder = '.\\test_cases\\test1\\bert_Jul_29_16_00_31_test1\\'

        with open(folder + "50_bert-3049122.out", "r") as out_file:
            experiment, model_criteria = out_file_processing(folder, out_file)

            self.assertEqual(model_criteria, accepted_model_criteria, "Should be {}".format(accepted_model_criteria))
            self.assertEqual(experiment, accepted_output_experiment, "Should be {}, was {}".format(accepted_output_experiment, experiment))

    def test_metrics_file_processing1(self):
        train_should_be = [["bert_Jul_29_16_00_31_test1", 1, 0.12256332660210358, 0.363838405232041, 0.13938095183833726, 
                        0.20155084467266288, 0.7546829688684804, 0.17801517571884984, 0.708664546899841, 0.1920715286006679,
                        0.30222900245783546, 0.7969872933891264, 0.39765466424460405, 0.4247933884297521, 0.4107762714011657,
                        None, None, None, None, None, None, 0.29043236369171194, 0.3209881045440636]]

        test_should_be = ["bert_Jul_29_16_00_31_test1", 0.2605752081966306, 0.5707946225340355, 0.32442195023603754, 
                        0.4137061583963679, 0.8045001977638817, 0.31853967273849954, 0.624735089312746, 0.39391047055454803,
                        0.4831704033249429, 0.8435083702198041, 0.4852368130325467, 0.5061885482938114, 0.49549129475376935,
                        None, None, None, None, None, None, 0.2759021656849503]

        accepted_model_criteria = "f1_macro"

        folder = '.\\test_cases\\test1\\bert_Jul_29_16_00_31_test1\\'

        with open(folder + "metrics.json", "r") as metrics_file:
            num_epochs, best_model_at_epoch, training_statistics, test_statistics = metrics_file_processing(folder, metrics_file, accepted_model_criteria)

            self.assertEqual(num_epochs, 1, "Should be {}, was {}".format( 1, num_epochs))
            self.assertEqual(best_model_at_epoch, 1, "Should be {}, was {}".format( 1, best_model_at_epoch))
            self.assertEqual(training_statistics, train_should_be, "Should be {}, was {}".format(train_should_be, training_statistics))
            self.assertEqual(test_statistics, test_should_be, "Should be {}, was {}".format(test_should_be, test_statistics))

    
    def test_main1(self):
        folder = '.\\test_cases\\test1\\'
        db_location = '.\\test_cases\\test_db.db'

        accepted_output_experiment = [("bert_Jul_29_16_00_31_test1", "/test", "50", "3",
                            2500, 512, None, "bert", 3, 25, 8, 0.2, 10,
                            16, 1,0.0001, "AdamW", 0.1, "f1_macro", 1, 0.1, 1, 0.95, 0,
                            12, 1, 10, 0, 0.0, 0.1, 0,
                            "emilyalsentzer/Bio_ClinicalBERT", "2020-07-29", "16:00", 1, 1, 1)]

        test_should_be = [("bert_Jul_29_16_00_31_test1", 0.2605752081966306, 0.5707946225340355, 0.32442195023603754, 
                        0.4137061583963679, 0.8045001977638817, 0.31853967273849954, 0.624735089312746, 0.39391047055454803,
                        0.4831704033249429, 0.8435083702198041, 0.4852368130325467, 0.5061885482938114, 0.49549129475376935,
                        None, None, None, None, None, None, 0.2759021656849503)]

        train_should_be = [("bert_Jul_29_16_00_31_test1", 1, 0.12256332660210358, 0.363838405232041, 0.13938095183833726, 
                        0.20155084467266288, 0.7546829688684804, 0.17801517571884984, 0.708664546899841, 0.1920715286006679,
                        0.30222900245783546, 0.7969872933891264, 0.39765466424460405, 0.4247933884297521, 0.4107762714011657,
                        None, None, None, None, None, None, 0.29043236369171194, 0.3209881045440636)]

        # First removing db, if exists
        if os.path.exists(db_location):
            os.remove(db_location)

        # Create the db and input data
        main(db_location, folder)

        
        # Connect to db, create cursor, query the db
        connection = sqlite3.connect(db_location)
        cur = connection.cursor()
        
        # First checking experiment table
        cur.execute("SELECT * FROM Experiments WHERE FolderName = 'bert_Jul_29_16_00_31_test1';" )
        experiment = cur.fetchall()
        self.assertEqual(experiment, accepted_output_experiment, "Should be {}, was {}".format(accepted_output_experiment, experiment))

        # Then checking test statistics
        cur.execute("SELECT * FROM TestStatistics WHERE FolderName = 'bert_Jul_29_16_00_31_test1';")
        test_statistics = cur.fetchall()
        self.assertEqual(test_statistics, test_should_be, "Should be {}, was {}".format(test_should_be, test_statistics))

        # Then checking training statistics
        cur.execute("SELECT * FROM TrainingStatistics WHERE FolderName = 'bert_Jul_29_16_00_31_test1' AND Epoch = 1;")
        train_statistics = cur.fetchall()
        self.assertEqual(train_statistics, train_should_be, "Should be {}, was {}".format(train_should_be, train_statistics))
        connection.close()
    
    def test_failed_training_run(self):
        # First setting up needed variables
        db_location = '.\\test_cases\\test_db.db'
        model_criteria = 'f1_macro'
        folder = '.\\test_cases\\test2\\elmo_Aug_24_10_39_10_test2\\'
        metrics_file = "".join([folder, "metrics.json"])
        train_should_be = [("elmo_Aug_24_10_39_10_test2", 3, 0.0, 0.0, 0.0, 0.0, 0.46579811244429226, 0.0, None, 0.0, None, 0.5750237367933662, 0.2069661320038722, 0.22364907819453272, 0.2149844387467271, None, None, None, None, None, None, 0.5515820256517863, 0.6169608133854252)]
        
        # First removing db, if exists
        if os.path.exists(db_location):
            os.remove(db_location)
        
        # Connecting to db and creating cursor
        connection = sqlite3.connect(db_location)
        cur = connection.cursor()

        # Creating tables, if not exists already
        prepare_database(connection, cur, 'DB_preparation.sql')

        # Opening metrics-file, getting training statistics and loading to database
        with open(metrics_file) as m:
            num_epochs, best_model_at_epoch, training_statistics, test_statistics = metrics_file_processing(folder, m, model_criteria)
            training_statistics_to_db(cur, training_statistics)
            connection.commit()
        
        # Obtaining one tuple from TrainingStatistics table and comparing to expected value
        cur.execute("SELECT * FROM TrainingStatistics WHERE FolderName = 'elmo_Aug_24_10_39_10_test2' AND Epoch = 3;" )
        train_from_db = cur.fetchall()
        self.assertEqual(train_from_db, train_should_be, "Should be {}, was {}".format(train_should_be, train_from_db))

    def test_not_finalized(self):
        folder = '.\\test_cases\\test3\\'
        db_location = '.\\test_cases\\test_db.db'

        accepted_output_experiment = [("bert_Jul_29_16_00_31_test3", "/test", "50", "3",
                            2500, 512, None, "bert", 3, 25, 8, 0.2, 10,
                            16, 1,0.0001, "AdamW", 0.1, "f1_macro", 1, 0.1, 1, 0.95, 0,
                            12, 1, 10, 0, 0.0, 0.1, 0,
                            "emilyalsentzer/Bio_ClinicalBERT", "2020-07-29", "16:00", 1, 1, 0)]

        test_should_be = []

        train_should_be = [("bert_Jul_29_16_00_31_test3", 1, 0.12256332660210358, 0.363838405232041, 0.13938095183833726, 
                        0.20155084467266288, 0.7546829688684804, 0.17801517571884984, 0.708664546899841, 0.1920715286006679,
                        0.30222900245783546, 0.7969872933891264, 0.39765466424460405, 0.4247933884297521, 0.4107762714011657,
                        None, None, None, None, None, None, 0.29043236369171194, 0.3209881045440636)]

        # First removing db, if exists
        if os.path.exists(db_location):
            os.remove(db_location)

        # Create the db and input data
        main(db_location, folder)

        
        # Connect to db, create cursor, query the db
        connection = sqlite3.connect(db_location)
        cur = connection.cursor()
        
        # First checking experiment table
        cur.execute("SELECT * FROM Experiments WHERE FolderName = 'bert_Jul_29_16_00_31_test3';" )
        experiment = cur.fetchall()
        self.assertEqual(experiment, accepted_output_experiment, "Should be {}, was {}".format(accepted_output_experiment, experiment))

        # Then checking test statistics
        cur.execute("SELECT * FROM TestStatistics WHERE FolderName = 'bert_Jul_29_16_00_31_test3';")
        test_statistics = cur.fetchall()
        self.assertEqual(test_statistics, test_should_be, "Should be {}, was {}".format(test_should_be, test_statistics))

        # Then checking training statistics
        cur.execute("SELECT * FROM TrainingStatistics WHERE FolderName = 'bert_Jul_29_16_00_31_test3' AND Epoch = 1;")
        train_statistics = cur.fetchall()
        self.assertEqual(train_statistics, train_should_be, "Should be {}, was {}".format(train_should_be, train_statistics))
        connection.close()

if __name__ == '__main__':
    unittest.main()