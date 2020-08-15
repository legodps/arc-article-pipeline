import json
import os
import re
from scipy.stats import sem


DECIMAL_DIGITS = 4
# Needs to be a directory, not a singular filepath
EVAL_DIRECTORY = '../trec_eval_data/'
FILE_EXTENSION = '.run.evalall'
MAP = 'map'
RESULTS_FILE = 'checkpoints/eval_run_metrics.json'
RPREC = 'Rprec'
NDCG = 'ndcg_cut_20'


def load_eval_results():
    print('Loading in *.run.evalall files')
    eval_files = [file for file in os.listdir(EVAL_DIRECTORY) if os.path.isfile(os.path.join(EVAL_DIRECTORY, file))]
    individual_eval_files = [file for file in eval_files if FILE_EXTENSION in file]
    all_file_results = {}
    for file in individual_eval_files:
        individual_file_results = {
            MAP: [],
            RPREC: [],
            NDCG: []
        }
        with open(f'{EVAL_DIRECTORY}{file}', 'r') as eval_file:
            line = eval_file.readline()
            while line:
                cleaned_line = re.sub(r"\s+", '#', line).split('#')
                metric = cleaned_line[0]
                #article_id = cleaned_line[1].split(':')[1].split('/')[0]
                value = float(cleaned_line[2])
                if MAP in metric:
                    individual_file_results[MAP].append(value)
                elif RPREC in metric:
                    individual_file_results[RPREC].append(value)
                elif NDCG in metric:
                    individual_file_results[NDCG].append(value)

                line = eval_file.readline()

        all_file_results[file] = individual_file_results
    return all_file_results


def calculate_averages(file_results):
    print(f'Calculating averages and standard deviations for {len(file_results.keys())} files')
    aggregated_results = {}
    for file_name in file_results.keys():
        aggregated_results[file_name] = {
            'average_map': round(sum(file_results[file_name][MAP]) / len(file_results[file_name][MAP]), DECIMAL_DIGITS),
            'map_std_dev': round(sem(file_results[file_name][MAP]), DECIMAL_DIGITS),
            'average_rprec': round(
                sum(file_results[file_name][RPREC]) / len(file_results[file_name][RPREC]),
                DECIMAL_DIGITS
            ),
            'rprec_std_dev': round(sem(file_results[file_name][RPREC]), DECIMAL_DIGITS),
            'average_ndcg': round(
                sum(file_results[file_name][NDCG]) / len(file_results[file_name][NDCG]),
                DECIMAL_DIGITS
            ),
            'ndcg_std_dev': round(sem(file_results[file_name][NDCG]), DECIMAL_DIGITS)
        }

    return aggregated_results


def calculate_averages_and_std_dev():
    individual_run_results = load_eval_results()
    aggregated_results = calculate_averages(individual_run_results)

    json_file = open(f'{RESULTS_FILE}', 'w')
    json.dump(aggregated_results, json_file)
    json_file.close()


calculate_averages_and_std_dev()
