import os
import shutil
from arc_benchmark.load_files import read_json_questions
from arc_benchmark.store_files import store_question_sets


def create_or_clean_directory(config):
    """ Deletes the test_set_directory if it exists, clearing any previous files out, then recreates the directory

        Args:
            config (dict): config file specified properties to use in running the benchmark
    """
    if os.path.isdir(config['test_set_directory']):
        shutil.rmtree(config['test_set_directory'])

    os.mkdir(config['test_set_directory'])


def create_test_sets(question_directory, question_set_ids, config):
    """ Orchestrates the loading of questions from one or more JSON files and then the storage of sets of questions
        into JSONL test sets for use in the ARC QA system

        Args:
            question_directory (str): the filepath to a singular, or directory of, JSON question files
            question_set_ids (keysview): a list of ids that correspond to sets of questions that should be saved,
                all other sets of questions should be ignored as they won't be used in the benchmark
            config (dict): config file specified properties to use in running the benchmark

        Returns:
            list: the filepaths of the saved question sets
    """
    create_or_clean_directory(config)

    question_sets = read_json_questions(question_directory)
    return store_question_sets(question_sets, question_set_ids)
