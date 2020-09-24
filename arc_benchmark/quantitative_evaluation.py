import json
import sys


RUNS_TO_COMPARE = ['tqa', 'rerank2-bert']
CHECKPOINT_FILE = 'checkpoints/arc_runner_checkpoints.jsonl'

BOTH_CORRECT = 'both_correct'
BOTH_INCORRECT = 'both_incorrect'
BOTH_UNANSWERED = 'both_unanswered'
CORRECT = 'correct'
INCORRECT = 'incorrect'
INDEX = 'index'
INDIVIDUAL_RESULTS = 'individual_results'
RESULTS = 'results'
UNANSWERED = 'unanswered'
QUESTION_SET = 'question_set'


def load_and_filter_checkpoints():
    """ Loads the checkpoint results from the EXAM checkpoint file and imports the relevant runs

        Returns:
            dict: the results of each run of the Decompatt model for each algorithm run
    """
    filtered_results = {}
    count = 0
    for run in RUNS_TO_COMPARE:
        filtered_results[run] = {}
    with open(CHECKPOINT_FILE, 'r') as checkpoint_file:
        line = checkpoint_file.readline()
        while line:
            json_line = json.loads(line)
            for run in RUNS_TO_COMPARE:
                if json_line[INDEX][:len(run)] == run:
                    count += 1
                    cleaned_article_name = json_line[INDEX][len(run):].replace('-', '')
                    question_id = json_line[QUESTION_SET]
                    filtered_results[run][f'{cleaned_article_name}-{question_id}'] = json_line
            line = checkpoint_file.readline()
    return filtered_results


def calculate_confusion(results):
    """ Calculates a semi-confusion matrix based on the Correct, Incorrect, or Unanswered questions of each
        algorithm run

        Args:
            results (dict): the loaded results for each algorithm run for each question set

        Returns:
            dict: the confusion matrix for the compared Correct, Incorrect, and Unanswered questions
    """
    bulk_results = {
        RUNS_TO_COMPARE[0]: {
            CORRECT: 0,
            INCORRECT: 0,
            UNANSWERED: 0
        },
        RUNS_TO_COMPARE[1]: {
            CORRECT: 0,
            INCORRECT: 0,
            UNANSWERED: 0
        }
    }
    # assumes both have same articles
    articles = list(results[RUNS_TO_COMPARE[1]].keys())

    run_results_by_question = {}

    for article in articles:
        for question_id in list(results[RUNS_TO_COMPARE[0]][article][INDIVIDUAL_RESULTS].keys()):
            run_results_by_question[(article, question_id)] = {}
            for run in RUNS_TO_COMPARE:
                run_results_by_question[(article, question_id)][run] = \
                    results[run][article][INDIVIDUAL_RESULTS][question_id]
        for run in RUNS_TO_COMPARE:
            bulk_results[run][CORRECT] += results[run][article][RESULTS][CORRECT]
            bulk_results[run][INCORRECT] += results[run][article][RESULTS][INCORRECT]
            bulk_results[run][UNANSWERED] += results[run][article][RESULTS][UNANSWERED]

    confusion_matrix = {
        f'{RUNS_TO_COMPARE[0]}_{CORRECT}_{RUNS_TO_COMPARE[1]}_{CORRECT}': 0,
        f'{RUNS_TO_COMPARE[0]}_{CORRECT}_{RUNS_TO_COMPARE[1]}_{INCORRECT}': 0,
        f'{RUNS_TO_COMPARE[0]}_{CORRECT}_{RUNS_TO_COMPARE[1]}_{UNANSWERED}': 0,
        f'{RUNS_TO_COMPARE[0]}_{INCORRECT}_{RUNS_TO_COMPARE[1]}_{CORRECT}': 0,
        f'{RUNS_TO_COMPARE[0]}_{INCORRECT}_{RUNS_TO_COMPARE[1]}_{INCORRECT}': 0,
        f'{RUNS_TO_COMPARE[0]}_{INCORRECT}_{RUNS_TO_COMPARE[1]}_{UNANSWERED}': 0,
        f'{RUNS_TO_COMPARE[0]}_{UNANSWERED}_{RUNS_TO_COMPARE[1]}_{CORRECT }': 0,
        f'{RUNS_TO_COMPARE[0]}_{UNANSWERED}_{RUNS_TO_COMPARE[1]}_{INCORRECT}': 0,
        f'{RUNS_TO_COMPARE[0]}_{UNANSWERED}_{RUNS_TO_COMPARE[1]}_{UNANSWERED}': 0
    }
    print(bulk_results)

    for article_question_tuple in run_results_by_question.keys():
        run_1_results = run_results_by_question[article_question_tuple][RUNS_TO_COMPARE[0]]
        run_2_results = run_results_by_question[article_question_tuple][RUNS_TO_COMPARE[1]]
        confusion_matrix[f'{RUNS_TO_COMPARE[0]}_{run_1_results}_{RUNS_TO_COMPARE[1]}_{run_2_results}'] += 1
    return confusion_matrix


def calculate_gold_versus_best_overlap():
    """ Orchestrates the calculation of the confusion matrix between two algorithm runs and prints the results to
        the console
    """
    if len(RUNS_TO_COMPARE) > 2:
        print('ERROR: should only be run on 2 systems')
        sys.exit(1)
    results = load_and_filter_checkpoints()
    confusion_results = calculate_confusion(results)
    print(confusion_results)
    # store confusion


calculate_gold_versus_best_overlap()