import argparse
import os
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from arc_benchmark.file_utils import load_json, store_json
from arc_benchmark.config_loader import load_config, override_config
from arc_benchmark.benchmark_set_creator import create_test_sets
from arc_benchmark.article_archiver import load_and_store_articles, load_and_store_tqa_articles
from arc_benchmark.arc_runner import evaluate_articles, evaluate_arc_index
from arc_benchmark.results_analysis import analyze_results, analyze_questions
from arc_benchmark.constants import ARC_BENCHMARK_DIRECTORY, ARC_RESULTS_FILE, ARC_SOLVER_DIRECTORY, \
    ARTICLE_DIRECTORY, BENCHMARK_CONFIG_YAML, BENCHMARK_SET_DIRECTORY, CHECKPOINT_DIRECTORY, CONFIG_FILE, \
    ENV_DIRECTORY, FINAL_RESULTS_FILE, HOST, HTMLCOV_DIRECTORY, PORT, QUESTION_DIRECTORY, TESTS_DIRECTORY

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
parser.add_argument(
    f'--{ARC_SOLVER_DIRECTORY}',
    default=None,
    help='a filepath to the top-level directory of the ARC Solver system'
)


def run_arc_benchmark(config_file, article_directory, question_directory, arc_solver_directory):
    """ Runs the ARC-Solver QA system to perform a benchmark on a set of articles with a set of questions.

        Args:
            config_file (str): the filepath to a yaml configuration file, defaults to benchmarkConfig.yaml
            article_directory (str): the filepath to a singular, or directory of, JSONL article files to run the
                benchmark on
            question_directory (str): the filepath to a singular, or directory of, JSON question files to evaluate
                the articles with
            arc_solver_directory (str): the filepath to the directory ARC-Solvers will look to, to run predictions on
    """
    config = load_config(config_file)

    article_filepath = override_config(ARTICLE_DIRECTORY, article_directory, config)
    question_filepath = override_config(QUESTION_DIRECTORY, question_directory, config)
    arc_solver_filepath = override_config(ARC_SOLVER_DIRECTORY, arc_solver_directory, config)

    if not article_filepath or not isinstance(article_filepath, str):
        print(f'ERROR: {ARTICLE_DIRECTORY} either is not a string or is not defined via terminal arguments/config file.'
              ' It is a required property to run the benchmark')
    elif not question_filepath or not isinstance(question_filepath, str):
        print(f'ERROR: {QUESTION_DIRECTORY} either is not a string or is not defined via terminal arguments/config '
              f'file. It is a required property to run the benchmark')
    elif not arc_solver_filepath or not isinstance(arc_solver_filepath, str):
        print(f'ERROR: {ARC_SOLVER_DIRECTORY} either is not a string or is not defined via terminal arguments/config '
              f'file. It is a required property to run the benchmark')
    elif BENCHMARK_SET_DIRECTORY not in config or not isinstance(config[BENCHMARK_SET_DIRECTORY], str):
        print(f'ERROR: {BENCHMARK_SET_DIRECTORY} either is not a string or is not defined via the config file. '
           f'Do not set {BENCHMARK_SET_DIRECTORY} to any critical or already used directories.')
    else:
        benchmark_results = load_json(config[ARC_RESULTS_FILE], config)

        es = Elasticsearch(hosts=[{HOST: config[HOST], PORT: config[PORT]}], retries=3, timeout=60)
        print('Connection to Elasticsearch cluster established')
        print('Storing Articles In Elasticsearch...')
        question_set_indices, index_files = load_and_store_articles(article_filepath, es, bulk, config)
        question_set_indices, tqa_index = load_and_store_tqa_articles(question_set_indices, es, bulk, config)
        print('Results Successfully stored')

        index_files = {
            **index_files,
            **tqa_index
        }
        benchmark_set_filepaths, question_answer_counts = create_test_sets(
            question_filepath,
            question_set_indices.keys(),
            config
        )
        if not benchmark_results:
            print('Evaluating Articles...')
            benchmark_results = evaluate_articles(
                index_files,
                question_set_indices,
                benchmark_set_filepaths,
                arc_solver_filepath,
                config
            )
            benchmark_results = evaluate_arc_index(
                benchmark_results,
                question_set_indices,
                benchmark_set_filepaths,
                arc_solver_filepath,
                config
            )
            print('Articles Evaluated')
            store_json(benchmark_results, config[ARC_RESULTS_FILE], config)

        if not os.path.isfile(f'{config[CHECKPOINT_DIRECTORY]}/{config[FINAL_RESULTS_FILE]}'):
            analyze_results(benchmark_results, question_answer_counts, config)
            print('analysis complete')
        print(question_answer_counts)

        analyze_questions(benchmark_results, config)


args = parser.parse_args()

run_arc_benchmark(args.config_file, args.article_directory, args.question_directory, args.arc_solver_directory)
