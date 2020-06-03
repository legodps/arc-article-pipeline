import json
import os
import shutil
from unittest import TestCase
from math import sqrt
from arc_benchmark.constants import DECIMAL_DIGITS
from arc_benchmark.results_analysis import analyze_questions, analyze_results, calculate_baselines, \
    calculate_results_standard_deviation, calculate_disagreement, calculate_individual_question_metrics, \
    calculate_question_set_metrics


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
            test_question_counts = {
                '2': 5,
                '4': 5
            }
            analyze_results(benchmark_results, test_question_counts, config)
            expected_results = {
                'random_answering': {'correct': 4, 'incorrect': 6, 'unanswered': 0},
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

    def test_calculate_question_set_metrics(self):
        test_question_set_input = {
            '1': [{
                    'results': {
                        'correct': 1,
                        'incorrect': 2,
                        'unanswered': 3
                    }
            }, {
                    'results': {
                        'correct': 2,
                        'incorrect': 3,
                        'unanswered': 1
                    }
            }],
            '2': [{
                'results': {
                    'correct': 2,
                    'incorrect': 3,
                    'unanswered': 4
                }
            }, {
                'results': {
                    'correct': 4,
                    'incorrect': 3,
                    'unanswered': 2
                }
            }]
        }
        expected_output = {
            '1': {
                'article_count': 2,
                'question_count': 6,
                'total_correct': 3,
                'total_incorrect': 5,
                'total_unanswered': 4,
                'average_correct': 1.5,
                'average_incorrect': 2.5,
                'average_unanswered': 2.0,
                'average_percent_correct': .25,
                'average_percent_incorrect': round((2.5/6), DECIMAL_DIGITS),
                'average_percent_unanswered': round((2/6), DECIMAL_DIGITS),
                'correct_std_dev': 0.5,
                'incorrect_std_dev': 0.5,
                'unanswered_std_dev': 1.0
            },
            '2': {
                'article_count': 2,
                'question_count': 9,
                'total_correct': 6,
                'total_incorrect': 6,
                'total_unanswered': 6,
                'average_correct': 3.0,
                'average_incorrect': 3.0,
                'average_unanswered': 3.0,
                'average_percent_correct': round((1/3), DECIMAL_DIGITS),
                'average_percent_incorrect': round((1/3), DECIMAL_DIGITS),
                'average_percent_unanswered': round((1/3), DECIMAL_DIGITS),
                'correct_std_dev': 1.0,
                'incorrect_std_dev': 0.0,
                'unanswered_std_dev': 1.0
            }
        }
        self.assertEqual(
            expected_output,
            calculate_question_set_metrics(test_question_set_input),
            'It should calculate a suite of statistics about a raw set of results'
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

    def test_analyze_questions(self):
        fake_directory = '/fake_directory_dont_use'
        if os.path.isdir(f'{os.getcwd()}{fake_directory}'):
            self.assertTrue(False, f'directory of {fake_directory} is already in use, dont use it >:(')
        else:
            os.mkdir(f'{os.getcwd()}{fake_directory}')
            set_results_filename = 'set_results_file.json'
            individual_results_filename = 'individual_results_file.json'
            config = {
                'checkpoint_directory': f'{os.getcwd()}{fake_directory}',
                'question_set_metrics_file': set_results_filename,
                'individual_question_metrics_file': individual_results_filename
            }
            test_benchmark_results = {
                'file1': [{
                    'question_set': '1',
                    'results': {
                        'correct': 1,
                        'incorrect': 2,
                        'unanswered': 3
                    },
                    'individual_results': {
                        '0': 'correct',
                        '1': 'incorrect',
                        '2': 'incorrect',
                        '3': 'unanswered',
                        '4': 'unanswered',
                        '5': 'unanswered'
                    }
                }, {
                    'question_set': '2',
                    'results': {
                        'correct': 2,
                        'incorrect': 3,
                        'unanswered': 4
                    },
                    'individual_results': {
                        '0': 'correct',
                        '1': 'correct',
                        '2': 'incorrect',
                        '3': 'incorrect',
                        '4': 'incorrect',
                        '5': 'unanswered',
                        '6': 'unanswered',
                        '7': 'unanswered',
                        '8': 'unanswered'
                    }
                }],
                'file2': [{
                    'question_set': '1',
                    'results': {
                        'correct': 2,
                        'incorrect': 3,
                        'unanswered': 1
                    },
                    'individual_results': {
                        '0': 'correct',
                        '1': 'correct',
                        '2': 'incorrect',
                        '3': 'incorrect',
                        '4': 'incorrect',
                        '5': 'unanswered'
                    }
                }, {
                    'question_set': '2',
                    'results': {
                        'correct': 4,
                        'incorrect': 3,
                        'unanswered': 2
                    },
                    'individual_results': {
                        '0': 'correct',
                        '1': 'correct',
                        '2': 'correct',
                        '3': 'correct',
                        '4': 'incorrect',
                        '5': 'incorrect',
                        '6': 'incorrect',
                        '7': 'unanswered',
                        '8': 'unanswered'
                    }
                }]
            }
            expected_set_metrics = {
                '1': {
                    'article_count': 2,
                    'question_count': 6,
                    'total_correct': 3,
                    'total_incorrect': 5,
                    'total_unanswered': 4,
                    'average_correct': 1.5,
                    'average_incorrect': 2.5,
                    'average_unanswered': 2.0,
                    'average_percent_correct': .25,
                    'average_percent_incorrect': round((2.5 / 6), DECIMAL_DIGITS),
                    'average_percent_unanswered': round((2 / 6), DECIMAL_DIGITS),
                    'correct_std_dev': 0.5,
                    'incorrect_std_dev': 0.5,
                    'unanswered_std_dev': 1.0
                },
                '2': {
                    'article_count': 2,
                    'question_count': 9,
                    'total_correct': 6,
                    'total_incorrect': 6,
                    'total_unanswered': 6,
                    'average_correct': 3.0,
                    'average_incorrect': 3.0,
                    'average_unanswered': 3.0,
                    'average_percent_correct': round((1 / 3), DECIMAL_DIGITS),
                    'average_percent_incorrect': round((1 / 3), DECIMAL_DIGITS),
                    'average_percent_unanswered': round((1 / 3), DECIMAL_DIGITS),
                    'correct_std_dev': 1.0,
                    'incorrect_std_dev': 0.0,
                    'unanswered_std_dev': 1.0
                }
            }
            expected_individual_metrics = {
                '1:0': {
                    'question_set': '1',
                    'question_id': '0',
                    'correct': 2,
                    'incorrect': 0,
                    'unanswered': 0,
                    'article_count': 2,
                    'percent_correct': 1.0,
                    'percent_incorrect': 0.0,
                    'percent_unanswered': 0.0,
                    'disagreement': 0.0,
                },
                '1:1': {
                    'question_set': '1',
                    'question_id': '1',
                    'correct': 1,
                    'incorrect': 1,
                    'unanswered': 0,
                    'article_count': 2,
                    'percent_correct': .5,
                    'percent_incorrect': .5,
                    'percent_unanswered': 0.0,
                    'disagreement': .5
                },
                '1:2': {
                    'question_set': '1',
                    'question_id': '2',
                    'correct': 0,
                    'incorrect': 2,
                    'unanswered': 0,
                    'article_count': 2,
                    'percent_correct': 0.0,
                    'percent_incorrect': 1.0,
                    'percent_unanswered': 0.0,
                    'disagreement': 0.0
                },
                '1:3': {
                    'question_set': '1',
                    'question_id': '3',
                    'correct': 0,
                    'incorrect': 1,
                    'unanswered': 1,
                    'article_count': 2,
                    'percent_correct': 0.0,
                    'percent_incorrect': .5,
                    'percent_unanswered': .5,
                    'disagreement': .5
                },
                '1:4': {
                    'question_set': '1',
                    'question_id': '4',
                    'correct': 0,
                    'incorrect': 1,
                    'unanswered': 1,
                    'article_count': 2,
                    'percent_correct': 0.0,
                    'percent_incorrect': .5,
                    'percent_unanswered': .5,
                    'disagreement': .5
                },
                '1:5': {
                    'question_set': '1',
                    'question_id': '5',
                    'correct': 0,
                    'incorrect': 0,
                    'unanswered': 2,
                    'article_count': 2,
                    'percent_correct': 0.0,
                    'percent_incorrect': 0.0,
                    'percent_unanswered': 1.0,
                    'disagreement': 0.0
                },
                '2:0': {
                    'question_set': '2',
                    'question_id': '0',
                    'correct': 2,
                    'incorrect': 0,
                    'unanswered': 0,
                    'article_count': 2,
                    'percent_correct': 1.0,
                    'percent_incorrect': 0.0,
                    'percent_unanswered': 0.0,
                    'disagreement': 0.0
                },
                '2:1': {
                    'question_set': '2',
                    'question_id': '1',
                    'correct': 2,
                    'incorrect': 0,
                    'unanswered': 0,
                    'article_count': 2,
                    'percent_correct': 1.0,
                    'percent_incorrect': 0.0,
                    'percent_unanswered': 0.0,
                    'disagreement': 0.0
                },
                '2:2': {
                    'question_set': '2',
                    'question_id': '2',
                    'correct': 1,
                    'incorrect': 1,
                    'unanswered': 0,
                    'article_count': 2,
                    'percent_correct': .5,
                    'percent_incorrect': .5,
                    'percent_unanswered': 0.0,
                    'disagreement': .5
                },
                '2:3': {
                    'question_set': '2',
                    'question_id': '3',
                    'correct': 1,
                    'incorrect': 1,
                    'unanswered': 0,
                    'article_count': 2,
                    'percent_correct': .5,
                    'percent_incorrect': .5,
                    'percent_unanswered': 0.0,
                    'disagreement': .5
                },
                '2:4': {
                    'question_set': '2',
                    'question_id': '4',
                    'correct': 0,
                    'incorrect': 2,
                    'unanswered': 0,
                    'article_count': 2,
                    'percent_correct': 0.0,
                    'percent_incorrect': 1.0,
                    'percent_unanswered': 0.0,
                    'disagreement': 0.0
                },
                '2:5': {
                    'question_set': '2',
                    'question_id': '5',
                    'correct': 0,
                    'incorrect': 1,
                    'unanswered': 1,
                    'article_count': 2,
                    'percent_correct': 0.0,
                    'percent_incorrect': .5,
                    'percent_unanswered': .5,
                    'disagreement': .5
                },
                '2:6': {
                    'question_set': '2',
                    'question_id': '6',
                    'correct': 0,
                    'incorrect': 1,
                    'unanswered': 1,
                    'article_count': 2,
                    'percent_correct': 0.0,
                    'percent_incorrect': .5,
                    'percent_unanswered': .5,
                    'disagreement': .5
                },
                '2:7': {
                    'question_set': '2',
                    'question_id': '7',
                    'correct': 0,
                    'incorrect': 0,
                    'unanswered': 2,
                    'article_count': 2,
                    'percent_correct': 0.0,
                    'percent_incorrect': 0.0,
                    'percent_unanswered': 1.0,
                    'disagreement': 0.0
                },
                '2:8': {
                    'question_set': '2',
                    'question_id': '8',
                    'correct': 0,
                    'incorrect': 0,
                    'unanswered': 2,
                    'article_count': 2,
                    'percent_correct': 0.0,
                    'percent_incorrect': 0.0,
                    'percent_unanswered': 1.0,
                    'disagreement': 0.0
                }
            }
            analyze_questions(test_benchmark_results, config)
            set_results_file = open(f'{os.getcwd()}{fake_directory}/{set_results_filename}', 'r')
            set_results = json.load(set_results_file)
            set_results_file.close()
            individual_results_file = open(f'{os.getcwd()}{fake_directory}/{individual_results_filename}', 'r')
            individual_results = json.load(individual_results_file)
            individual_results_file.close()
            self.assertEqual(
                expected_set_metrics,
                set_results,
                'it should calculate a variety of performance metrics about a set of questions and store them in json'
            )
            self.assertEqual(
                expected_individual_metrics,
                individual_results,
                'it should calculate a variety of performance metrics about individual questions and store them in json'
            )
            shutil.rmtree(f'{os.getcwd()}{fake_directory}')
