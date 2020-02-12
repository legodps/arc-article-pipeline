# Article Archiver

# Setup Instructions

### 1. Install python 3
Download and install python 3 from the [Python Website](https://www.python.org/downloads/)

### 2. Create Virtual env (optional)
Virtual environments are not required but are recommended, as they allow you to have versions of packages installed
according to the needs of a project rather than the highest/lowest common denominator. Instructions paraphrased from
here: [Virtual Env Docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/). My instructions
are for linux, though the docs explain for windows as well.

#### Install Virtual Env
Run this command to install virtualenv.
`python3 -m pip install --user virtualenv`
You may encounter a permissions issue, however, sudo'ing this command should fix that 

#### Create Virtual Env
Run this command to create the Virtual Env
`python3 -m venv env`
This will create a folder within the downloaded project called `env` where the virtual environment information will be stored

#### Turning on the Virtual Env
Run this command to turn the Virtual Environment on
`source env/bin/activate/`

### 3. Install Dependencies
Run this command to have pip install dependencies (or upgrade them) based on the included requirements list
`pip3 install --upgrade -r requirements.txt`

# Configuring the Project
In addition to command line arguments, you can configure the archiver via a yaml file with the following properties
* `host`: the hostname of the Elasticsearch database, default is `localhost`, required
* `port`: the port of the Elasticsearch database, default is `9200`, required
* `data_directory`: the filepath of a particular jsonl file or path to a directory of jsonl files. The archiver system
    prioritizes terminal specification of the data filepath via the `-f` or `--filepath` options over the config file.
    This is provided for convenience for repeated runs of the Archiver
* `mapping`: the Elasticsearch index map. This is used to configure the indices of the articles for the best retrieval.
    Its default should be sufficient. Feel free to experiment if you wish.
A default config file is provided [archiverConfig.yaml](benchmarkConfig.yaml)

# Running the Project
Use the following command to run the article archiver
`python -m archiver -f path/to/data/file(s) -c path/to/config/file`
the `-f` option can be specified in the configuration file as mentioned above
the `-c` option is not required as long as you are using the base config file

The archiver is idempotent so it should matter if you rerun it unless you change what articles are being loaded etc.

# Testing Instructions
To see if unit tests pass and the coverage level run the following commands
```
coverage run --omit=tests/**,**/__init__.py,env/** -m unittest
coverage report
coverage html
```
The first command runs the tests, the second prints a coverage report to the terminal, and the third creates a web-browsable
version to allow you to look visually where coverage is missing and explore the files

# Common Issues
If you get a "read-only" issue from Elasticsearch, this could be due to how much free space is left on your system. If
your hard drive is 95% full, it will not let you re index documents. Clear up some space on your hard drive and try
again.