# ARC Benchmark
The ARC Benchmark is a tool designed to read in articles and evaluate them on a set of questions to see how informative
or useful they are. This Benchmark tool is Designed to use questions from the 
[TQA question data set from](http://data.allenai.org/tqa/) dataset, specifically: "tqa_v1_train.json" and JSONL articles
formatted in a particular way (ToDo clarify this)

# Setup Instructions

### 1. Install python 3
Download and install python 3 from the [Python Website](https://www.python.org/downloads/)

### 2. Create Virtual env (optional)
Virtual environments are not required but are recommended, as they allow you to have versions of packages installed
according to the needs of a project rather than the highest/lowest common denominator. Instructions paraphrased from
here: [Virtual Env Docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/). 
My instructions are for linux, though the docs explain for windows as well.

#### Install Virtual Env
Run this command to install virtualenv.
`python3 -m pip install --user virtualenv`
You may encounter a permissions issue, however, sudo'ing this command should fix that 

#### Create Virtual Env
Run this command to create the Virtual Env
`python3 -m venv env`
This will create a folder within the downloaded project called `env` where the virtual environment information will be
stored

#### Turning on the Virtual Env
Run this command to turn the Virtual Environment on
`source env/bin/activate/`

### 3. Install Dependencies
Run this command to have pip install dependencies (or upgrade them) based on the included requirements list
`pip3 install --upgrade -r requirements.txt`

# Configuring the Project
In addition to terminal arguments, you can configure the benchmark via a yaml file with the following properties
* `host`: the hostname of the Elasticsearch database, default is `localhost`, required
* `port`: the port of the Elasticsearch database, default is `9200`, required
* `article_directory`: the filepath to a singular, or directory of, JSONL article files. This config setting is
    overridden if a different path is specified via the terminal. This is provided for convenience of multiple runs.
* `question_directory`: the filepath to a singular, or directory of, JSON question files. This config setting is
    overridden if a different path is specified via the termnial. This is provided for convenience of multiple runs.
* `test_set_directory`: the filepath where questions sets should be saved to. DO NOT NAME IT TO ANY EXISTING DIRECTORY,
    THE DEFAULT IS FINE. It is not recommended to change the directory location as it and all files within it will be
    deleted and recreated by running the benchmark deleted and recreated on successive runs.
* `mapping`: the Elasticsearch index map. This is used to configure the indices of the articles for the best retrieval.
    Its default should be sufficient.
    
A default config file is provided [benchmarkConfig.yaml](benchmarkConfig.yaml)

# Running the Project
Use the following command to run the benchmark
`python -m arc_benchmark -c path/to/config/file --article_directory path/to/article/directory 
--question_directory path/to/question/directory`

### What does the ARC Benchmark Do?
The benchmark operates in 3 steps.
1. Loads in articles and stores them to Elasticsearch
2. Loads in questions and stores them in JSONL files for later use
3. Runs the ARC-Solvers against a series of articles and question sets

# Testing Instructions
To see if unit tests pass and the coverage level run the following commands
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