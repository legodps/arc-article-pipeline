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
ToDo

# Running the Project
Not Complete

Use the following command to run the pipeline
`python -m pipeline -c path/to/config/file`

# Testing Instructions
To see if unit tests pass and the coverage level run the following commands
```
coverage run --omit=tests/**,**/__init__.py,env/** -m unittest
coverage report
coverage html
```
The first command runs the tests, the second prints a coverage report to the terminal, and the third creates a web-browsable
version to allow you to look visually where coverage is missing and explore the files