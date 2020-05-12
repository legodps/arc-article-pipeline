import json
import os
import shutil
import subprocess
from arc_benchmark.file_utils import create_or_load_arc_checkpoint
from arc_benchmark.constants import ARC_CHALLENGE_TEST, ARC_CORPUS_INDEX, ARC_DATA_FULL_WIPE_KEEP_FILES, \
    ARC_DATA_SMALL_WIPE_KEEP_FILES, ARC_DATA_SUBDIRECTORY, ARC_MODEL_SUBDIRECTORY, CONDA_ENVIRONMENT_NAME, CORRECT, \
    EVALUATE_SOLVER_FILEPATH, INCORRECT, INDEX, METRICS, QUESTION_SET, RESULTS, UNANSWERED


def clean_checkpoints(arc_solver_directory, config, full_reset=False):
    """ Cleans out files from the data directory, including the test set if it is a full reset

        Args:
            arc_solver_directory (str): the directory to the ARC-Solver project
            config (dict): config file specified properties to use in running the benchmark
            full_reset (bool): optional, whether or not the test set should be cleaned out with the other surplus files
    """
    for filename in sorted(os.listdir(f'{arc_solver_directory}/{config[ARC_DATA_SUBDIRECTORY]}')):
        if full_reset and filename not in ARC_DATA_FULL_WIPE_KEEP_FILES:
            os.remove(f'{arc_solver_directory}/{config[ARC_DATA_SUBDIRECTORY]}/{filename}')
        elif filename not in ARC_DATA_SMALL_WIPE_KEEP_FILES:
            os.remove(f'{arc_solver_directory}/{config[ARC_DATA_SUBDIRECTORY]}/{filename}')

    if full_reset:
        print('Full clean complete')


def copy_test_set(arc_solver_directory, question_set_filepath, config):
    """ Copies a test set from the benchmark project to the ARC-Solver project

        Args:
            arc_solver_directory (str): the directory to the ARC-Solver project
            question_set_filepath (str): the directory to the test sets in the benchmark project
            config (dict): config file specified properties to use in running the benchmark
    """
    shutil.copyfile(
        question_set_filepath,
        f'{arc_solver_directory}/{config[ARC_DATA_SUBDIRECTORY]}/{ARC_CHALLENGE_TEST}'
    )


def run_arc_on_index(index, config):
    """ Runs the ARC-Solver on a questions set with a particular index

        Args:
            index (str): the Elasticsearch index that has an article designed for the question set
            config (dict): config file specified properties to use in running the benchmark

        Returns:
            dict: a python object containing the number of correct, incorrect, and unanswered questions the ARC-Solver
                run produced for a given set of questions and article
    """
    run_results = subprocess.run(
        [
            'conda',
            'run',
            '-n',
            f'{config[CONDA_ENVIRONMENT_NAME]}',
            'sh',
            f'{EVALUATE_SOLVER_FILEPATH}',
            f'{config[ARC_DATA_SUBDIRECTORY]}/{ARC_CHALLENGE_TEST}',
            f'{config[ARC_MODEL_SUBDIRECTORY]}',
            f'{index}'
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    output = run_results.stdout.split('\n')
    results = {}
    for line_index in range(len(output)):
        if METRICS in output[line_index]:
            results = {
                CORRECT: int(output[line_index + 4].split(':')[1].strip()),
                INCORRECT: int(output[line_index + 5].split(':')[1].strip()),
                UNANSWERED: int(output[line_index + 6].split(':')[1].strip())
            }
    if len(results.keys()) == 0:
        print('************')
        print(run_results.stdout)
        print('************')
        print(run_results.stderr)
        print('************')
    return results


def evaluate_articles(index_files, question_set_indices, benchmark_set_filepaths, arc_solver_directory, config):
    """ Orchestrates the running of the ARC-Solver and organizes the results, along with keeping checkpoints

        Args:
            index_files (dict): a dictionary used to connect index names to their source article file
            question_set_indices (dict): a dictionary used to connect question sets to indices
            benchmark_set_filepaths (dict): a dictionary used to connect question sets to particular files
            arc_solver_directory (str): the directory of the ARC-Solver project
            config (dict): config file specified properties to use in running the benchmark

        Returns:
            dict: a dictionary containing the results for each index run on its associated question set
    """
    benchmark_results = {}
    print('##########################')
    checkpoint_file, completed_entries = create_or_load_arc_checkpoint(config)
    benchmark_dir = os.getcwd()
    os.chdir(arc_solver_directory)
    for question_set_id in question_set_indices.keys():
        clean_checkpoints(arc_solver_directory, config, full_reset=True)
        if question_set_id not in benchmark_set_filepaths \
                or not os.path.isfile(f'{benchmark_dir}{benchmark_set_filepaths[question_set_id]}'):
            print(f'no question set found for {question_set_id}')
            continue
        copy_test_set(arc_solver_directory, f'{benchmark_dir}{benchmark_set_filepaths[question_set_id]}', config)
        for index in question_set_indices[question_set_id]:
            if not index_files[index] in benchmark_results:
                benchmark_results[index_files[index]] = []

            if (index, question_set_id) in completed_entries.keys():
                benchmark_results[index_files[index]].append(completed_entries[(index, question_set_id)])
            else:
                print(f'question_set_id: {question_set_id} index: {index}')
                results = run_arc_on_index(index, config)
                results_entry = {INDEX: index, QUESTION_SET: question_set_id, RESULTS: results}
                checkpoint_file.write(json.dumps(results_entry) + '\n')

                benchmark_results[index_files[index]].append({QUESTION_SET: question_set_id, RESULTS: results})
                clean_checkpoints(arc_solver_directory, config)

    checkpoint_file.close()
    os.chdir(benchmark_dir)
    return benchmark_results


def evaluate_arc_index(benchmark_results, question_set_indices, benchmark_set_filepaths, arc_solver_directory, config):
    """

    """
    checkpoint_file, completed_entries = create_or_load_arc_checkpoint(config)
    benchmark_dir = os.getcwd()
    os.chdir(arc_solver_directory)
    benchmark_results[config[ARC_CORPUS_INDEX]] = []
    for question_set_id in question_set_indices.keys():
        clean_checkpoints(arc_solver_directory, config, full_reset=True)
        if question_set_id not in benchmark_set_filepaths \
                or not os.path.isfile(f'{benchmark_dir}{benchmark_set_filepaths[question_set_id]}'):
            print(f'no question set found for {question_set_id}')
            continue
        copy_test_set(arc_solver_directory, f'{benchmark_dir}{benchmark_set_filepaths[question_set_id]}', config)
        if (config[ARC_CORPUS_INDEX], question_set_id) in completed_entries.keys():
            benchmark_results[config[ARC_CORPUS_INDEX]].append(
                completed_entries[config[ARC_CORPUS_INDEX], question_set_id]
            )
        else:
            results = run_arc_on_index(config[ARC_CORPUS_INDEX], config)
            results_entry = {INDEX: config[ARC_CORPUS_INDEX], QUESTION_SET: question_set_id, RESULTS: results}
            checkpoint_file.write(json.dumps(results_entry) + '\n')
            benchmark_results[config[ARC_CORPUS_INDEX]].append({QUESTION_SET: question_set_id, RESULTS: results})
            clean_checkpoints(arc_solver_directory, config)

    checkpoint_file.close()
    os.chdir(benchmark_dir)
    return benchmark_results
