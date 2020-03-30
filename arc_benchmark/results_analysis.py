from arc_benchmark.constants import CHECKPOINT_DIRECTORY, CORRECT, FINAL_RESULTS_FILE, INCORRECT, RESULTS, UNANSWERED
from arc_benchmark.file_utils import store_json


def analyze_results(benchmark_results, config):
    """ Tallies the count of correct, incorrect, and unanswered questions by article file

        Args:
            benchmark_results (obj): the results obtained from running the ARC Solver repeatedly
            config (dict): config file specified properties to use in running the benchmark
    """
    file_results = {}
    for file in benchmark_results.keys():
        correct = 0
        incorrect = 0
        unanswered = 0
        for index_entry in benchmark_results[file]:
            correct += index_entry[RESULTS][CORRECT]
            incorrect += index_entry[RESULTS][INCORRECT]
            unanswered += index_entry[RESULTS][UNANSWERED]
        file_results[file] = {CORRECT: correct, INCORRECT: incorrect, UNANSWERED: unanswered}

    print('##############')
    store_json(file_results, config[FINAL_RESULTS_FILE], config)
    print(f'Results tallied in {config[CHECKPOINT_DIRECTORY]}/{config[FINAL_RESULTS_FILE]}')
    print('##############')
    print(file_results)
