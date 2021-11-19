# EXAM
EXAM is a tool designed to read in articles and evaluate them on a set of questions to see how informative
or useful they are. The score produced, sometimes referred to as "informativeness", is called the EXAM score. This 
tool is designed to use questions formatted like these [example questions](examples/example_question_file.json),
and JSONL articles formatted like this
[example article](examples/example_article_set_file.jsonl). To learn more about creating articles or questions check 
out [createarticles.md](createarticles.md) and [createquestions.md](createquestions.md) respectively.

# Setup Instructions

### 1. Install python 3
Download and install python 3 from the [Python Website](https://www.python.org/downloads/)

### 2. Create a Virtual Environmnet (optional)
Virtual environments are not required but are recommended, as they allow you to have versions of packages installed
according to the needs of a project. Instructions paraphrased from
here: [Virtual Env Docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/). 
The instructions are for linux, though the docs explain for windows as well. You could also substitute with Conda.

#### a. Install Virtual Env
Run this command to install virtualenv.
`python3 -m pip install --user virtualenv`
You may encounter a permissions issue, however, sudo'ing this command should fix that 

#### b. Create the VirtualEnv
Run this command to create the Virtual Env
`python3 -m venv env`
This will create a folder within the downloaded project called `env` where the virtual environment information will be
stored

#### c. Turning on the Virtual Env
Run this command to turn the Virtual Environment on
`source env/bin/activate`

### 3. Install Dependencies
Run this command to have pip install dependencies (or upgrade them) based on the included requirements list
`pip3 install --upgrade -r requirements.txt`

Depending on your version of pip, you may need to upgrade pip by running:
`python -m pip install --upgrade pip`

This was discovered with an issue related to installing nltk.

### 4. Install Elasticsearch
Elasticsearch is a non-relational database that is often used for storing textual data. This project was built with
Elasticsearch 7.X.X in mind (specifically Elasticsearch 7.6.2 but others should work just fine). You can download
Elasticsearch [here](https://www.elastic.co/downloads/elasticsearch).

### 5. Installing ARC
To be able to run this benchmark on the ARC solver, which this is intended for, it requires a bit of setup.
The ARC Solver repo can be found here: [ARC-Solver](https://github.com/allenai/ARC-Solvers)

We make the assumption that the [ARC-Solver](https://github.com/allenai/ARC-Solvers) project will not be significantly
updated again, as it hasn't received a commit to master since August 2018 as of this readme. Should it be updated, for
posterity the link below is the exact commit that this project was designed to use: 
[ARC-Solver commit](https://github.com/allenai/ARC-Solvers/commit/8f21cb821b3a457f25535ccd1b5cddb01ed1bc4e)

Once you have downloaded the ARC-Solver project, follow their setup instructions to set up the ARC-Solver. It should
be noted that some additional work needs to be done to allow it to function with this benchmark. 

#### a. Apply the patch
In the `/arc_solver_path` directory is a .patch file that you need to apply to the ARC-Solver project. This project was
developed in [Pycharm](https://www.jetbrains.com/pycharm/), the community edition does allow the creation and
application of patches. We recommend you use that if you do not already have a way to apply .patch files. 

#### b. Copy Question Tupilizer
As part of the ARC-Solver downloading data, it will download a file located at `ARC-Solver/data/ARC-V1-Models-Aug2018`.
If it does not exist create a directory at `ARC-Solver/data/ARC-V1-Models-Feb2018`, then copy
`ARC-Solver/data/ARC-V1-Models-Aug2018/question-tupilizer.jar` to
`ARC-Solver/data/ARC-V1-Models-Feb2018/question-tupilizer.jar`. This jar is necessary for ARC-Solver to run properly.

#### c. Test it out
Before launching the pipeline, make sure to test out the QnA system. You can run the QnA system by executing the
following command:

``` 
sh scripts/evaluate_solver.sh \
	data/ARC-V1-Feb2018/ARC-Challenge/ARC-Challenge-Test.jsonl \
	data/ARC-V1-Models-Aug2018/decompatt/
	arc_corpus
```

NOTE: the original command in the ARC-Solver repo will not work because it is missing the additional parameter
provided in the above terminal command. If you rename the index where the ARC data is stored, you will need to change
`arc_corpus` to the appropriate value. If you simply went with defaults, the above command is fine.

#### Troubleshooting ARC failed ARC-Solver runs
The scripts that sets up the ARC-Solver project sometimes encounters issues installing libraries. If you have issues
running the decompatt model due to missing packages, activate the conda environment for ARC-Solver, and install the
missing packages like:

`conda install package-name`

if the package is not available in the default conda repo, you can most likely find it in the conda-forge repo. Install
from conda-forge by running:

`conda install package-name -c conda-forge`

You may need to specifically install spacy version 1.9.0, which can be installed by running:

`conda install spacy==1.9.0`

If you have issues not solved by the above, make sure the appropriate commit is downloaded. The setup script should
change the active commit, but if you are having issues, verify it is the commit mentioned in step 5. If that commit is
not the active commit, roll back changes until you get to that commit.

### 6. Download TQA dataset
This project uses the questions and the corpus from the TQA Dataset. To be able to run this benchmark, you need to
download the dataset here: [TQA dataset](https://allenai.org/data/tqa) and extract/unzip the files. In the config file,
make sure you specify the filepath to the TQA file: `tqa_v1_train.json` with the property `question_directory`. By
default in the extracted files you can find it at `tqa_train_val_test/train/tqa_v1_train.json`. As long as the config
is given the correct directory, you can move that file anywhere you want.


# Configuring the Project
In addition to terminal arguments, you can configure the benchmark via a yaml file with the following properties

### Properties you might need to change:
* `host`: the hostname of the Elasticsearch database, default is `localhost`, required
* `port`: the port of the Elasticsearch database, default is `9200`, required
* `article_directory`: the filepath to a singular, or directory of, JSONL article files. This config setting is
    overridden if a different path is specified via terminal arguments. This is provided for convenience of repeated
    runs.
* `question_directory`: the filepath to a singular, or directory of, JSON question files. This config setting is
    overridden if a different path is specified via terminal arguments. This is provided for convenience of repeated
    runs.
* `arc_solver_directory`: the filepath to where the base ARC-Solver directory is. This config setting is overridden if a
    different path is specified via terminal arguments. This is provided for convenience of repeated runs.
* `conda_environment_name`: as part of the setup of the ARC-Solver project, you need to create a conda environment,
    much like a python environment. This must be set to the name of the conda environment you created as part of that
    setup.

### Properties you probably shouldn't change:
* `benchmark_set_directory`: the filepath where questions sets should be saved to. DO NOT NAME IT TO ANY EXISTING 
    DIRECTORY, THE DEFAULT IS FINE. It is not recommended to change the directory location as it, and all files within 
    it, will be deleted and recreated by running the benchmark.
* `arc_data_subdirectory`: the directory path to the Challenging test sets which the ARC-Solver evaluates on by default.
    This should not need changed as this is already pre-configured to the right series of subdirectories.
* `arc_model_subdirectory`: the directory path to the model that ARC-Solver will use to evaluate the articles with. This
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
    
A default config file is provided [benchmarkConfig.yaml](benchmarkConfig.yaml), but it will require changes to be
usable.

# Running the Project

### 1. Start up Elasticsearch
In a terminal window, run the following commands. It may take a few minutes for Elasticsearch to boot up properly if
you have run the pipeline before. You should know it is ready when it mentions going from "red" to "yellow" or "green"
```
cd directory/to/elasticsearch/bin
source elasticsearch
```

### 2. Update Elasticsearch shard count (optional)
If running EXAM for many articles (more than 1000), the shard count needs updated. Once Elasticsearch is ready, open up a different terminal window and run the following command:
```
curl -XPUT localhost:9200/_cluster/settings -H 'Content-type: application/json' --data-binary $'{"transient":{"cluster.max_shards_per_node":2500}}'
```
This will make sure if you run the benchmark, that it can maintain enough active indices for 2500 articles

### 3. Run the benchmark
In the `arc-pipeline` project directory, run the following command to turn on the python environment
```
source env/bin/activate
```
Then use the following command to intiate the benchmark
```
python -m arc_benchmark -c path/to/config/file [--article_directory path/to/article/directory --question_directory path/to/question/directory]
```
This may take a while to run, as the benchmark needs to extract questions and articles from files, save them
to Elasticsearch, then run the benchmark. Each individual article processed by the benchmark takes slightly less than 20
seconds to complete (at least on mine).


### What does EXAM Do?
It operates in 3 steps.
1. Loads in articles and stores them to Elasticsearch
2. Loads in questions and stores them in JSONL files for later use
3. Runs the ARC-Solvers against a series of articles and question sets

# Testing Instructions
To see if unit tests pass and to see the coverage level, run the following commands. All tested files should be at 100%
coverage. Some additional scripts are included in the main directory though they are just scripts used to calculate
results used in the associated paper.
```
coverage run --omit=tests/**,**/__init__.py,env/** -m unittest 
coverage report
coverage html
```
The first command runs the tests, the second prints a coverage report to the terminal, and the third creates a
web-browsable version to allow a visual examination of files and their coverage.

# Common Issues
If you get a "read-only" issue from Elasticsearch, this could be due to how much free space is left on your system. If
your hard drive is 95% full, it will not let you re-index documents. Clear up some space on your hard drive and try
again.

If you are running EXAM on lots and lots of questions and systems, Elasticsearch may get overloaded. If this happens,
it can recover, however, some bogus results may be added to `checkpoints/arc_results.json`. If this happens, you'll
encounter an error attempting to generate scores. To fix this, simply delete the rows of 
`checkpoints/arc_results.json` that have empty curly braces. An example would be:

```
"bert_cknrm_50": [{"index": "bert-cknrm-50-earth-science-and-its-branches", "question_set": "L_0002", "results": {} ...
```

Deleting these rows and rerunning EXAM will allow it to fill in the missing information.

Sometimes this bogging down can be bad enough that EXAM makes very slow progress. If you see the process retrying
consistently, shut down the process and reboot your computer. The checkpoint file will maintain any progress so nothing
will be lost, and it will likely help Elasticsearch process the requests faster. There may be a way to fix this by
giving Elasticsearch more memory, but this has had limited success.


# Additional Scripts
Several scripts have been included to help calculate results, we describe them briefly here if people wish to validate
our results the way we originally calculated them.

* `calculate_correlation.py`: calculates the correlation between the different metrics used in our work. It is
    prepopulated with all the information you need but will need changed if you use different articles
* `calculate_existing_eval_average.py`: calculates the average of NDCG@20, MAP, and Precision at R for the TREC CAR
    Y3 data, unless you wish to validate the results of our tables you shouldn't need this. If you do wish to use this,
    you may need to change the directory information in the script
* `calculate_rouge.py`: calculates the ROUGE-1 precision, recall, and f1 for a set of articles versus the TQA data,
    if you wish to use this you will need to change the directory locations to the appropriate position
* `quantitative_evaluation.py`: examines overlap or distinction between two different sets of articles in how they
    sucessfully or unsuccessfully answer questions.


