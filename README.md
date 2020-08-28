# Storing machine learning experiments to SQlite-database
While working on my BSc thesis on predicting ICD codes from clinical notes with pretrained language models, I noticed that as the amount of experiments grew to tens, keeping track of the different experiments became time consuming or even impossible. As it seemed I might need to perform between fifty and hundred experiments during the process, a more formal solution was required. Therefore, I created this small tool enabling me to read in the hyperparameters utilized in each experiment and the respective training, validation and test performance and storing it all into a SQlite-database. This database can be then easily either directly queried or used for visualizations in Python or in tools such as Power BI.

Examples of the file structures that are handled can be found in [this folder](./test_cases/test1bert_Jul_29_16_00_31_test1). The files were slightly edited for testing and publishing purposes. The use of the tool requires creating file config.py, with two variables “folder_experiments” and “db_location”. In the variables, path names need to use double Windows backslashes (“\\”).

## Learning during the project
- Right from the start it was clear tests were needed. Due to the detail-oriented nature of loading in data, tests are the only way to capture errors. The tests helped me in finding multiple errors and fixing them. It might be beneficial to add even some more tests.
- Mapping data from files to database columns was very cumbersome, maybe there is a better way to handle it?
