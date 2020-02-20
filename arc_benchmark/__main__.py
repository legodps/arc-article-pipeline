import argparse
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from arc_benchmark.config_loader import load_config, override_config
from arc_benchmark.benchmark_set_creator import create_test_sets
from arc_benchmark.article_archiver import load_and_store_articles
from arc_benchmark.constants import ARC_BENCHMARK_DIRECTORY, ARTICLE_DIRECTORY, BENCHMARK_CONFIG_YAML, \
    BENCHMARK_SET_DIRECTORY, CONFIG_FILE, ENV_DIRECTORY, HOST, HTMLCOV_DIRECTORY, PORT, QUESTION_DIRECTORY, \
    TESTS_DIRECTORY

parser = argparse.ArgumentParser(
    description='Benchmarks generated articles against question sets using the ARC QA system'
)
parser.add_argument(
    '-c',
    f'--{CONFIG_FILE}',
    default=BENCHMARK_CONFIG_YAML,
    help='A yaml config file to import settings from, defaults to benchmarkConfig.yaml'
)
parser.add_argument(
    f'--{ARTICLE_DIRECTORY}',
    default=None,
    help='a filepath to a singular article file or a directory of article files'
)
parser.add_argument(
    f'--{QUESTION_DIRECTORY}',
    default=None,
    help='a filepath to a singular question file or a directory of question files'
)


def run_arc_benchmark(config_file, article_directory, question_directory):
    """ Runs the ARC-Solver QA system to perform a benchmark on a set of articles with a set of questions.

        Args:
            config_file (str): the filepath to a yaml configuration file, defaults to benchmarkConfig.yaml
            article_directory (str): the filepath to a singular, or directory of, JSONL article files to run the
                benchmark on
            question_directory (str): the filepath to a singular, or directory of, JSON question files to evaluate
                the articles with
    """
    config = load_config(config_file)

    article_filepath = override_config(ARTICLE_DIRECTORY, article_directory, config)
    question_filepath = override_config(QUESTION_DIRECTORY, question_directory, config)

    if not article_filepath or not isinstance(article_filepath, str):
        print(f'ERROR: {ARTICLE_DIRECTORY} either is not a string or is not defined via terminal arguments/config file.'
              ' It is a required property to run the benchmark')
    elif not question_filepath or not isinstance(question_filepath, str):
        print(f'ERROR: {QUESTION_DIRECTORY} either is not a string or is not defined via terminal arguments/config '
              f'file. It is a required property to run the benchmark')
    elif BENCHMARK_SET_DIRECTORY not in config or not isinstance(config[BENCHMARK_SET_DIRECTORY], str):
        print(f'ERROR: {BENCHMARK_SET_DIRECTORY} either is not a string or is not defined via the config file. '
              'It is a required property to run the benchmark.')
    elif TESTS_DIRECTORY in config[BENCHMARK_SET_DIRECTORY] or ENV_DIRECTORY in config[BENCHMARK_SET_DIRECTORY] \
            or ARC_BENCHMARK_DIRECTORY in config[BENCHMARK_SET_DIRECTORY] \
            or HTMLCOV_DIRECTORY in config[BENCHMARK_SET_DIRECTORY]:
        print(f'Do not set {BENCHMARK_SET_DIRECTORY} to any critical or already used directories.')
    else:
        es = Elasticsearch(hosts=[{HOST: config[HOST], PORT: config[PORT]}], retries=3, timeout=60)
        print('Connection to Elasticsearch cluster established')

        question_set_indices = load_and_store_articles(article_filepath, es, bulk, config)
        question_jsonl_filepaths = create_test_sets(question_filepath, question_set_indices.keys(), config)

        # ToDo: add step 3, the running of the ARC QA system


args = parser.parse_args()

run_arc_benchmark(args.config_file, args.article_directory, args.question_directory)