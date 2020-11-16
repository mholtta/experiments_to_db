CREATE TABLE IF NOT EXISTS Experiments (
	FolderName TEXT NOT NULL PRIMARY KEY,
	Data TEXT NOT NULL, -- For storing data path
	ICDCodeSet TEXT NOT NULL, -- Full or top 50
	Version TEXT NOT NULL,
	MaxLength INTEGER NOT NULL,
	BertMaxLength INTEGER,
	JobID INTEGER,
	Model TEXT NOT NULL,
	FilterSize INTEGER NOT NULL,
	NumFilterMaps INTEGER NOT NULL,
	NumEpochs INTEGER NOT NULL,
	Dropout REAL NOT NULL,
	Patience INTEGER NOT NULL,
	BatchSizeTrain INTEGER NOT NULL,
	BatchSizeTest INTEGER NOT NULL,
	LearningRate FLOAT NOT NULL,
	Optimizer TEXT NOT NULL,
	WeightDecay REAL NOT NULL,
	Criterion TEXT NOT NULL,
	UseLrScheduler INTEGER, -- Boolean
	WarmUp REAL,
	UseLrLayerDecay INTEGER, -- Boolean
	LrLayerDecay REAL,
	TuneWordEmbedding INTEGER NOT NULL, -- Boolean
	RandomSeed INTEGER NOT NULL,
	UseExternalEmbedding INTEGER NOT NULL,
	NumWorkers INTEGER,
	ElmoTune INTEGER NOT NULL, -- Boolean
	ElmoDropOut REAL NOT NULL,
	ElmoGamma REAL NOT NULL,
	UseElmo INTEGER NOT NULL, -- Boolean
	PreTrainedModel TEXT NOT NULL,
	Date TEXT NOT NULL,
	Time TEXT NOT NULL,
	EpochsRun INTEGER NOT NULL,
	BestModelAtEpoch INTEGER NOT NULL,
	ExperimentFinalized INTEGER -- Boolean
);

CREATE TABLE IF NOT EXISTS TrainingStatistics (
	FolderName TEXT NOT NULL,
	Epoch INTEGER NOT NULL,
	MacroAccuracy REAL,
	MacroPrecision REAL,
	MacroRecall REAL,
	MacroF1 REAL,
	MacroAUC REAL,
	MicroAccuracy REAL,
	MicroPrecision REAL,
	MicroRecall REAL,
	MicroF1 REAL,
	MicroAUC REAL,
	RecallAt5 REAL,
	PrecisionAt5 REAL,
	F1At5 REAL,
	RecallAt8 REAL,
	PrecisionAt8 REAL,
	F1At8 REAL,
	RecallAt15 REAL,
	PrecisionAt15 REAL,
	F1At15 REAL,
	LossValidation REAL,
	LossTraining REAL,
	PRIMARY KEY (FolderName, Epoch),
	FOREIGN KEY(FolderName) REFERENCES Experiments(FolderName)
);

CREATE TABLE IF NOT EXISTS TestStatistics (
	FolderName TEXT NOT NULL PRIMARY KEY,
	MacroAccuracy REAL,
	MacroPrecision REAL,
	MacroRecall REAL,
	MacroF1 REAL,
	MacroAUC REAL,
	MicroAccuracy REAL,
	MicroPrecision REAL,
	MicroRecall REAL,
	MicroF1 REAL,
	MicroAUC REAL,
	RecallAt5 REAL,
	PrecisionAt5 REAL,
	F1At5 REAL,
	RecallAt8 REAL,
	PrecisionAt8 REAL,
	F1At8 REAL,
	RecallAt15 REAL,
	PrecisionAt15 REAL,
	F1At15 REAL,
	LossTest REAL,
	FOREIGN KEY(FolderName) REFERENCES Experiments(FolderName)
);


DROP VIEW IF EXISTS Leaderboard;

-- View with top instances for each model based on test MicroF1-score
CREATE VIEW IF NOT EXISTS Leaderboard
AS
	SELECT Experiments.*, TestStatistics.*
    FROM Experiments, TestStatistics
    WHERE Experiments.FolderName = TestStatistics.FolderName AND TestStatistics.FolderName IN
        (SELECT TestStatistics.FolderName
            FROM TestStatistics, Experiments
            WHERE Experiments.FolderName = TestStatistics.FolderName
            GROUP BY Experiments.Model, Experiments.Version, Experiments.ICDCodeSet
            HAVING MAX(TestStatistics.MicroF1)
        )
    ORDER BY Experiments.Version, Experiments.ICDCodeSet, TestStatistics.MacroF1 DESC;

-- New view
CREATE VIEW IF NOT EXISTS Leaderboard
AS
	SELECT Experiments.*, TestStatistics.*
    FROM Experiments, TestStatistics
    WHERE Experiments.FolderName = TestStatistics.FolderName AND TestStatistics.FolderName IN
        (SELECT TestStatistics.FolderName
            FROM TestStatistics, Experiments
            WHERE Experiments.FolderName = TestStatistics.FolderName
            GROUP BY Experiments.Model, Experiments.Version, Experiments.ICDCodeSet, Experiments.UseElmo 
            HAVING MAX(TestStatistics.MacroF1)
        )
    ORDER BY Experiments.Version, Experiments.ICDCodeSet, TestStatistics.MacroF1 DESC;