import os
import shutil
from arc_benchmark.load_files import read_json_questions
from arc_benchmark.constants import ANSWER_KEY, ARC_CHALLENGE_TEST, BENCHMARK_SET_DIRECTORY, CHOICES, ID, LABEL, \
    QUESTION, STEM, TEXT


def create_or_clean_directory(config):
    """ Deletes the benchmark_set_directory if it exists, clearing any previous files out, then recreates the directory

        Args:
            config (dict): config file specified properties to use in running the benchmark
    """
    if os.path.isdir(config[BENCHMARK_SET_DIRECTORY]):
        shutil.rmtree(config[BENCHMARK_SET_DIRECTORY])

    os.mkdir(config[BENCHMARK_SET_DIRECTORY])


def store_question_sets(question_sets, question_set_ids, config):
    """ Stores the sets of questions into different files, named based on the question set ID. Not all question sets
        should be saved into files as only a subset will have associated articles to be evaluated on.

        Args:
            question_sets (dict): all questions grouped into different sets based on ID
            question_set_ids (list): the list of question ids the articles should be benchmarked on
            config (dict): config file specified properties to use in running the benchmark

        Returns:
            list: all filepaths of the question set files
    """
    question_set_filepaths = {}
    for question_set_key in question_sets.keys():
        if question_set_key not in question_set_ids:
            continue

        filename = f'{question_set_key}-{ARC_CHALLENGE_TEST}'
        question_set = question_sets[question_set_key]
        jsonl_questions = []

        for question in question_set:
            jsonl_string = '{"' + ID + '": "' + str(question[ID]) + '", "' + QUESTION + '": {"' + STEM + '": "' \
                           + question[QUESTION][STEM] + '", "' + CHOICES + '": ['
            for choice_index in range(len(question[QUESTION][CHOICES])):
                if choice_index > 0:
                    jsonl_string += ', '
                jsonl_string += '{"' + TEXT + '": "' + question[QUESTION][CHOICES][choice_index][TEXT] \
                    + '", "' + LABEL + '": "' + question[QUESTION][CHOICES][choice_index][LABEL] + '"}'
            jsonl_string += ']}, "' + ANSWER_KEY + '": "' + question[ANSWER_KEY] + '"}'
            jsonl_questions.append(jsonl_string)

        with open(f'{config[BENCHMARK_SET_DIRECTORY]}/{filename}', 'w') as jsonl_file:
            for question in jsonl_questions:
                jsonl_file.write(f'{question}\n')

        question_set_filepaths[question_set_key] = f'{config[BENCHMARK_SET_DIRECTORY]}/{filename}'

    return question_set_filepaths


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
    return store_question_sets(question_sets, question_set_ids, config)
