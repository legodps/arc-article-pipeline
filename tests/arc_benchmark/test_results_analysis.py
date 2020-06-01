import json
import os
import shutil
from unittest import TestCase
from math import sqrt
from arc_benchmark.constants import DECIMAL_DIGITS
from arc_benchmark.results_analysis import analyze_results, calculate_baselines, calculate_results_standard_deviation, \
    calculate_disagreement, calculate_individual_question_metrics


class TestResultsAnalysis(TestCase):
    def test_calculate_baselines(self):
        test_input = {
            '2': 5,
            '4': 5
        }
        self.assertEqual(
            {'correct': 4, 'incorrect': 6, 'unanswered': 0},
            calculate_baselines(test_input),
            'it should provide a statistically random distribution of correct answers based on the number of possible'
            'answers, rounding up on 50/50 splits'
        )

    def test_analyze_results(self):
        fake_directory = '/fake_directory_dont_use'
        if os.path.isdir(f'{os.getcwd()}{fake_directory}'):
            self.assertTrue(False, f'directory of {fake_directory} is already in use, dont use it >:(')
        else:
            os.mkdir(f'{os.getcwd()}{fake_directory}')
            results_filename = 'results_file.json'
            config = {
                'checkpoint_directory': f'{os.getcwd()}{fake_directory}',
                'final_results_file': results_filename
            }
            benchmark_results = {
                'file1': [
                    {'results': {'correct': 1, 'incorrect': 2, 'unanswered': 3}},
                    {'results': {'correct': 2, 'incorrect': 3, 'unanswered': 4}},
                ],
                'file2': [
                    {'results': {'correct': 3, 'incorrect': 4, 'unanswered': 5}}
                ]
            }
            analyze_results(benchmark_results, config)
            expected_results = {
                'file1': {'correct': 3, 'incorrect': 5, 'unanswered': 7},
                'file2': {'correct': 3, 'incorrect': 4, 'unanswered': 5}
            }
            results_file = open(f'{os.getcwd()}{fake_directory}/{results_filename}', 'r')
            actual_results = json.load(results_file)
            results_file.close()
            self.assertEqual(
                expected_results,
                actual_results,
                'it should sum the correct, incorrect, and unanswered from each index and save it to a file'
            )
            shutil.rmtree(f'{os.getcwd()}{fake_directory}')

    def test_calculate_results_standard_deviation(self):
        test_question_set_results = [
            {
                'results': {
                    'correct': 1,
                    'incorrect': 2,
                    'unanswered': 3
                }
            },
            {
                'results': {
                    'correct': 2,
                    'incorrect': 3,
                    'unanswered': 1
                }
            }
        ]
        test_question_metrics = {
            'average_correct': 2,
            'average_incorrect': 2,
            'average_unanswered': 2,
            'article_count': 2
        }
        expected_output = {
            'correct_std_dev': round(sqrt(.5), DECIMAL_DIGITS),
            'incorrect_std_dev': round(sqrt(.5), DECIMAL_DIGITS),
            'unanswered_std_dev': 1.0
        }
        self.assertEqual(
            expected_output,
            calculate_results_standard_deviation(
                test_question_set_results,
                test_question_metrics
            ),
            'it should calculate the standard deviation of the results from different articles'
        )

    def test_calculate_disagreement(self):
        test_input = {
            'correct': 2,
            'incorrect': 3,
            'unanswered': 4,
            'article_count': 9
        }
        self.assertEqual(
            round(5 / 9, DECIMAL_DIGITS),
            calculate_disagreement(test_input),
            'it should return the sum of the minority answer states'
        )

    def test_calculate_individual_question_metrics(self):
        test_individual_metrics = {
            '1': {
                'correct': 1,
                'incorrect': 2,
                'unanswered': 3,
                'article_count': 6
            },
            '2': {
                'correct': 2,
                'incorrect': 3,
                'unanswered': 4,
                'article_count': 9
            }
        }
        expected_output = {
            '1': {
                'correct': 1,
                'incorrect': 2,
                'unanswered': 3,
                'article_count': 6,
                'percent_correct': round(1 / 6, DECIMAL_DIGITS),
                'percent_incorrect': round(2 / 6, DECIMAL_DIGITS),
                'percent_unanswered': .5,
                'disagreement': .5
            },
            '2': {
                'correct': 2,
                'incorrect': 3,
                'unanswered': 4,
                'article_count': 9,
                'percent_correct': round(2 / 9, DECIMAL_DIGITS),
                'percent_incorrect': round(3 / 9, DECIMAL_DIGITS),
                'percent_unanswered': round(4 / 9, DECIMAL_DIGITS),
                'disagreement': round(5 / 9, DECIMAL_DIGITS)
            }
        }
        self.assertEqual(
            expected_output,
            calculate_individual_question_metrics(test_individual_metrics),
            'it should add percent correct, incorrect, unanswerd, and disagreement to the raw performance'
        )
