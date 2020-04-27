from math import floor, ceil
from arc_benchmark.constants import CHECKPOINT_DIRECTORY, CORRECT, FINAL_RESULTS_FILE, INCORRECT, RESULTS, UNANSWERED
from arc_benchmark.file_utils import store_json


def calculate_baselines(question_answer_counts):
    """ Calculates the baseline of random answers (rounded such that >= .5 yields correct and < .5 is incorrect)

        Args:
            question_answer_counts (dict): the count of questions by the number of possible answers

        Returns:
            dict: the results of the random answer baseline
    """
    print(question_answer_counts)
    baseline_results = {CORRECT: 0, INCORRECT: 0, UNANSWERED: 0}

    for answer_count in question_answer_counts.keys():
        correct = question_answer_counts[answer_count] / int(answer_count)
        incorrect = question_answer_counts[answer_count] * (int(answer_count) - 1) / int(answer_count)
        correct_decimal = correct - floor(correct)
        if correct_decimal == .5:
            baseline_results[CORRECT] += ceil(correct)
            baseline_results[INCORRECT] += floor(incorrect)
        else:
            baseline_results[CORRECT] += round(correct)
            baseline_results[INCORRECT] += round(incorrect)

    return baseline_results


def analyze_results(benchmark_results, question_answer_counts, config):
    """ Tallies the count of correct, incorrect, and unanswered questions by article file

        Args:
            benchmark_results (dict): the results obtained from running the ARC Solver repeatedly,
            question_answer_counts (dict): the count of questions by the number of possible answers
            config (dict): config file specified properties to use in running the benchmark
    """
    baseline_results = calculate_baselines(question_answer_counts)
    print(baseline_results)

    file_results = {'random_answering': baseline_results}
    for file in benchmark_results.keys():
        correct = 0
        incorrect = 0
        unanswered = 0
        for index_entry in benchmark_results[file]:
            if len(index_entry[RESULTS].keys()) > 0:
                correct += index_entry[RESULTS][CORRECT]
                incorrect += index_entry[RESULTS][INCORRECT]
                unanswered += index_entry[RESULTS][UNANSWERED]
        file_results[file] = {CORRECT: correct, INCORRECT: incorrect, UNANSWERED: unanswered}

    print('##############')
    store_json(file_results, config[FINAL_RESULTS_FILE], config)
    print(f'Results tallied in {config[CHECKPOINT_DIRECTORY]}/{config[FINAL_RESULTS_FILE]}')
    print('##############')
    print(file_results)
