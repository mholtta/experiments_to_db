import unittest
from file_processing import out_file_processing, metrics_file_processing


class TestFileProcessing(unittest.TestCase):

    def test_out_file_processing1(self):
        accepted_output_experiment = ["bert_Jul_29_16_00_31_test1", "/test", "50", "3",
                            "2500", "512", None, "bert", "3", "25", "8", "0.2", "10",
                            "16", "0.0001", "AdamW", "0.1", "f1_macro", "True", "0.1", "True", "0.95", "False",
                            "12", "1", "10", "False", "0", "0.1", "0",
                            "emilyalsentzer/Bio_ClinicalBERT", "2020-07-29", "16:00"]

        accepted_model_criteria = "f1_macro"

        folder = '.\\test_cases\\bert_Jul_29_16_00_31_test1\\'

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

        folder = '.\\test_cases\\bert_Jul_29_16_00_31_test1\\'

        with open(folder + "metrics.json", "r") as metrics_file:
            num_epochs, best_model_at_epoch, training_statistics, test_statistics = metrics_file_processing(folder, metrics_file, accepted_model_criteria)

            self.assertEqual(num_epochs, 1, "Should be {}, was {}".format( 1, num_epochs))
            self.assertEqual(best_model_at_epoch, 1, "Should be {}, was {}".format( 1, best_model_at_epoch))
            self.assertEqual(training_statistics, train_should_be, "Should be {}, was {}".format(train_should_be, training_statistics))
            self.assertEqual(test_statistics, test_should_be, "Should be {}, was {}".format(test_should_be, test_statistics))

    


if __name__ == '__main__':
    unittest.main()