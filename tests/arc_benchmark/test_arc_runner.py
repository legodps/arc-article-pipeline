import json
import os
import shutil
import subprocess
from unittest import TestCase
from unittest.mock import Mock, patch
from arc_benchmark.constants import ARC_DATA_SMALL_WIPE_KEEP_FILES, ARC_DATA_FULL_WIPE_KEEP_FILES
from arc_benchmark.arc_runner import clean_checkpoints, copy_test_set, run_arc_on_index, evaluate_articles

fake_directory = 'fake_directory_dont_use'
fake_response = 'unused text\n more unused text\n Metrics\n\n\n\nCorrect:1\nIncorrect:2\nUnanswered:3\n' \
                'Addendum Results:\n{"0": "correct", "1": "incorrect", "2": "incorrect", "3": "unanswered", ' \
                '"4": "unanswered", "5": "unanswered"}'
test_set_filename = 'fake-test-set.jsonl'


class TestArcRunner(TestCase):
    def test_clean_checkpoints_non_full(self):
        if os.path.isdir(f'{os.getcwd()}{fake_directory}'):
            self.assertTrue(False, f'directory of {fake_directory} is already in use, dont use it >:(')
        else:
            os.mkdir(f'{os.getcwd()}/{fake_directory}')
            for filename in ARC_DATA_SMALL_WIPE_KEEP_FILES:
                open(f'{os.getcwd()}/{fake_directory}/{filename}', 'a').close()
            open(f'{os.getcwd()}/{fake_directory}/empty_file.txt', 'a').close()
            clean_checkpoints(os.getcwd(), {'arc_data_subdirectory': fake_directory})
            self.assertEqual(
                sorted(os.listdir(f'{os.getcwd()}/{fake_directory}')),
                sorted(ARC_DATA_SMALL_WIPE_KEEP_FILES),
                'it should only wipe the file specified for small resets'
            )

            shutil.rmtree(f'{os.getcwd()}/{fake_directory}')

    def test_clean_checkpoints_full(self):
        if os.path.isdir(f'{os.getcwd()}{fake_directory}'):
            self.assertTrue(False, f'directory of {fake_directory} is already in use, dont use it >:(')
        else:
            os.mkdir(f'{os.getcwd()}/{fake_directory}')
            for filename in ARC_DATA_SMALL_WIPE_KEEP_FILES:
                open(f'{os.getcwd()}/{fake_directory}/{filename}', 'a').close()
            open(f'{os.getcwd()}/{fake_directory}/empty_file.txt', 'a').close()
            clean_checkpoints(os.getcwd(), {'arc_data_subdirectory': fake_directory}, full_reset=True)
            self.assertEqual(
                sorted(os.listdir(f'{os.getcwd()}/{fake_directory}')),
                sorted(ARC_DATA_FULL_WIPE_KEEP_FILES),
                'it should wipe all files specified for the full wipe'
            )

            shutil.rmtree(f'{os.getcwd()}/{fake_directory}')

    def test_copy_test_set(self):
        if os.path.isdir(f'{os.getcwd()}{fake_directory}'):
            self.assertTrue(False, f'directory of {fake_directory} is already in use, dont use it >:(')
        else:
            os.mkdir(f'{os.getcwd()}/{fake_directory}')
            open(f'{os.getcwd()}/{fake_directory}/{test_set_filename}', 'a').close()
            copy_test_set(
                os.getcwd(),
                f'{os.getcwd()}/{fake_directory}/{test_set_filename}',
                {'arc_data_subdirectory': fake_directory}
            )
            self.assertTrue(
                os.path.isfile(f'{os.getcwd()}/{fake_directory}/ARC-Challenge-Test.jsonl'),
                'it should move a file from one location to another'
            )

            shutil.rmtree(f'{os.getcwd()}/{fake_directory}')

    @patch('subprocess.run')
    def test_run_arc_on_index(self, mock_run):
        mock_run.return_value = Mock(stdout=fake_response)
        config = {
            'conda_environment_name': 'fake_environment',
            'arc_data_subdirectory': 'fake_subdirectory',
            'arc_model_subdirectory': 'fake_directory'
        }
        expected_individual_results = {
            '0': 'correct',
            '1': 'incorrect',
            '2': 'incorrect',
            '3': 'unanswered',
            '4': 'unanswered',
            '5': 'unanswered'
        }
        results, individual_results = run_arc_on_index('fake_index', config)
        self.assertEqual(
            {'correct': 1, 'incorrect': 2, 'unanswered': 3},
            results,
            'it should run the ARC solver program, get the results, and parse them'
        )
        self.assertEqual(expected_individual_results, individual_results)
        mock_run.assert_called_once_with(
            [
                'conda',
                'run',
                '-n',
                'fake_environment',
                'sh',
                'scripts/evaluate_solver.sh',
                'fake_subdirectory/ARC-Challenge-Test.jsonl',
                'fake_directory',
                'fake_index'
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

    @patch('subprocess.run')
    def test_evaluate_article(self, mock_run):
        fake_directory_2 = 'fake_directory_2'
        if os.path.isdir(f'{os.getcwd()}/{fake_directory}') or os.path.isdir(f'{os.getcwd()}/{fake_directory_2}'):
            self.assertTrue(
                False,
                f'directory of {fake_directory} and {fake_directory_2} is already in use, dont use it >:('
            )
        else:
            mock_run.return_value = Mock(stdout=fake_response)
            checkpoint_filename = 'checkpoint_file.jsonl'
            os.mkdir(f'{os.getcwd()}/{fake_directory}')
            os.mkdir(f'{os.getcwd()}/{fake_directory_2}')
            os.mkdir(f'{os.getcwd()}/{fake_directory_2}/fake_subdirectory')
            checkpoint_file = open(f'{os.getcwd()}/{fake_directory}/{checkpoint_filename}', 'a')
            checkpoint_json = {
                'index': 'index1',
                'question_set': '1',
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
                },
                'results': {
                    'correct': 2,
                    'incorrect': 3,
                    'unanswered': 4
                }
            }
            json.dump(checkpoint_json, checkpoint_file)
            checkpoint_file.close()
            open(f'{os.getcwd()}/{fake_directory}/{test_set_filename}', 'a').close()
            config = {
                'conda_environment_name': 'fake_environment',
                'arc_data_subdirectory': 'fake_subdirectory',
                'arc_model_subdirectory': 'fake_directory',
                'checkpoint_directory': fake_directory,
                'arc_checkpoint_file': checkpoint_filename
            }
            index_files = {'index1': 'index_file', 'index2': 'index_file'}
            question_set_indices = {'1': ['index1', 'index2']}
            benchmark_set_filepaths = {'1': f'/{fake_directory}/{test_set_filename}'}
            results = evaluate_articles(
                index_files,
                question_set_indices,
                benchmark_set_filepaths,
                f'{os.getcwd()}/{fake_directory_2}',
                config
            )
            expected_results = {
                'index_file': [
                    {
                        'index': 'index1',
                        'question_set': '1',
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
                        },
                        'results': {
                            'correct': 2,
                            'incorrect': 3,
                            'unanswered': 4
                        }
                    },
                    {
                        'question_set': '1',
                        'individual_results': {
                            '0': 'correct',
                            '1': 'incorrect',
                            '2': 'incorrect',
                            '3': 'unanswered',
                            '4': 'unanswered',
                            '5': 'unanswered'
                        },
                        'results': {
                            'correct': 1,
                            'incorrect': 2,
                            'unanswered': 3
                        }
                    }
                ]
            }
            self.assertEqual(
                expected_results,
                results,
                'it should load results for previously run indices and run the solver on the others'
            )
            shutil.rmtree(f'{os.getcwd()}/{fake_directory}')
            shutil.rmtree(f'{os.getcwd()}/{fake_directory_2}')
