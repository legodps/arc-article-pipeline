import os
import json
import shutil
from unittest import TestCase
from arc_benchmark.benchmark_set_creator import create_or_clean_directory, store_question_sets, create_test_sets


fake_directory = 'fake_directory_dont_use'
config = {'benchmark_set_directory': fake_directory}
question_sets = {
    '1': [
        {
            'id': '0',
            'question': {
                'stem': 'Question 1',
                'choices': [
                    {
                        'text': 'answer a',
                        'label': 'a'
                    },
                    {
                        'text': 'answer b',
                        'label': 'b'
                    }
                ]
            },
            'answerKey': 'a'
        },
        {
            'id': '1',
            'question': {
                'stem': 'Question 2',
                'choices': [
                    {
                        'text': 'answer one',
                        'label': '1'
                    },
                    {
                        'text': 'answer two',
                        'label': '2'
                    },
                    {
                        'text': 'answer three',
                        'label': '3'
                    }
                ]
            },
            'answerKey': '2'
        }
    ],
    '2': [{
        'id': '0',
        'question': {
            'stem': 'Question 3',
            'choices': [
                {
                    'text': 'true',
                    'label': 'a'
                },
                {
                    'text': 'false',
                    'label': 'b'
                }
            ]
        },
        'answerKey': 'c'
    }],
    '3': [{
        'id': '0',
        'question': {
            'stem': 'Question 4',
            'choices': [
                {
                    'text': 'only option',
                    'label': 'alpha'
                }
            ]
        },
        'answerKey': 'alpha'
    }]
}
question_set_imported = [
    [
        {
            'id': '0',
            'question': {
                'stem': 'Question 1',
                'choices': [
                    {
                        'text': 'answer a',
                        'label': 'a'
                    },
                    {
                        'text': 'answer b',
                        'label': 'b'
                    }
                ]
            },
            'answerKey': 'a'
        },
        {
            'id': '1',
            'question': {
                'stem': 'Question 2',
                'choices': [
                    {
                        'text': 'answer one',
                        'label': '1'
                    },
                    {
                        'text': 'answer two',
                        'label': '2'
                    },
                    {
                        'text': 'answer three',
                        'label': '3'
                    }
                ]
            },
            'answerKey': '2'
        }
    ],
    [{
        'id': '0',
        'question': {
            'stem': 'Question 4',
            'choices': [
                {
                    'text': 'only option',
                    'label': 'alpha'
                }
            ]
        },
        'answerKey': 'alpha'
    }]
]


class TestQuestionSetCreator(TestCase):
    def test_create_or_clean_directory(self):
        if os.path.isdir(fake_directory):
            self.assertTrue(False, f'directory of {fake_directory} is already in use, dont use it >:(')
        else:
            create_or_clean_directory(config)
            self.assertTrue(os.path.isdir(fake_directory), 'it should create a directory')

            open(f'{fake_directory}/empty_file.txt', 'a').close()
            create_or_clean_directory(config)
            self.assertFalse(
                os.path.isfile(f'{fake_directory}/empty_file.txt'),
                'it should clean out any files in the configured test set directory'
            )
            self.assertTrue(os.path.isdir(fake_directory))
            os.rmdir(fake_directory)
            self.assertFalse(os.path.isdir(fake_directory))

    def test_store_question_sets(self):
        if os.path.isdir(fake_directory):
            self.assertTrue(False, f'directory of {fake_directory} is already in use, dont use it >:(')
        else:
            create_or_clean_directory(config)

            store_question_sets(question_sets, ['1', '3'], config)
            filenames = [f'{fake_directory}/1-ARC-Challenge-Test.jsonl', f'{fake_directory}/3-ARC-Challenge-Test.jsonl']
            questions = []
            for file_index in range(len(filenames)):
                question_file_questions = []
                with open(filenames[file_index]) as question_file:
                    question_line = question_file.readline()
                    while question_line:
                        question_file_questions.append(json.loads(question_line))
                        question_line = question_file.readline()
                questions.append(question_file_questions)

            self.assertEqual(
                question_set_imported,
                questions,
                'it should store the questions as expected into jsonl files'
            )
            shutil.rmtree(fake_directory)

    def test_create_test_sets(self):
        if os.path.isdir(fake_directory):
            self.assertTrue(False, f'directory of {fake_directory} is already in use, dont use it >:(')
        else:
            create_or_clean_directory(config)
            open(f'{fake_directory}/empty_file.txt', 'a').close()
            create_test_sets('tests/data-files/questions', ['abcd', 'ijkl'], config)

            self.assertTrue(
                os.path.isdir(fake_directory),
                'it should create the directory to store the test sets'
            )
            self.assertTrue(
                os.path.isfile(f'{fake_directory}/abcd-ARC-Challenge-Test.jsonl'),
                'it should store 2 separate files of test sets'
            )
            self.assertTrue(
                os.path.isfile(f'{fake_directory}/ijkl-ARC-Challenge-Test.jsonl'),
                'it should store 2 separate files of test sets'
            )
            self.assertFalse(
                os.path.isfile(f'{fake_directory}/empty_file.txt'),
                'it should have deleted the old file during the directory clean and re-creation'
            )
            shutil.rmtree(fake_directory)
