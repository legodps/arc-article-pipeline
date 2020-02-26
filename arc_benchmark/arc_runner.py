import os
import shutil
import subprocess
from arc_benchmark.constants import ARC_CHALLENGE_TEST, ARC_DATA_FULL_WIPE_KEEP_FILES, ARC_DATA_SMALL_WIPE_KEEP_FILES, \
    ARC_DATA_SUBDIRECTORY, ARC_MODEL_SUBDIRECTORY, CONDA_ENVIRONMENT_NAME, EVALUATE_SOLVER_FILEPATH, METRICS


def full_reset(arc_solver_directory, config):
    """

    """
    for filename in sorted(os.listdir(f'{arc_solver_directory}/{config[ARC_DATA_SUBDIRECTORY]}')):
        if filename not in ARC_DATA_FULL_WIPE_KEEP_FILES:
            os.remove(f'{arc_solver_directory}/{config[ARC_DATA_SUBDIRECTORY]}/{filename}')
    print('Wipe complete')


def copy_test_set(arc_solver_directory, question_set_filepath, config):
    """

    """
    shutil.copyfile(
        question_set_filepath,
        f'{arc_solver_directory}/{config[ARC_DATA_SUBDIRECTORY]}/{ARC_CHALLENGE_TEST}'
    )


def run_arc_on_index(arc_solver_directory, index, config):
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
                'correct': int(output[line_index + 4].split(':')[1].strip()),
                'incorrect': int(output[line_index + 5].split(':')[1].strip())
                + int(output[line_index + 6].split(':')[1].strip())
            }


def evaluate_articles(index_files, question_set_indices, benchmark_set_filepaths, arc_solver_directory, config):
    """

    """
    benchmark_results = {}
    print(question_set_indices)
    print('##########################')
    print(benchmark_set_filepaths)

    benchmark_dir = os.getcwd()
    os.chdir(arc_solver_directory)
    full_reset(arc_solver_directory, config)
    copy_test_set(arc_solver_directory, f'{benchmark_dir}/question-sets/test-challenge-set.jsonl', config)
    results = run_arc_on_index(arc_solver_directory, 'test-index', config)
    #for question_set_id in question_set_indices.keys():

        #copy_test_set(benchmark_set_filepaths[question_set_id], config)

        #for index in question_set_indices[question_set_id]:
            #run_arc_on_index(index, config)
