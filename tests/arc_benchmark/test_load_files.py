from unittest import TestCase
from arc_benchmark.load_files import process_article_line, process_article, read_jsonl_articles, retrieve_questions, \
    read_json_questions


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
