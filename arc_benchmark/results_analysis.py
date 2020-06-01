from math import floor, ceil
from arc_benchmark.constants import ARTICLE_COUNT, AVERAGE_CORRECT, AVERAGE_INCORRECT, AVERAGE_PERCENT_CORRECT, \
    AVERAGE_PERCENT_INCORRECT, AVERAGE_PERCENT_UNANSWERED, AVERAGE_UNANSWERED, CHECKPOINT_DIRECTORY, CORRECT, \
    CORRECT_STANDARD_DEVIATION, DECIMAL_DIGITS, DISAGREEMENT, FINAL_RESULTS_FILE, INCORRECT, \
    INCORRECT_STANDARD_DEVIATION, INDIVIDUAL_QUESTION_METRICS_FILE, INDIVIDUAL_RESULTS, PERCENT_CORRECT, \
    PERCENT_INCORRECT, PERCENT_UNANSWERED, RANDOM_ANSWERING, RESULTS, QUESTION_COUNT, QUESTION_ID, QUESTION_SET, \
    QUESTION_SET_METRICS_FILE, TOTAL_CORRECT, TOTAL_INCORRECT, TOTAL_UNANSWERED, UNANSWERED, \
    UNANSWERD_STANDARD_DEVIATION
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
            benchmark_results (dict): the results obtained from running the ARC Solver repeatedly
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


def calculate_results_standard_deviation(question_set_results, question_set_metrics):
    """ Calculates the standard deviation of the number of correct, incorrect, and unanswered questions by articles
        across a question set

        Args:
            question_set_results (list): the raw performance of articles across question sets
            question_set_metrics (dict): the partially analyzed results from the article performance on a question set

        Returns:
            dict: the partially analyzed results with the additional standard deviation metrics
    """
    correct_mean_diff_total = 0
    incorrect_mean_diff_total = 0
    unanswered_mean_diff_total = 0
    for results in question_set_results:
        correct_mean_diff_total += (results[RESULTS][CORRECT] - question_set_metrics[AVERAGE_CORRECT]) ** 2
        incorrect_mean_diff_total += (results[RESULTS][INCORRECT] - question_set_metrics[AVERAGE_INCORRECT]) ** 2
        unanswered_mean_diff_total += (results[RESULTS][UNANSWERED] - question_set_metrics[AVERAGE_UNANSWERED]) ** 2

    return {
        CORRECT_STANDARD_DEVIATION: round(
            (correct_mean_diff_total / question_set_metrics[ARTICLE_COUNT]) ** 0.5,
            DECIMAL_DIGITS
        ),
        INCORRECT_STANDARD_DEVIATION: round(
            (incorrect_mean_diff_total / question_set_metrics[ARTICLE_COUNT]) ** 0.5,
            DECIMAL_DIGITS
        ),
        UNANSWERD_STANDARD_DEVIATION: round(
            (unanswered_mean_diff_total / question_set_metrics[ARTICLE_COUNT]) ** 0.5,
            DECIMAL_DIGITS
        )
    }


def calculate_question_set_metrics(question_set_results):
    """ Calculates the metrics across sets of questions

        Args:
            question_set_results (dict): the raw performance of articles by each question set

        Returns:
            dict: the fully analyzed results of article performance on a question set
    """
    question_set_metrics = {}
    for question_set_id in question_set_results.keys():
        count = 0
        correct = 0
        incorrect = 0
        unanswered = 0
        print(question_set_results[question_set_id])
        for results in question_set_results[question_set_id]:
            count += 1
            correct += results[RESULTS][CORRECT]
            incorrect += results[RESULTS][INCORRECT]
            unanswered += results[RESULTS][UNANSWERED]

        question_set_metrics[question_set_id] = {
            ARTICLE_COUNT: count,
            QUESTION_COUNT: int((correct + incorrect + unanswered) / count),
            TOTAL_CORRECT: correct,
            AVERAGE_CORRECT: round(correct / count, DECIMAL_DIGITS),
            TOTAL_INCORRECT: incorrect,
            AVERAGE_INCORRECT: round(incorrect / count, DECIMAL_DIGITS),
            TOTAL_UNANSWERED: unanswered,
            AVERAGE_UNANSWERED: round(unanswered / count, DECIMAL_DIGITS)
        }

        question_set_metrics[question_set_id] = {
            **question_set_metrics[question_set_id],
            AVERAGE_PERCENT_CORRECT: round(
                question_set_metrics[question_set_id][AVERAGE_CORRECT]
                    / question_set_metrics[question_set_id][QUESTION_COUNT],
                DECIMAL_DIGITS
            ),
            AVERAGE_PERCENT_INCORRECT: round(
                question_set_metrics[question_set_id][AVERAGE_INCORRECT]
                    / question_set_metrics[question_set_id][QUESTION_COUNT],
                DECIMAL_DIGITS
            ),
            AVERAGE_PERCENT_UNANSWERED: round(
                question_set_metrics[question_set_id][AVERAGE_UNANSWERED]
                    / question_set_metrics[question_set_id][QUESTION_COUNT],
                DECIMAL_DIGITS
            )
        }

        question_set_metrics[question_set_id] = {
            **question_set_metrics[question_set_id],
            **calculate_results_standard_deviation(
                question_set_results[question_set_id],
                question_set_metrics[question_set_id]
            )
        }
    return question_set_metrics


def calculate_disagreement(individual_question_result):
    """ Calculates how many articles disagreed from the majority/plurality opinion on an individual question

        Args:
            individual_question_result (dict): the raw performance of the articles on an individual question

        Returns:
            float: the percent of answers that differed from the majority/plurality
    """
    answer_percents = [
        individual_question_result[CORRECT] / individual_question_result[ARTICLE_COUNT],
        individual_question_result[INCORRECT] / individual_question_result[ARTICLE_COUNT],
        individual_question_result[UNANSWERED] / individual_question_result[ARTICLE_COUNT]
    ]
    answer_percents.sort()
    return round(answer_percents[0] + answer_percents[1], DECIMAL_DIGITS)


def calculate_individual_question_metrics(individual_question_results):
    """ Calculates metrics specific to individual questions

        Args:
            individual_question_results (dict): the raw performance of articles on an individual question

        Returns:
            dict: the fully analyzed results of each individual question
    """
    individual_question_metrics = {}
    for question_set_and_id in individual_question_results.keys():
        article_count = individual_question_results[question_set_and_id][ARTICLE_COUNT]
        individual_question_metrics[question_set_and_id] = {
            **individual_question_results[question_set_and_id],
            PERCENT_CORRECT: round(
                individual_question_results[question_set_and_id][CORRECT] / article_count,
                DECIMAL_DIGITS
            ),
            PERCENT_INCORRECT: round(
                individual_question_results[question_set_and_id][INCORRECT] / article_count,
                DECIMAL_DIGITS
            ),
            PERCENT_UNANSWERED: round(
                individual_question_results[question_set_and_id][UNANSWERED] / article_count,
                DECIMAL_DIGITS
            ),
            DISAGREEMENT: calculate_disagreement(individual_question_results[question_set_and_id])
        }

    return individual_question_metrics


def analyze_questions(benchmark_results, config):
    """ Orchestrates the calculation of the metrics about question sets and individual questions

        Args:
            benchmark_results (dict): the results obtained from running the ARC Solver repeatedly
            config (dict): config file specified properties to use in running the benchmark
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
                        ARTICLE_COUNT: 0
                    }
                individual_question_results[f'{index_results[QUESTION_SET]}:{question_id}'] \
                    [index_results[INDIVIDUAL_RESULTS][question_id]] += 1
                individual_question_results[f'{index_results[QUESTION_SET]}:{question_id}'][ARTICLE_COUNT] += 1

    question_set_metrics = calculate_question_set_metrics(question_set_results)
    individual_question_metrics = calculate_individual_question_metrics(individual_question_results)
    store_json(question_set_metrics, config[QUESTION_SET_METRICS_FILE], config)
    store_json(individual_question_metrics, config[INDIVIDUAL_QUESTION_METRICS_FILE], config)
