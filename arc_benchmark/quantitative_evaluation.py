import json
import sys


RUNS_TO_COMPARE = ['tqa', 'dangnt-nlp']
CHECKPOINT_FILE = 'checkpoints/arc_runner_checkpoints.jsonl'

BOTH_CORRECT = 'both_correct'
BOTH_INCORRECT = 'both_incorrect'
BOTH_UNANSWERED = 'both_unanswered'
CORRECT = 'correct'
INCORRECT = 'incorrect'
INDEX = 'index'
INDIVIDUAL_RESULTS = 'individual_results'
UNANSWERED = 'unanswered'


def load_and_filter_checkpoints():
    filtered_results = {}
    for run in RUNS_TO_COMPARE:
        filtered_results[run] = {}
    with open(CHECKPOINT_FILE, 'r') as checkpoint_file:
        line = checkpoint_file.readline()
        json_line = json.loads(line)
        while line:
            json_line = json.loads(line)
            for run in RUNS_TO_COMPARE:
                if json_line[INDEX][:len(run)] == run:
                    cleaned_article_name = json_line[INDEX][len(run):].replace('-', '')
                    filtered_results[run][cleaned_article_name] = json_line
            line = checkpoint_file.readline()
    return filtered_results


def calculate_confusion(results):
    """

    """
    # assumes both have same articles
    articles = list(results[RUNS_TO_COMPARE[0]].keys())

    run_results_by_question = {}

    #print(results[RUNS_TO_COMPARE[1]]['-the-sun-and-the-earth-moon-system'])

    for article in articles:
        for question_id in list(results[RUNS_TO_COMPARE[0]][article][INDIVIDUAL_RESULTS].keys()):
            run_results_by_question[(article, question_id)] = {}
            for run in RUNS_TO_COMPARE:
                #print(results[run])
                run_results_by_question[(article, question_id)][run] = \
                    results[run][article][INDIVIDUAL_RESULTS][question_id]

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

    for article_question_tuple in run_results_by_question.keys():
        run_1_results = run_results_by_question[article_question_tuple][RUNS_TO_COMPARE[0]]
        run_2_results = run_results_by_question[article_question_tuple][RUNS_TO_COMPARE[1]]
        confusion_matrix[f'{RUNS_TO_COMPARE[0]}_{run_1_results}_{RUNS_TO_COMPARE[1]}_{run_2_results}'] += 1
    return confusion_matrix


def calculate_gold_versus_best_overlap():
    """

    """
    if len(RUNS_TO_COMPARE) > 2:
        print('ERROR: should only be run on 2 systems')
        sys.exit(1)
    results = load_and_filter_checkpoints()
    confusion_results = calculate_confusion(results)
    print(confusion_results)
    # store confusion


calculate_gold_versus_best_overlap()