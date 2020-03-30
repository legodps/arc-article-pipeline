import json
import os
import shutil
import subprocess
from arc_benchmark.file_utils import create_or_load_arc_checkpoint
from arc_benchmark.constants import ARC_CHALLENGE_TEST, ARC_CHECKPOINT_FILE, ARC_DATA_FULL_WIPE_KEEP_FILES, \
    ARC_DATA_SMALL_WIPE_KEEP_FILES, ARC_DATA_SUBDIRECTORY, ARC_MODEL_SUBDIRECTORY, CONDA_ENVIRONMENT_NAME, CORRECT, \
    EVALUATE_SOLVER_FILEPATH, INCORRECT, INDEX, METRICS, QUESTION_SET, RESULTS, UNANSWERED


def clean_checkpoints(arc_solver_directory, config, full_reset=False):
    """

    """
    for filename in sorted(os.listdir(f'{arc_solver_directory}/{config[ARC_DATA_SUBDIRECTORY]}')):
        if full_reset and filename not in ARC_DATA_FULL_WIPE_KEEP_FILES:
            os.remove(f'{arc_solver_directory}/{config[ARC_DATA_SUBDIRECTORY]}/{filename}')
        elif filename not in ARC_DATA_SMALL_WIPE_KEEP_FILES:
            os.remove(f'{arc_solver_directory}/{config[ARC_DATA_SUBDIRECTORY]}/{filename}')

    if full_reset:
        print('Full clean complete')


def copy_test_set(arc_solver_directory, question_set_filepath, config):
    """

    """
    shutil.copyfile(
        question_set_filepath,
        f'{arc_solver_directory}/{config[ARC_DATA_SUBDIRECTORY]}/{ARC_CHALLENGE_TEST}'
    )


def run_arc_on_index(index, config):
    """

    """
    stdout = subprocess.run(
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
        stderr=subprocess.DEVNULL,
        universal_newlines=True
    )
    output = stdout.stdout.split('\n')
    for line_index in range(len(output)):
        if METRICS in output[line_index]:
            return {
                CORRECT: int(output[line_index + 4].split(':')[1].strip()),
                INCORRECT: int(output[line_index + 5].split(':')[1].strip()),
                UNANSWERED: int(output[line_index + 6].split(':')[1].strip())
            }


def evaluate_articles(index_files, question_set_indices, benchmark_set_filepaths, arc_solver_directory, config):
    """

    """
    benchmark_results = {}
    print('##########################')
    checkpoint_file, completed_entries = create_or_load_arc_checkpoint(config)
    benchmark_dir = os.getcwd()
    os.chdir(arc_solver_directory)
    count = 0
    for question_set_id in question_set_indices.keys():
        clean_checkpoints(arc_solver_directory, config, full_reset=True)
        copy_test_set(arc_solver_directory, f'{benchmark_dir}{benchmark_set_filepaths[question_set_id]}', config)
        for index in question_set_indices[question_set_id]:
            if count > 2:
                continue

            if not index_files[index] in benchmark_results:
                benchmark_results[index_files[index]] = []

            if index in completed_entries.keys():
                benchmark_results[index_files[index]].append(completed_entries[index])
            else:
                results = run_arc_on_index(index, config)
                results_entry = {INDEX: index, QUESTION_SET: question_set_id, RESULTS: results}
                print(results_entry)
                checkpoint_file.write(json.dumps(results_entry) + '\n')

                benchmark_results[index_files[index]].append({QUESTION_SET: question_set_id, RESULTS: results})
                clean_checkpoints(arc_solver_directory, config)
            count += 1
            print(f'###The count is {count}###')

    checkpoint_file.close()
    os.chdir(benchmark_dir)
    return benchmark_results

