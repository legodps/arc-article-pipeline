# EXAM
EXAM is a tool designed to read in articles and evaluate them on a set of questions to see how informative
or useful they are. The score produced, sometimes referred to as "informativeness", is called the EXAM score. This 
tool is designed to use questions from the  [TQA question data set from](http://data.allenai.org/tqa/) 
dataset, specifically: "tqa_v1_train.json" and JSONL articles formatted in a particular way (ToDo clarify this)

# Setup Instructions

### 1. Install python 3
Download and install python 3 from the [Python Website](https://www.python.org/downloads/), you will need python 3.6
installed to be able to run the sub-program of [ARC-Solver](https://github.com/allenai/ARC-Solvers), but you can run
this benchmark tool with 3.7+.

### 2. Create Virtual env (optional)
Virtual environments are not required but are recommended, as they allow you to have versions of packages installed
according to the needs of a project rather than the highest/lowest common denominator. Instructions paraphrased from
here: [Virtual Env Docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/). 
My instructions are for linux, though the docs explain for windows as well.

#### a. Install Virtual Env
Run this command to install virtualenv.
`python3 -m pip install --user virtualenv`
You may encounter a permissions issue, however, sudo'ing this command should fix that 

#### b. Create Virtual Env
Run this command to create the Virtual Env
`python3 -m venv env`
This will create a folder within the downloaded project called `env` where the virtual environment information will be
stored

#### c. Turning on the Virtual Env
Run this command to turn the Virtual Environment on
`source env/bin/activate/`

### 3. Install Dependencies
Run this command to have pip install dependencies (or upgrade them) based on the included requirements list
`pip3 install --upgrade -r requirements.txt`

### 4. Install Elasticsearch
Elasticsearch is a non-relational database that is often used for storing textual data. This project was built with
Elasticsearch 7.X.X in mind (specifically Elasticsearch 7.6.2 but others should work just fine). You can download
Elasticsearch [here](https://www.elastic.co/downloads/elasticsearch).

By default, Elasticsearch can only support 1000 active, open indices. While Elasticsearch doesn't recommend doing any
more than that, for our purposes we need around 2500, see instructions on running the pipeline to see how to do so.

### 5. Installing ARC
To be able to run this benchmark on the ARC solver, which this is intended for, it requires a bit of setup.
The ARC Solver repo can be found here: [ARC-Solver](https://github.com/allenai/ARC-Solvers)

We make the assumption that the [ARC-Solver](https://github.com/allenai/ARC-Solvers) project will not be significantly
updated again, as it hasn't received a commit to master since August 2018 as of this readme. Should it be updated, for
posterity the link below is the exact commit that this project was designed to use: 
[ARC-Solver commit](https://github.com/allenai/ARC-Solvers/commit/8f21cb821b3a457f25535ccd1b5cddb01ed1bc4e)

Once you have downloaded the ARC-Solver project, follow their setup instructions to set up the ARC-Solver. It should
be noted that some additional work need to be done to allow it to function with this benchmark. 

#### a. Apply the patch
In the `/arc_solver_path` directory is a .patch file that you can apply to the ARC-Solver project. This project was
developed in [Pycharm](https://www.jetbrains.com/pycharm/), the community edition does allow one to create and apply
patches. We recommend you use that if you do not already have a way to apply .patch files. 

#### b. Copy Question Tupilizer
As part of the ARC-Solver downloading data, it will download a file located at `ARC-Solver/data/ARC-V1-Models-Aug2018`.
If it does not exist create a directory at `ARC-Solver/data/ARC-V1-Models-Feb2018`. Then copy
`ARC-Solver/data/ARC-V1-Models-Aug2018/question-tupilizer.jar` to
`ARC-Solver/data/ARC-V1-Models-Feb2018/question-tupilizer.jar`. This is necessary for ARC-Solver to use the jar when
it is running on data.

#### c. Test it out
Before launching the pipeline, make sure to test out these changes. If properly set up, you can follow the instructions
of to run the benchmark with the `decompatt` model.

IMPORTANT: you need to include an additional command line argument, that being the index for the ARC-Solver to look at.
This was hard coded originally, the patch, among other things, changes this so that the index in Elasticsearch can be
specified.

### 6. Download TQA dataset
This project uses the questions and the corpus from the TQA Dataset. To be able to run this benchmark, you need to
download the dataset here: [TQA dataset](https://allenai.org/data/tqa) and extract/unzip the files. In the config file,
make sure you specify the filepath to the TQA file: `tqa_v1_train.json` with the property `question_directory`. By
default in the extracted files you can find it at `tqa_train_val_test/train/tqa_v1_train.json`. As long as the config
is given the correct directory, you can move that file anywhere you want.


# Configuring the Project
In addition to terminal arguments, you can configure the benchmark via a yaml file with the following properties

### Properties you might need to change
* `host`: the hostname of the Elasticsearch database, default is `localhost`, required
* `port`: the port of the Elasticsearch database, default is `9200`, required
* `article_directory`: the filepath to a singular, or directory of, JSONL article files. This config setting is
    overridden if a different path is specified via terminal arguments. This is provided for convenience of multiple
    runs.
* `question_directory`: the filepath to a singular, or directory of, JSON question files. This config setting is
    overridden if a different path is specified via terminal arguments. This is provided for convenience of multiple
    runs.
* `arc_solver_directory`: the filepath to where the base ARC-Solver directory is. This config setting is overridden if a
    different path is specified via terminal arguments. This is provided for convenience of multiple runs.
* `conda_environment_name`: as part of the setup of the ARC-Solver project, you need to create a conda environment,
    much like a python environment. This must be set to the name of the conda environment you created as part of that
    setup.

### Properties you probably shouldn't change
* `benchmark_set_directory`: the filepath where questions sets should be saved to. DO NOT NAME IT TO ANY EXISTING 
    DIRECTORY, THE DEFAULT IS FINE. It is not recommended to change the directory location as it and all files within it
    will be deleted and recreated by running the benchmark deleted and recreated on successive runs.
* `arc_data_subdirectory`: the directory path to the Challenging test sets which the ARC-Solver evaluates on by default.
    This should not need changed as this is already pre-configured to the right series of subdirectories.
* `arc_model_subdirectory`: the directory path to the model ARC-Solver will use to evaluate the articles with. This
    should not be altered as the decompatt model is sufficient to test the articles.
* `checkpoint_directory`: the directory checkpoints in the running of the arc_benchmark files should be saved to. This
    includes files that track the progress of the run and the results files.
* `arc_checkpoint_file`: the file that stores results from the ARC-Solver runs in real time.
* `arc_results_file`: the file that the processed results from the ARC-solver run will be stored to.
* `final_results_file`: the file containing the digested results of the different article methods are stored in.
* `individual_question_results_file`: the file containing the results of individual questions on individual articles.
* `arc_corpus_index`: the index that ARC-Solver default corpus will be stored at. Once saved, it is strongly advised you
    do not change this. If you are not using any ARC data you don't need to worry about this, changing it or otherwise.
* `max_question_disagreement`: the maximum percentage of articles allowed to disagree on the results of a run before
    the benchmark considers a question to lack consensus. This is used in evaluating the results.
* `mapping`: the Elasticsearch index map. This is used to configure the indices of the articles for the best retrieval.
    Its default should be sufficient.
    
A default config file is provided [benchmarkConfig.yaml](benchmarkConfig.yaml)

# Running the Project

### 1. Start up Elasticsearch
In a terminal window, run the following commands. It may take a few minutes for Elasticsearch to boot up properly if
you have run the pipeline before. You should know it is ready when it mentions going from "red" to "yellow" or "green"
```
cd directory/to/elasticsearch/bin
source elasticsearch
```

### 2. Update Elasticsearch shart count
Once Elasticsearch is ready, open up a different terminal window and run the following command if you have over 1000
articles.
```
curl -XPUT localhost:9200/_cluster/settings -H 'Content-type: application/json' --data-binary $'{"transient":{"cluster.max_shards_per_node":2500}}'
```
This will make sure if you run the benchmark, that it can maintain enough active indices for our uses

### 3. Run the benchmark
in the `arc-pipeline` project directory, run the following command to turn on the python environment
```
source env/bin/activate/
```
Then use the following command to intiate the benchmark
```
python -m arc_benchmark -c path/to/config/file --article_directory path/to/article/directory --question_directory path/to/question/directory
```
This may take a number of hours to run, as the benchmark needs to extract questions and articles from files, save them
to Elasticsearch, then run the benchmark. Each individual run of the benchmark takes a hair under 20 seconds on my
laptop. All told, it took around 12 hours to run.

With the additional shards introduced, I have noticed an issue where ARC/elasticsearch gets bogged down on my local
machine. It causes errors, and retrying the operation a couple times works. However, if you see it restarting a lot in
the logs, I recommend you shut down the progress and reboot your computer. The checkpoint file will keep your progress
so nothing will be lost, and it will likely help Elasticsearch process the requests faster. There may be a way to fix
this on the Elasticsearch side by giving it more memory but I couldn't get it to work.

### What does EXAM Do?
IT operates in 3 steps.
1. Loads in articles and stores them to Elasticsearch
2. Loads in questions and stores them in JSONL files for later use
3. Runs the ARC-Solvers against a series of articles and question sets

# Testing Instructions
To see if unit tests pass and the coverage level run the following commands. All tested files should be at 100%
coverage. Some additional scripts are included in the main directory though they are just scripts used to calculate
results used in the associated paper.
```
coverage run --omit=tests/**,**/__init__.py,env/** -m unittest 
coverage report
coverage html
```
The first command runs the tests, the second prints a coverage report to the terminal, and the third creates a
web-browsable version to allow you to look visually where coverage is missing and explore the files

# Common Issues
If you get a "read-only" issue from Elasticsearch, this could be due to how much free space is left on your system. If
your hard drive is 95% full, it will not let you re-index documents. Clear up some space on your hard drive and try
again.

# Additional Scripts
Several scripts have been included to help calculate results, we describe them briefly here if people wish to validate
our results the way we originally calculated them.

* `calculate_correlation.py`: calculates the correlation between the different metrics used in our work. It is
    prepopulated with all the information you need but will need changed if you use different articles.
* `calculate_existing_eval_average.py`: calculates the average of NDCG@20, MAP, and Precision at R for the TREC CAR
    Y3 data, unless you wish to validate the results of our tables you shouldn't need this. If you do wish to use this,
    you may need to change the directory information in the script
* `calculate_rouge.py`: calculates the ROUGE-1 precision, recall, and f1 for a set of articles versus the TQA data,
    if you wish to use this you will need to change the directory locations to the appropriate position
* `quantitative_evaluation.py`: examines overlap or distinction between two different sets of articles in how they
    sucessfully or unsuccessfully answer questions.


