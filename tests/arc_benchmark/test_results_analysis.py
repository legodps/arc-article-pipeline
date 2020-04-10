import json
import os
import shutil
from unittest import TestCase
from arc_benchmark.results_analysis import analyze_results


class TestResultsAnalysis(TestCase):
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
