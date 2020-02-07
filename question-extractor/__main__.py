import argparse
from file_io.load_files import load_config, read_json_questions
from file_io.store_files import store_question_sets


parser = argparse.ArgumentParser(description='Extracts files and generates jsonl test files')
parser.add_argument(
    '-f',
    '--filepath',
    default=None,
    help='a filepath to a singular article file or a directory of files of questions'
)
parser.add_argument(
    '-c',
    '--config_file',
    default='archiverConfig.yaml',
    help='A yaml config file to import settings from, defaults to archiverConfig.yaml'
)


def process_questions(filepath, config_file):
    """ This orchestrates the processing of articles, and then the insertion of the sentences into elasticsearch

        Args:
            filepath (various): the command line argument of the filepath to load articles from
            config_file (str): the command line argument of the config file to use
    """
    properties = load_config(config_file)
    directory = filepath

    # default to use the command line argument if not specified use the config file if present
    if not directory and 'question_directory' in properties.keys():
        directory = properties['question_directory']

    question_sets = read_json_questions(directory)
    store_question_sets(question_sets)


args = parser.parse_args()

process_questions(args.filepath, args.config_file)
