CREATE TABLE IF NOT EXISTS Experiments (
	FolderName TEXT NOT NULL PRIMARY KEY,
	Data TEXT NOT NULL, -- For storing data path
	ICDCodeSet TEXT NOT NULL, -- Full or top 50
	Version TEXT NOT NULL,
	MaxLength INTEGER NOT NULL,
	BertMaxLenght INTEGER NOT NULL,
	JobID INTEGER NOT NULL UNIQUE,
	Model TEXT NOT NULL,
	FilterSize INTEGER NOT NULL,
	NumFilterMaps INTEGER NOT NULL,
	NumEpochs INTEGER NOT NULL,
	Dropout REAL NOT NULL,
	Patience INTEGER NOT NULL,
	BatchSize INTEGER NOT NULL,
	LearningRate INTEGER NOT NULL,
	Optimizer INTEGER NOT NULL,
	WeightDecay REAL NOT NULL,
	Criterion TEXT NOT NULL,
	UseLrScheduler INTEGER NOT NULL, -- Boolean
	WarmUp REAL NOT NULL,
	UseLrLayerDecay INTEGER NOT NULL, -- Boolean
	LrLayerDecay REAL NOT NULL,
	TuneWordEmbedding INTEGER NOT NULL, -- Boolean
	RandomSeed INTEGER NOT NULL,
	UseExternalEmbedding INTEGER NOT NULL,
	NumWorkers INTEGER NOT NULL,
	ElmoTune INTEGER NOT NULL, -- Boolean
	ElmoDropOut REAL NOT NULL,
	ElmoGamma REAL NOT NULL,
	UseElmo INTEGER NOT NULL, -- Boolean
	PreTrainedModel TEXT NOT NULL,
	Runtime TEXT,
	EpochsRun INTEGER,
	BestModelAtEpoch INTEGER
);

CREATE TABLE IF NOT EXISTS TrainingStatistics (
	FolderName TEXT NOT NULL,
	Epoch INTEGER NOT NULL,
	MacroAccuracy REAL NOT NULL,
	MacroPrecision REAL NOT NULL,
	MacroRecall REAL NOT NULL,
	MacroF1 REAL NOT NULL,
	MacroAUC REAL NOT NULL,
	MicroAccuracy REAL NOT NULL,
	MicroPrecision REAL NOT NULL,
	MicroRecall REAL NOT NULL,
	MicroF1 REAL NOT NULL,
	MicroAUC REAL NOT NULL,
	RecallAt5 REAL,
	PrecisionAt5 REAL,
	F1At5 REAL,
	LossValidation REAL NOT NULL,
	LossTraining REAL NOT NULL,
	PRIMARY KEY (FolderName, Epoch),
	FOREIGN KEY(FolderName) REFERENCES Experiments(FolderName)
);

CREATE TABLE IF NOT EXISTS TestStatistics (
	FolderName TEXT NOT NULL PRIMARY KEY,
	MacroAccuracy REAL NOT NULL,
	MacroPrecision REAL NOT NULL,
	MacroRecall REAL NOT NULL,
	MacroF1 REAL NOT NULL,
	MacroAUC REAL NOT NULL,
	MicroAccuracy REAL NOT NULL,
	MicroPrecision REAL NOT NULL,
	MicroRecall REAL NOT NULL,
	MicroF1 REAL NOT NULL,
	MicroAUC REAL NOT NULL,
	RecallAt5 REAL,
	PrecisionAt5 REAL,
	F1At5 REAL,
	FOREIGN KEY(FolderName) REFERENCES Experiments(FolderName)
);