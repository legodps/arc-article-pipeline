from math import floor, ceil
from arc_benchmark.constants import AVERAGE_CORRECT, AVERAGE_INCORRECT, AVERAGE_UNANSWERED, CHECKPOINT_DIRECTORY, \
    CORRECT, CORRECT_STANDARD_DEVIATION, FINAL_RESULTS_FILE, INCORRECT, INCORRECT_STANDARD_DEVIATION, INDEX_COUNT, \
    INDIVIDUAL_QUESTION_RESULTS_FILE, INDIVIDUAL_RESULTS, RANDOM_ANSWERING, RESULTS, QUESTION_COUNT, QUESTION_ID, \
    QUESTION_SET, TOTAL, UNANSWERED, UNANSWERD_STANDARD_DEVIATION
from arc_benchmark.file_utils import store_json


def calculate_baselines(question_answer_counts):
    """ Calculates the baseline of random answers (rounded such that >= .5 yields correct and < .5 is incorrect)

        Args:
            question_answer_counts (dict): the count of questions by the number of possible answers

        Returns:
            dict: the results of the random answer baseline
    """
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

    file_results = {RANDOM_ANSWERING: baseline_results}
    count = 1
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
        count += 1

    print('##############')
    store_json(file_results, config[FINAL_RESULTS_FILE], config)
    print(f'Results tallied in {config[CHECKPOINT_DIRECTORY]}/{config[FINAL_RESULTS_FILE]}')
    print('##############')


def calculate_results_standard_deviation(question_set_results, question_totals):
    correct_mean_diff_total = 0
    incorrect_mean_diff_total = 0
    unanswered_mean_diff_total = 0
    for results in question_set_results:
        correct_mean_diff_total = (results[RESULTS][CORRECT] - question_totals[AVERAGE_CORRECT]) ** 2
        incorrect_mean_diff_total = (results[RESULTS][INCORRECT] - question_totals[AVERAGE_INCORRECT]) ** 2
        unanswered_mean_diff_total = (results[RESULTS][UNANSWERED] - question_totals[AVERAGE_UNANSWERED]) ** 2

    return {
        CORRECT_STANDARD_DEVIATION: (correct_mean_diff_total / question_totals[INDEX_COUNT]) ** 0.5,
        INCORRECT_STANDARD_DEVIATION: (incorrect_mean_diff_total / question_totals[INDEX_COUNT]) ** 0.5,
        UNANSWERD_STANDARD_DEVIATION: (unanswered_mean_diff_total / question_totals[INDEX_COUNT]) ** 0.5
    }


def analyze_questions(benchmark_results, config):
    """

    """
    question_set_results = {}
    individual_question_results = {}
    for file in benchmark_results.keys():
        for index_results in benchmark_results[file]:
            if index_results[QUESTION_SET] not in question_set_results.keys():
                question_set_results[index_results[QUESTION_SET]] = []
            question_set_results[index_results[QUESTION_SET]].append(index_results)

            for question_id in index_results[INDIVIDUAL_RESULTS].keys():
                if f'{index_results[QUESTION_SET]}:{question_id}' not in individual_question_results:
                    individual_question_results[f'{index_results[QUESTION_SET]}:{question_id}'] = {
                        QUESTION_SET: index_results[QUESTION_SET],
                        QUESTION_ID:  question_id,
                        CORRECT: 0,
                        INCORRECT: 0,
                        UNANSWERED: 0,
                        TOTAL: 0
                    }
                individual_question_results[f'{index_results[QUESTION_SET]}:{question_id}'] \
                    [index_results[INDIVIDUAL_RESULTS][question_id]] += 1
                individual_question_results[f'{index_results[QUESTION_SET]}:{question_id}'][TOTAL] += 1

    question_totals = {}
    for question_set_id in question_set_results.keys():
        count = 0
        correct = 0
        incorrect = 0
        unanswered = 0
        for results in question_set_results[question_set_id]:
            count += 1
            correct += results[RESULTS][CORRECT]
            incorrect += results[RESULTS][INCORRECT]
            unanswered += results[RESULTS][UNANSWERED]

        question_totals[question_set_id] = {
            INDEX_COUNT: count,
            QUESTION_COUNT: (correct + incorrect + unanswered) / count,
            CORRECT: correct,
            AVERAGE_CORRECT: correct/count,
            INCORRECT: incorrect,
            AVERAGE_INCORRECT: incorrect/count,
            UNANSWERED: unanswered,
            AVERAGE_UNANSWERED: unanswered/count
        }

        question_totals[question_set_id] = {
            **question_totals[question_set_id],
            'average_percent_correct': question_totals[question_set_id][AVERAGE_CORRECT]
                                        / question_totals[question_set_id][QUESTION_COUNT],
            'average_percent_incorrect': question_totals[question_set_id][AVERAGE_INCORRECT]
                                         / question_totals[question_set_id][QUESTION_COUNT],
            'average_percent_unanswered': question_totals[question_set_id][AVERAGE_UNANSWERED]
                                          / question_totals[question_set_id][QUESTION_COUNT]
        }

        question_totals[question_set_id] = {
            **question_totals[question_set_id],
            **calculate_results_standard_deviation(
                question_set_results[question_set_id],
                question_totals[question_set_id]
            )
        }

    store_json(individual_question_results, config[INDIVIDUAL_QUESTION_RESULTS_FILE], config)
    print(individual_question_results)