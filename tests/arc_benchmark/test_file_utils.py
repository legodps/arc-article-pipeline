import json
import os
import shutil
from unittest import TestCase
from arc_benchmark.file_utils import process_article_line, process_article, read_jsonl_articles, retrieve_questions, \
    read_json_questions, create_or_load_arc_checkpoint, load_json, store_json

fake_directory = '/fake_directory_dont_use'


class TestLoadFiles(TestCase):
    def test_process_article_line(self):
        test_line = '{"squid": "lol:asdf", "title": "boop", "paragraphs": [{"para_body": [{"text": "fake"},' \
                    '{"not": "used", "text": " line"}] }] }'
        self.assertEqual(
            {'title': 'bongo_cat-boop', 'text': 'fake line', 'id': 'asdf', 'file': 'bongo_cat'},
            process_article_line(test_line, 'bongo_cat'),
            'It should extract the text entries from the JSON formatted data'
        )

    def test_process_article(self):
        expected_articles = [
            {
                'title': 'test_articles_1-test-title',
                'text': 'this is a test of the software that I made for processing articles',
                'id': 'efgh',
                'file': 'test_articles_1'
            },
            {
                'title': 'test_articles_1-full-metal-coding',
                'text': 'There are many code bases like this but this one is mine',
                'id': 'mnop',
                'file': 'test_articles_1'
            }
        ]
        test_file = 'tests/data-files/articles/test_articles_1'
        self.assertEqual(
            expected_articles,
            process_article(test_file),
            'It should extract articles from a given JSONL file without a .jsonl extension'
        )
        self.assertEqual(
            expected_articles,
            process_article(f'{test_file}.jsonl'),
            'It should extract articles from a given JSONL file with the .jsonl extension specified'
        )

    def test_read_jsonl_articles(self):
        expected_articles_partial = [
            {
                'title': 'test_articles_2-pluto-remorse',
                'text': 'Poor Pluto, once a planet now relegated to a lesser status',
                'id': 'uvwx',
                'file': 'test_articles_2'
            },
            {
                'title': 'test_articles_2-meditation',
                'text': 'Ask not for whom the bell tolls, it tolls for thee',
                'id': 'cdef',
                'file': 'test_articles_2'
            }
        ]
        expected_articles_full = [
            {
                'title': 'test_articles_1-test-title',
                'text': 'this is a test of the software that I made for processing articles',
                'id': 'efgh',
                'file': 'test_articles_1'
            },
            {
                'title': 'test_articles_1-full-metal-coding',
                'text': 'There are many code bases like this but this one is mine',
                'id': 'mnop',
                'file': 'test_articles_1'
            },
            {
                'title': 'test_articles_2-pluto-remorse',
                'text': 'Poor Pluto, once a planet now relegated to a lesser status',
                'id': 'uvwx',
                'file': 'test_articles_2'
            },
            {
                'title': 'test_articles_2-meditation',
                'text': 'Ask not for whom the bell tolls, it tolls for thee',
                'id': 'cdef',
                'file': 'test_articles_2'
            }
        ]
        self.assertEqual(
            expected_articles_partial,
            read_jsonl_articles('tests/data-files/articles/test_articles_2.jsonl'),
            'It should load in a singular file given a singular file filepath'
        )
        self.assertEqual(
            expected_articles_full,
            read_jsonl_articles('tests/data-files/articles'),
            'It should load in a directory of files given a directory filepath'
        )

    def test_retrieve_questions(self):
        expected_questions = {
            'abcd': [
                {
                    'id': '0',
                    'question': {
                        'stem': 'this is the first question being asked',
                        'choices': [
                            {
                                'text': 'this is the first answer',
                                'label': 'a'
                            },
                            {
                                'text': 'this is the second answer',
                                'label': 'b'
                            }
                        ]
                    },
                    'answerKey': 'a'
                },
                {
                    'id': '1',
                    'question': {
                        'stem': 'this is the second question being asked',
                        'choices': [
                            {
                                'text': 'answer one',
                                'label': 'a'
                            },
                            {
                                'text': 'answer two',
                                'label': 'b'
                            },
                            {
                                'text': 'answer three',
                                'label': 'c'
                            }
                        ]
                    },
                    'answerKey': 'b'
                }
            ],
            'efgh': [{
                'id': '0',
                'question': {
                    'stem': 'this is the third question being asked',
                    'choices': [
                        {
                            'text': 'The first answer is correct',
                            'label': 'a'
                        },
                        {
                            'text': 'The second answer is correct',
                            'label': 'b'
                        },
                        {
                            'text': 'The third answer is correct',
                            'label': 'c'
                        },
                        {
                            'text': 'The fourth answer is correct',
                            'label': 'd'
                        }
                    ]
                },
                'answerKey': 'c'
            }]
        }
        filename = 'tests/data-files/questions/test_questions_1'
        self.assertEqual(
            expected_questions,
            retrieve_questions(filename),
            'it should load in the question file without a specified file extension'
        )
        self.assertEqual(
            expected_questions,
            retrieve_questions(f'{filename}.json'),
            'it should load in the question file with a specified file extension'
        )

    def test_read_json_questions_single_file(self):
        expected_single_file = {
            'ijkl': [
                {
                    'id': '0',
                    'question': {
                        'stem': 'this is the fourth question',
                        'choices': [{
                            'text': 'this is the only answer',
                            'label': 'a'
                        }]
                    },
                    'answerKey': 'a'
                }
            ],
            'mnop': [
                {
                    'id': '0',
                    'question': {
                        'stem': 'this is fifth question',
                        'choices': [
                            {
                                'text': 'option 1',
                                'label': '1'
                            },
                            {
                                'text': 'option 2',
                                'label': '2'
                            }
                        ]
                    },
                    'answerKey': '2'
                },
                {
                    'id': '1',
                    'question': {
                        'stem': 'question six',
                        'choices': [
                            {
                                'text': '1 of 5',
                                'label': 'a'
                            },
                            {
                                'text': '2 of 5',
                                'label': 'b'
                            },
                            {
                                'text': '3 of 5',
                                'label': 'c'
                            },
                            {
                                'text': '4 of 5',
                                'label': 'd'
                            },
                            {
                                'text': '5 of 5',
                                'label': 'e'
                            }
                        ]
                    },
                    'answerKey': 'e'
                }
            ]
        }

        self.assertEqual(
            expected_single_file,
            read_json_questions('tests/data-files/questions/test_questions_2.json'),
            'it should load in a single specified and all questions within it'
        )

    def test_read_json_questions_multiple_files(self):
        expected_single_file = {
            'abcd': [
                {
                    'id': '0',
                    'question': {
                        'stem': 'this is the first question being asked',
                        'choices': [
                            {
                                'text': 'this is the first answer',
                                'label': 'a'
                            },
                            {
                                'text': 'this is the second answer',
                                'label': 'b'
                            }
                        ]
                    },
                    'answerKey': 'a'
                },
                {
                    'id': '1',
                    'question': {
                        'stem': 'this is the second question being asked',
                        'choices': [
                            {
                                'text': 'answer one',
                                'label': 'a'
                            },
                            {
                                'text': 'answer two',
                                'label': 'b'
                            },
                            {
                                'text': 'answer three',
                                'label': 'c'
                            }
                        ]
                    },
                    'answerKey': 'b'
                }
            ],
            'efgh': [{
                'id': '0',
                'question': {
                    'stem': 'this is the third question being asked',
                    'choices': [
                        {
                            'text': 'The first answer is correct',
                            'label': 'a'
                        },
                        {
                            'text': 'The second answer is correct',
                            'label': 'b'
                        },
                        {
                            'text': 'The third answer is correct',
                            'label': 'c'
                        },
                        {
                            'text': 'The fourth answer is correct',
                            'label': 'd'
                        }
                    ]
                },
                'answerKey': 'c'
            }],
            'ijkl': [
                {
                    'id': '0',
                    'question': {
                        'stem': 'this is the fourth question',
                        'choices': [{
                            'text': 'this is the only answer',
                            'label': 'a'
                        }]
                    },
                    'answerKey': 'a'
                }
            ],
            'mnop': [
                {
                    'id': '0',
                    'question': {
                        'stem': 'this is fifth question',
                        'choices': [
                            {
                                'text': 'option 1',
                                'label': '1'
                            },
                            {
                                'text': 'option 2',
                                'label': '2'
                            }
                        ]
                    },
                    'answerKey': '2'
                },
                {
                    'id': '1',
                    'question': {
                        'stem': 'question six',
                        'choices': [
                            {
                                'text': '1 of 5',
                                'label': 'a'
                            },
                            {
                                'text': '2 of 5',
                                'label': 'b'
                            },
                            {
                                'text': '3 of 5',
                                'label': 'c'
                            },
                            {
                                'text': '4 of 5',
                                'label': 'd'
                            },
                            {
                                'text': '5 of 5',
                                'label': 'e'
                            }
                        ]
                    },
                    'answerKey': 'e'
                }
            ]
        }

        self.assertEqual(
            expected_single_file,
            read_json_questions('tests/data-files/questions'),
            'it should load in all questions from a directory of question files'
        )

    def test_create_or_load_arc_checkpoint_no_checkpoint(self):
        if os.path.isdir(f'{os.getcwd()}/{fake_directory}'):
            self.assertTrue(False, f'directory of {fake_directory} is already in use, dont use it >:(')
        else:
            checkpoint_filename = 'fake_checkpoint.jsonl'
            checkpoint_file, completed_entries = create_or_load_arc_checkpoint({
                'checkpoint_directory': f'{os.getcwd()}{fake_directory}',
                'arc_checkpoint_file': checkpoint_filename
            })
            self.assertTrue(
                os.path.isdir(f'{os.getcwd()}{fake_directory}'),
                'It should create a directory and a blank checkpoint file'
            )
            self.assertEqual({}, completed_entries)
            self.assertTrue(isinstance(checkpoint_file, object))
            checkpoint_file.close()

            shutil.rmtree(f'{os.getcwd()}/{fake_directory}')

    def test_create_or_load_arc_checkpoint_extant_checkpoint(self):
        if os.path.isdir(f'{os.getcwd()}{fake_directory}'):
            self.assertTrue(False, f'directory of {fake_directory} is already in use, dont use it >:(')
        else:
            checkpoint_filename = 'fake_checkpoint.jsonl'
            os.mkdir(f'{os.getcwd()}{fake_directory}')
            file = open(f'{os.getcwd()}/{fake_directory}/{checkpoint_filename}', 'w')
            file.write(json.dumps({'index': 'fake_index', 'one': 'two'}))
            file.close()

            checkpoint_file, completed_entries = create_or_load_arc_checkpoint({
                'checkpoint_directory': f'{os.getcwd()}{fake_directory}',
                'arc_checkpoint_file': checkpoint_filename
            })
            self.assertTrue(
                os.path.isdir(f'{os.getcwd()}{fake_directory}'),
                'It should load an existing checkpoint file'
            )
            self.assertEqual({'fake_index': {'index': 'fake_index', 'one': 'two'}}, completed_entries)
            self.assertTrue(isinstance(checkpoint_file, object))
            checkpoint_file.close()

            shutil.rmtree(f'{os.getcwd()}/{fake_directory}')

    def test_load_json_no_results(self):
        if os.path.isdir(f'{os.getcwd()}{fake_directory}'):
            self.assertTrue(False, f'directory of {fake_directory} is already in use, dont use it >:(')
        else:
            self.assertEqual(
                None,
                load_json('fake_results.json', {'checkpoint_directory': fake_directory}),
                'It should return None if the checkpoint directory does not exist'
            )

            os.mkdir(f'{os.getcwd()}{fake_directory}')
            self.assertEqual(
                None,
                load_json('fake_results.json', {'checkpoint_directory': fake_directory}),
                'It should return None if the checkpoint directory exists but the json file does not'
            )
            os.rmdir(f'{os.getcwd()}{fake_directory}')

    def test_load_json_results(self):
        if os.path.isdir(f'{os.getcwd()}{fake_directory}'):
            self.assertTrue(False, f'directory of {fake_directory} is already in use, dont use it >:(')
        else:
            results_filename = 'fake_results.json'
            os.mkdir(f'{os.getcwd()}{fake_directory}')
            file = open(f'{os.getcwd()}{fake_directory}/{results_filename}', 'w')
            file.write(json.dumps({'one': 'two'}))
            file.close()

            results = load_json(results_filename, {'checkpoint_directory': f'{os.getcwd()}{fake_directory}'})
            self.assertEqual({'one': 'two'}, results, 'It should load the json results from the checkpoint directory')

            shutil.rmtree(f'{os.getcwd()}/{fake_directory}')

    def test_store_json_results(self):
        if os.path.isdir(f'{os.getcwd()}{fake_directory}'):
            self.assertTrue(False, f'directory of {fake_directory} is already in use, dont use it >:(')
        else:
            results_filename = 'fake_results.json'
            results_object = {'fake': 'results'}
            os.mkdir(f'{os.getcwd()}{fake_directory}')
            store_json(results_object, results_filename, {'checkpoint_directory': f'{os.getcwd()}{fake_directory}'})
            json_file = open(f'{os.getcwd()}{fake_directory}/{results_filename}', 'r')
            saved_json = json.load(json_file)
            json_file.close()
            self.assertEqual(
                results_object,
                saved_json,
                'it should save json to a specified file as given to it'
            )

            shutil.rmtree(f'{os.getcwd()}/{fake_directory}')